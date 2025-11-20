"""
SEDAR Import Service
Orchestrates SEDAR assessment scraping, AI analysis, and database import
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import anthropic
import os

from src.config.extensions import db
from src.models.safe_sedar import SEDARAssessment, AssessmentActionLink, SAFESEDARScrapeLog
from src.scrapers.sedar_scraper_enhanced import SEDARScraperEnhanced
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class SEDARImportService:
    """Service for importing SEDAR assessments with AI-powered analysis"""

    def __init__(self):
        self.scraper = SEDARScraperEnhanced()
        self.claude_client = None

        # Initialize Claude if API key available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
        else:
            logger.warning("ANTHROPIC_API_KEY not set - AI extraction will be skipped")

    def import_all_assessments(self, safmc_only: bool = False) -> Dict:
        """
        Import all SEDAR assessments from sedarweb.org

        Args:
            safmc_only: If True, only import SAFMC-related assessments

        Returns:
            Dict with import results
        """
        logger.info(f"Starting SEDAR import (SAFMC only: {safmc_only})...")

        # Create scrape log
        scrape_log = SAFESEDARScrapeLog(
            scrape_type='sedar_assessments',
            scrape_target='All' if not safmc_only else 'SAFMC only',
            status='started',
            triggered_by='manual',
            started_at=datetime.now()
        )
        db.session.add(scrape_log)
        db.session.commit()

        try:
            # Step 1: Scrape assessments
            logger.info("Scraping SEDAR assessments...")
            if safmc_only:
                scraped_assessments = self.scraper.get_safmc_assessments_only()
            else:
                scraped_assessments = self.scraper.scrape_all_assessments()

            scrape_log.items_found = len(scraped_assessments)

            # Step 2: Process each assessment
            created_count = 0
            updated_count = 0
            errors = []

            for assessment_data in scraped_assessments:
                try:
                    result = self._import_single_assessment(assessment_data)
                    if result == 'created':
                        created_count += 1
                    elif result == 'updated':
                        updated_count += 1

                    scrape_log.items_processed += 1

                except Exception as e:
                    error_msg = f"Error importing {assessment_data.get('sedar_number')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    scrape_log.errors_count += 1

            # Update scrape log
            scrape_log.items_created = created_count
            scrape_log.items_updated = updated_count
            scrape_log.status = 'completed' if not errors else 'partial'
            scrape_log.completed_at = datetime.now()
            scrape_log.duration_seconds = int((scrape_log.completed_at - scrape_log.started_at).total_seconds())

            if errors:
                scrape_log.error_messages = errors[:100]  # Limit to 100 errors

            db.session.commit()

            logger.info(f"SEDAR import complete: {created_count} created, {updated_count} updated, {scrape_log.errors_count} errors")

            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': scrape_log.errors_count,
                'total_processed': scrape_log.items_processed,
                'error_messages': errors[:10]  # Return first 10 errors
            }

        except Exception as e:
            logger.error(f"Critical error in import_all_assessments: {e}")

            scrape_log.status = 'failed'
            scrape_log.completed_at = datetime.now()
            scrape_log.error_messages = [str(e)]
            db.session.commit()

            return {
                'success': False,
                'error': str(e)
            }

    def _import_single_assessment(self, assessment_data: Dict) -> str:
        """
        Import a single SEDAR assessment into database

        Args:
            assessment_data: Dictionary from scraper

        Returns:
            'created', 'updated', or 'skipped'
        """
        sedar_number = assessment_data.get('sedar_number')

        if not sedar_number:
            raise ValueError("Missing sedar_number")

        # Check if exists
        existing = SEDARAssessment.query.filter_by(sedar_number=sedar_number).first()

        # Use AI to extract additional insights if content available
        if self.claude_client and assessment_data.get('page_content'):
            ai_insights = self._extract_ai_insights(assessment_data)
            assessment_data.update(ai_insights)

        if existing:
            # Update existing assessment
            self._update_assessment(existing, assessment_data)
            return 'updated'
        else:
            # Create new assessment
            self._create_assessment(assessment_data)
            return 'created'

    def _create_assessment(self, data: Dict):
        """Create new SEDAR assessment record"""
        assessment = SEDARAssessment(
            sedar_number=data.get('sedar_number'),
            full_title=data.get('full_title'),
            species_name=data.get('species_name'),
            common_name=data.get('species_name'),  # Same as species_name for now
            scientific_name=data.get('scientific_name'),
            stock_area=data.get('stock_area'),
            fmp=data.get('fmp'),
            council=data.get('council'),
            assessment_status=data.get('assessment_status', 'Unknown'),
            assessment_type=data.get('assessment_type', 'Standard'),
            kickoff_date=data.get('kickoff_date'),
            data_workshop_date=data.get('data_workshop_date'),
            assessment_workshop_date=data.get('assessment_workshop_date'),
            review_workshop_date=data.get('review_workshop_date'),
            completion_date=data.get('completion_date'),
            expected_completion_date=data.get('expected_completion_date'),
            council_review_date=data.get('council_review_date'),
            sedar_url=data.get('sedar_url'),
            final_report_url=data.get('final_report_url'),
            executive_summary_url=data.get('executive_summary_url'),
            data_report_url=data.get('data_report_url'),
            stock_status=data.get('stock_status'),
            overfishing_status=data.get('overfishing_status'),
            abc_recommendation=data.get('abc_recommendation'),
            ofl_recommendation=data.get('ofl_recommendation'),
            rebuilding_required=data.get('rebuilding_required'),
            rebuilding_timeline=data.get('rebuilding_timeline'),
            executive_summary=data.get('executive_summary'),
            key_recommendations=data.get('key_recommendations'),
            management_implications=data.get('management_implications'),
            data_limitations=data.get('data_limitations'),
            last_scraped=datetime.now()
        )

        db.session.add(assessment)
        db.session.commit()

        logger.info(f"Created SEDAR assessment: {assessment.sedar_number}")

    def _update_assessment(self, assessment: SEDARAssessment, data: Dict):
        """Update existing SEDAR assessment record"""
        # Update fields that may have changed
        if data.get('full_title'):
            assessment.full_title = data['full_title']
        if data.get('species_name'):
            assessment.species_name = data['species_name']
            assessment.common_name = data['species_name']
        if data.get('scientific_name'):
            assessment.scientific_name = data['scientific_name']
        if data.get('stock_area'):
            assessment.stock_area = data['stock_area']
        if data.get('fmp'):
            assessment.fmp = data['fmp']
        if data.get('council'):
            assessment.council = data['council']
        if data.get('assessment_status'):
            assessment.assessment_status = data['assessment_status']
        if data.get('assessment_type'):
            assessment.assessment_type = data['assessment_type']

        # Update dates
        if data.get('kickoff_date'):
            assessment.kickoff_date = data['kickoff_date']
        if data.get('data_workshop_date'):
            assessment.data_workshop_date = data['data_workshop_date']
        if data.get('assessment_workshop_date'):
            assessment.assessment_workshop_date = data['assessment_workshop_date']
        if data.get('review_workshop_date'):
            assessment.review_workshop_date = data['review_workshop_date']
        if data.get('completion_date'):
            assessment.completion_date = data['completion_date']
        if data.get('council_review_date'):
            assessment.council_review_date = data['council_review_date']

        # Update URLs
        if data.get('sedar_url'):
            assessment.sedar_url = data['sedar_url']
        if data.get('final_report_url'):
            assessment.final_report_url = data['final_report_url']
        if data.get('executive_summary_url'):
            assessment.executive_summary_url = data['executive_summary_url']
        if data.get('data_report_url'):
            assessment.data_report_url = data['data_report_url']

        # Update AI-extracted content
        if data.get('stock_status'):
            assessment.stock_status = data['stock_status']
        if data.get('overfishing_status'):
            assessment.overfishing_status = data['overfishing_status']
        if data.get('abc_recommendation'):
            assessment.abc_recommendation = data['abc_recommendation']
        if data.get('ofl_recommendation'):
            assessment.ofl_recommendation = data['ofl_recommendation']
        if data.get('rebuilding_required') is not None:
            assessment.rebuilding_required = data['rebuilding_required']
        if data.get('rebuilding_timeline'):
            assessment.rebuilding_timeline = data['rebuilding_timeline']
        if data.get('executive_summary'):
            assessment.executive_summary = data['executive_summary']
        if data.get('key_recommendations'):
            assessment.key_recommendations = data['key_recommendations']
        if data.get('management_implications'):
            assessment.management_implications = data['management_implications']
        if data.get('data_limitations'):
            assessment.data_limitations = data['data_limitations']

        assessment.last_scraped = datetime.now()
        assessment.updated_at = datetime.now()

        db.session.commit()

        logger.info(f"Updated SEDAR assessment: {assessment.sedar_number}")

    def _extract_ai_insights(self, assessment_data: Dict) -> Dict:
        """
        Use Claude AI to extract key insights from assessment content

        Args:
            assessment_data: Dictionary with 'page_content' field

        Returns:
            Dictionary with extracted insights
        """
        if not self.claude_client:
            return {}

        content = assessment_data.get('page_content', '')
        if not content or len(content) < 100:
            return {}

        sedar_number = assessment_data.get('sedar_number', 'Unknown')
        species = assessment_data.get('species_name', 'Unknown')

        prompt = f"""Analyze this SEDAR stock assessment content and extract key information.

SEDAR Assessment: {sedar_number}
Species: {species}

Content:
{content}

Extract the following information (if available):

1. Stock Status: Is the stock "Overfished" or "Not Overfished" or "Unknown"? (one word answer)
2. Overfishing Status: Is overfishing "Occurring" or "Not Occurring" or "Unknown"? (one word answer)
3. ABC Recommendation: Recommended Acceptable Biological Catch in pounds (number only, or null)
4. OFL Recommendation: Overfishing Limit in pounds (number only, or null)
5. Rebuilding Required: Yes or No or Unknown
6. Rebuilding Timeline: If rebuilding required, what is the timeline? (e.g., "10 years", "by 2030")
7. Key Recommendations: List 2-4 key management recommendations (bullet points)
8. Management Implications: Brief summary of management implications (1-2 sentences)
9. Data Limitations: Key data gaps or uncertainties mentioned (1-2 sentences)

Return ONLY a JSON object with these exact keys:
{{
  "stock_status": "...",
  "overfishing_status": "...",
  "abc_recommendation": number or null,
  "ofl_recommendation": number or null,
  "rebuilding_required": boolean or null,
  "rebuilding_timeline": "..." or null,
  "key_recommendations": "...",
  "management_implications": "...",
  "data_limitations": "..."
}}

If information is not available in the content, use null or "Unknown".
"""

        try:
            logger.info(f"Requesting AI analysis for {sedar_number}...")

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            # Parse JSON response
            import json
            insights = json.loads(response_text)

            # Convert boolean strings to actual booleans
            if isinstance(insights.get('rebuilding_required'), str):
                rebuilding_str = insights['rebuilding_required'].lower()
                if rebuilding_str in ['yes', 'true']:
                    insights['rebuilding_required'] = True
                elif rebuilding_str in ['no', 'false']:
                    insights['rebuilding_required'] = False
                else:
                    insights['rebuilding_required'] = None

            logger.info(f"AI analysis complete for {sedar_number}")
            return insights

        except Exception as e:
            logger.warning(f"AI extraction failed for {sedar_number}: {e}")
            return {}

    def link_assessments_to_actions(self, confidence_threshold: int = 70) -> Dict:
        """
        Automatically link SEDAR assessments to management actions using fuzzy matching

        Args:
            confidence_threshold: Minimum fuzzy match score (0-100) to create link

        Returns:
            Dict with linking results
        """
        logger.info("Starting automatic assessment-to-action linking...")

        from src.models.action import Action

        assessments = SEDARAssessment.query.all()
        actions = Action.query.all()

        created_links = 0
        skipped_links = 0

        for assessment in assessments:
            species = assessment.species_name or assessment.common_name
            if not species:
                continue

            # Find actions that might be related to this assessment
            for action in actions:
                # Skip if link already exists
                existing_link = AssessmentActionLink.query.filter_by(
                    sedar_assessment_id=assessment.id,
                    action_id=action.action_id
                ).first()

                if existing_link:
                    skipped_links += 1
                    continue

                # Calculate match score
                score = self._calculate_link_score(assessment, action)

                if score >= confidence_threshold:
                    # Determine confidence level
                    if score >= 90:
                        confidence = 'high'
                    elif score >= 80:
                        confidence = 'medium'
                    else:
                        confidence = 'low'

                    # Create link
                    link = AssessmentActionLink(
                        sedar_assessment_id=assessment.id,
                        action_id=action.action_id,
                        link_type='basis_for_action',
                        confidence=confidence,
                        notes=f"Auto-linked with {score}% confidence",
                        created_by='system',
                        verified=False
                    )

                    db.session.add(link)
                    created_links += 1

                    logger.info(f"Linked {assessment.sedar_number} to {action.action_id} ({confidence} confidence)")

        db.session.commit()

        logger.info(f"Linking complete: {created_links} new links, {skipped_links} skipped")

        return {
            'success': True,
            'created_links': created_links,
            'skipped_links': skipped_links
        }

    def _calculate_link_score(self, assessment: SEDARAssessment, action) -> int:
        """
        Calculate fuzzy match score between assessment and action

        Args:
            assessment: SEDARAssessment object
            action: Action object

        Returns:
            Score from 0-100
        """
        scores = []

        # Compare species names
        if assessment.species_name and action.title:
            species_score = fuzz.partial_ratio(
                assessment.species_name.lower(),
                action.title.lower()
            )
            scores.append(species_score)

        # Compare SEDAR number mentioned in action description/title
        if action.description:
            sedar_in_desc = assessment.sedar_number.lower() in action.description.lower()
            if sedar_in_desc:
                scores.append(100)

        # Compare FMP
        if assessment.fmp and action.fmp:
            if assessment.fmp.lower() == action.fmp.lower():
                scores.append(80)

        # If no scores, return 0
        if not scores:
            return 0

        # Return average score
        return int(sum(scores) / len(scores))


def main():
    """Test the SEDAR import service"""
    from src.config.extensions import db
    from flask import Flask

    # Create minimal Flask app for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost/safmc_fmp_tracker'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        service = SEDARImportService()

        print("Testing SEDAR Import Service...")
        print("=" * 60)

        # Test: Import SAFMC assessments only (smaller subset for testing)
        print("\nImporting SAFMC assessments...")
        result = service.import_all_assessments(safmc_only=True)

        print(f"\nResults:")
        print(f"  Created: {result.get('created')}")
        print(f"  Updated: {result.get('updated')}")
        print(f"  Errors: {result.get('errors')}")

        if result.get('error_messages'):
            print(f"\nFirst few errors:")
            for error in result['error_messages'][:3]:
                print(f"  - {error}")


if __name__ == '__main__':
    main()
