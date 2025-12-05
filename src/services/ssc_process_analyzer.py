"""
SSC Process Analyzer
Analyzes SSC meetings against formal processes and learns from observed practices
"""
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func

from src.config.extensions import db
from src.models.ssc import SSCMeeting, SSCRecommendation, SSCDocument
from src.models.ssc_process import (
    SSCProcessStep, SSCObservedPractice, SSCMeetingCompliance, SSCProcessDocument
)
from src.services.ai_service import AIService

logger = logging.getLogger(__name__)


class SSCProcessAnalyzer:
    """
    Analyzes SSC meetings for process compliance and learns from patterns
    """

    def __init__(self):
        self.ai_service = AIService()

    def analyze_meeting_compliance(self, meeting_id: str) -> Dict:
        """
        Analyze a single meeting for process compliance
        Returns compliance data and insights
        """
        try:
            meeting = SSCMeeting.query.get(meeting_id)
            if not meeting:
                raise ValueError(f"Meeting not found: {meeting_id}")

            # Determine process type from meeting
            process_type = self._determine_process_type(meeting)

            # Get formal process steps
            formal_steps = SSCProcessStep.query.filter_by(
                process_type=process_type
            ).order_by(SSCProcessStep.step_number).all()

            # Analyze meeting documents for completed steps
            completed_steps, skipped_steps, added_steps = self._analyze_meeting_steps(
                meeting, formal_steps
            )

            # Calculate timeline compliance
            timeline_data = self._analyze_timeline_compliance(meeting, formal_steps)

            # Calculate compliance scores
            compliance_score = len(completed_steps) / len(formal_steps) if formal_steps else 0
            timeline_score = self._calculate_timeline_score(timeline_data)
            overall_score = (compliance_score * 0.6) + (timeline_score * 0.4)

            # Generate flags
            flags = self._generate_compliance_flags(
                completed_steps, skipped_steps, timeline_data
            )

            # Get AI insights
            ai_insights = self._generate_ai_insights(
                meeting, formal_steps, completed_steps, skipped_steps, timeline_data
            )

            # Create or update compliance record
            compliance = SSCMeetingCompliance.query.filter_by(
                meeting_id=meeting.id,
                process_type=process_type
            ).first()

            if not compliance:
                compliance = SSCMeetingCompliance(
                    meeting_id=meeting.id,
                    process_type=process_type
                )

            compliance.steps_completed = [str(s.id) for s in completed_steps]
            compliance.steps_skipped = [str(s.id) for s in skipped_steps]
            compliance.steps_added = added_steps
            compliance.expected_duration_days = timeline_data.get('expected_days')
            compliance.actual_duration_days = timeline_data.get('actual_days')
            compliance.timeline_variance_days = timeline_data.get('variance_days')
            compliance.compliance_score = compliance_score
            compliance.timeline_score = timeline_score
            compliance.overall_score = overall_score
            compliance.has_deviations = len(skipped_steps) > 0 or len(flags) > 0
            compliance.compliance_flags = flags
            compliance.ai_insights = ai_insights

            db.session.add(compliance)
            db.session.commit()

            # Update observed practices (adaptive learning)
            self._update_observed_practices(meeting, process_type, completed_steps, timeline_data)

            return {
                'meeting_id': str(meeting.id),
                'process_type': process_type,
                'compliance_score': compliance_score,
                'timeline_score': timeline_score,
                'overall_score': overall_score,
                'steps_completed': len(completed_steps),
                'steps_total': len(formal_steps),
                'flags': flags,
                'ai_insights': ai_insights
            }

        except Exception as e:
            logger.error(f"Error analyzing meeting compliance: {e}")
            raise

    def _determine_process_type(self, meeting: SSCMeeting) -> str:
        """Determine the process type from meeting details"""
        title_lower = meeting.title.lower()
        meeting_type = (meeting.meeting_type or '').lower()

        if 'abc' in title_lower or 'acceptable biological catch' in title_lower:
            return 'ABC Review'
        elif 'assessment' in title_lower or 'sedar' in title_lower:
            return 'Stock Assessment Review'
        elif 'research' in title_lower or 'priority' in title_lower:
            return 'Research Priorities'
        elif 'sep' in meeting_type or 'economic' in title_lower:
            return 'Economic/Social Review'
        else:
            return 'General SSC Meeting'

    def _analyze_meeting_steps(self, meeting: SSCMeeting, formal_steps: List[SSCProcessStep]) -> tuple:
        """
        Analyze meeting documents to determine which formal steps were completed
        Returns: (completed_steps, skipped_steps, added_steps)
        """
        completed = []
        skipped = []
        added = []

        # Download and analyze meeting documents
        documents = SSCDocument.query.filter_by(meeting_id=meeting.id).all()

        # Extract text from all documents
        all_text = ""
        for doc in documents:
            # This would extract actual text from PDFs in production
            all_text += f"{doc.title} {doc.document_type} "

        # Add agenda and report URLs text
        if meeting.agenda_url:
            all_text += " agenda "
        if meeting.report_url:
            all_text += " final report summary "
        if meeting.briefing_book_url:
            all_text += " briefing book materials "

        # Check each formal step
        for step in formal_steps:
            if self._step_completed(step, all_text, meeting):
                completed.append(step)
            elif step.is_required:
                skipped.append(step)

        # Look for additional practices not in formal process
        additional_practices = self._identify_additional_practices(all_text, formal_steps)
        added.extend(additional_practices)

        return completed, skipped, added

    def _step_completed(self, step: SSCProcessStep, text: str, meeting: SSCMeeting) -> bool:
        """
        Determine if a process step was completed based on meeting documents
        """
        text_lower = text.lower()
        step_name_lower = step.step_name.lower()

        # Check for keywords related to the step
        keywords = step_name_lower.split()

        # Check if deliverables are present
        if step.required_deliverables:
            for deliverable in step.required_deliverables:
                if deliverable.lower() in text_lower:
                    return True

        # Check for step name mentions
        if step_name_lower in text_lower:
            return True

        # Check for related terms
        step_indicators = {
            'review': ['reviewed', 'review', 'assessment'],
            'recommendation': ['recommended', 'recommendation', 'motion'],
            'presentation': ['presented', 'presentation', 'briefing'],
            'discussion': ['discussed', 'discussion', 'deliberation'],
            'vote': ['voted', 'vote', 'approved', 'rejected']
        }

        for indicator, terms in step_indicators.items():
            if indicator in step_name_lower:
                if any(term in text_lower for term in terms):
                    return True

        return False

    def _identify_additional_practices(self, text: str, formal_steps: List[SSCProcessStep]) -> List[str]:
        """
        Identify practices that occurred but aren't in the formal process
        """
        additional = []

        # Look for common SSC activities
        activities = {
            'Public Comment Period': ['public comment', 'stakeholder input'],
            'Webinar Presentation': ['webinar', 'online presentation'],
            'Expert Testimony': ['expert testimony', 'invited speaker'],
            'Workshop': ['workshop', 'training session'],
            'Joint Session': ['joint session', 'joint meeting']
        }

        text_lower = text.lower()
        formal_step_names = [s.step_name.lower() for s in formal_steps]

        for activity, keywords in activities.items():
            if activity.lower() not in formal_step_names:
                if any(kw in text_lower for kw in keywords):
                    additional.append(activity)

        return additional

    def _analyze_timeline_compliance(self, meeting: SSCMeeting, formal_steps: List[SSCProcessStep]) -> Dict:
        """
        Analyze timeline compliance
        """
        # Calculate expected duration
        expected_days = sum(s.typical_duration_days or 0 for s in formal_steps)

        # Calculate actual duration
        actual_days = 0
        if meeting.meeting_date_start and meeting.meeting_date_end:
            actual_days = (meeting.meeting_date_end - meeting.meeting_date_start).days
        else:
            # Assume single day meeting
            actual_days = 1

        variance_days = actual_days - expected_days if expected_days > 0 else 0

        return {
            'expected_days': expected_days,
            'actual_days': actual_days,
            'variance_days': variance_days
        }

    def _calculate_timeline_score(self, timeline_data: Dict) -> float:
        """
        Calculate timeline compliance score (0-1)
        1.0 = perfect timing, decreases with variance
        """
        if not timeline_data.get('expected_days'):
            return 1.0

        variance = abs(timeline_data.get('variance_days', 0))
        expected = timeline_data.get('expected_days', 1)

        # Allow 20% variance without penalty
        threshold = expected * 0.2
        if variance <= threshold:
            return 1.0

        # Decrease score based on variance
        excess_variance = variance - threshold
        penalty = excess_variance / expected
        score = max(0.0, 1.0 - penalty)

        return score

    def _generate_compliance_flags(self, completed: List, skipped: List, timeline_data: Dict) -> List[str]:
        """
        Generate compliance warning flags
        """
        flags = []

        if len(skipped) > 0:
            flags.append(f"missing_{len(skipped)}_required_steps")

        variance = timeline_data.get('variance_days', 0)
        if variance > 30:
            flags.append("significant_timeline_delay")
        elif variance < -30:
            flags.append("unusually_fast_completion")

        if len(completed) < 3:
            flags.append("minimal_documentation")

        return flags

    def _generate_ai_insights(self, meeting: SSCMeeting, formal_steps: List, completed: List, skipped: List, timeline_data: Dict) -> str:
        """
        Generate AI insights about the meeting's process compliance
        """
        try:
            context = f"""
Meeting: {meeting.title}
Date: {meeting.meeting_date_start}
Type: {meeting.meeting_type}

Formal Process Steps: {len(formal_steps)}
Completed Steps: {len(completed)}
Skipped Steps: {len(skipped)}
Timeline Variance: {timeline_data.get('variance_days', 0)} days

Skipped Step Names: {[s.step_name for s in skipped]}

Analyze this SSC meeting's compliance with formal processes. Explain:
1. What process variations occurred and why they might be justified
2. Whether timeline variance is reasonable
3. Any patterns or concerns
4. Recommendations for improvement

Provide a concise 2-3 sentence insight.
"""

            insight = self.ai_service.generate_completion(
                prompt=context,
                max_tokens=200
            )

            return insight.strip()

        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return "AI analysis unavailable"

    def _update_observed_practices(self, meeting: SSCMeeting, process_type: str, completed: List, timeline_data: Dict):
        """
        Update the adaptive model with observed practices
        """
        try:
            # Record observed practice patterns
            for step in completed:
                pattern = f"{process_type}: {step.step_name}"

                practice = SSCObservedPractice.query.filter_by(
                    process_type=process_type,
                    practice_pattern=step.step_name
                ).first()

                if practice:
                    # Update existing practice
                    practice.frequency_count += 1
                    practice.last_observed = datetime.utcnow()
                    practice.confidence_score = min(1.0, practice.confidence_score + 0.05)

                    # Update examples
                    examples = practice.examples or []
                    examples.append({
                        'meeting_id': str(meeting.id),
                        'meeting_title': meeting.title,
                        'date': meeting.meeting_date_start.isoformat() if meeting.meeting_date_start else None
                    })
                    practice.examples = examples[-10:]  # Keep last 10 examples

                else:
                    # Create new practice
                    practice = SSCObservedPractice(
                        process_type=process_type,
                        practice_pattern=step.step_name,
                        description=step.step_description,
                        frequency_count=1,
                        confidence_score=0.1,
                        examples=[{
                            'meeting_id': str(meeting.id),
                            'meeting_title': meeting.title,
                            'date': meeting.meeting_date_start.isoformat() if meeting.meeting_date_start else None
                        }]
                    )

                db.session.add(practice)

            # Record timeline patterns
            if timeline_data.get('actual_days'):
                timeline_practice = SSCObservedPractice.query.filter_by(
                    process_type=process_type,
                    practice_pattern='typical_duration'
                ).first()

                if timeline_practice:
                    # Update average duration
                    avg_duration = timeline_practice.typical_duration_observed or 0
                    count = timeline_practice.frequency_count
                    new_avg = ((avg_duration * count) + timeline_data['actual_days']) / (count + 1)
                    timeline_practice.typical_duration_observed = int(new_avg)
                    timeline_practice.frequency_count += 1
                else:
                    timeline_practice = SSCObservedPractice(
                        process_type=process_type,
                        practice_pattern='typical_duration',
                        description='Observed typical meeting duration',
                        typical_duration_observed=timeline_data['actual_days'],
                        frequency_count=1
                    )
                    db.session.add(timeline_practice)

            db.session.commit()

        except Exception as e:
            logger.error(f"Error updating observed practices: {e}")


    def get_compliance_summary(self) -> Dict:
        """
        Get overall compliance summary across all meetings
        """
        try:
            total_meetings = SSCMeetingCompliance.query.count()

            if total_meetings == 0:
                return {
                    'total_meetings_analyzed': 0,
                    'average_compliance_score': 0,
                    'average_timeline_score': 0,
                    'common_flags': []
                }

            avg_compliance = db.session.query(
                func.avg(SSCMeetingCompliance.compliance_score)
            ).scalar() or 0

            avg_timeline = db.session.query(
                func.avg(SSCMeetingCompliance.timeline_score)
            ).scalar() or 0

            # Get common flags
            all_flags = db.session.query(SSCMeetingCompliance.compliance_flags).all()
            flag_counts = {}
            for (flags,) in all_flags:
                if flags:
                    for flag in flags:
                        flag_counts[flag] = flag_counts.get(flag, 0) + 1

            common_flags = sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                'total_meetings_analyzed': total_meetings,
                'average_compliance_score': float(avg_compliance),
                'average_timeline_score': float(avg_timeline),
                'common_flags': [{'flag': f, 'count': c} for f, c in common_flags]
            }

        except Exception as e:
            logger.error(f"Error getting compliance summary: {e}")
            return {}
