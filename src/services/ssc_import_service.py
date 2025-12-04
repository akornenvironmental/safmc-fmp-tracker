"""
SSC Import Service
Imports SSC meetings, documents, and recommendations into the database
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.exc import IntegrityError

from src.config.extensions import db
from src.models.ssc import SSCMeeting, SSCRecommendation, SSCDocument
from src.scrapers.ssc_meeting_scraper import SSCMeetingScraper

logger = logging.getLogger(__name__)


class SSCImportService:
    """Service for importing SSC data"""

    def __init__(self):
        self.scraper = SSCMeetingScraper()

    def import_all_meetings(self, download_documents=True) -> Dict[str, int]:
        """
        Import all SSC meetings from safmc.net

        Args:
            download_documents: If True, download and parse document content

        Returns:
            Dictionary with counts of imported items
        """
        stats = {
            'meetings_created': 0,
            'meetings_updated': 0,
            'documents_created': 0,
            'recommendations_created': 0,
            'errors': 0
        }

        try:
            # Scrape all meetings
            logger.info("Scraping SSC meetings from safmc.net...")
            meetings_data = self.scraper.scrape_all_meetings()
            logger.info(f"Found {len(meetings_data)} meetings to process")

            for meeting_data in meetings_data:
                try:
                    result = self._import_meeting(meeting_data, download_documents)
                    stats['meetings_created'] += result['created']
                    stats['meetings_updated'] += result['updated']
                    stats['documents_created'] += result['documents']
                    stats['recommendations_created'] += result['recommendations']
                except Exception as e:
                    logger.error(f"Error importing meeting {meeting_data.get('title')}: {e}")
                    stats['errors'] += 1
                    continue

            db.session.commit()
            logger.info(f"Import complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error in import_all_meetings: {e}")
            db.session.rollback()
            stats['errors'] += 1
            return stats

    def _import_meeting(self, meeting_data: Dict, download_documents: bool) -> Dict[str, int]:
        """
        Import a single meeting and its documents

        Returns:
            Dictionary with counts: {'created': 0/1, 'updated': 0/1, 'documents': n, 'recommendations': n}
        """
        result = {
            'created': 0,
            'updated': 0,
            'documents': 0,
            'recommendations': 0
        }

        # Check if meeting already exists (by title and date)
        existing_meeting = None
        if meeting_data.get('meeting_date_start'):
            existing_meeting = SSCMeeting.query.filter_by(
                title=meeting_data['title'],
                meeting_date_start=meeting_data['meeting_date_start']
            ).first()

        if existing_meeting:
            # Update existing meeting
            meeting = existing_meeting
            result['updated'] = 1
            logger.info(f"Updating existing meeting: {meeting.title}")
        else:
            # Create new meeting
            meeting = SSCMeeting(
                title=meeting_data['title'],
                meeting_date_start=meeting_data.get('meeting_date_start') or datetime.now(),
                meeting_date_end=meeting_data.get('meeting_date_end'),
                location=meeting_data.get('location'),
                is_virtual=meeting_data.get('is_virtual', False),
                meeting_type=meeting_data.get('meeting_type'),
                status='completed' if meeting_data.get('report_url') else 'scheduled',
                agenda_url=meeting_data.get('agenda_url'),
                briefing_book_url=meeting_data.get('briefing_book_url'),
                report_url=meeting_data.get('report_url'),
                webinar_link=meeting_data.get('webinar_link'),
                description=meeting_data.get('description'),
                topics=meeting_data.get('topics', []),
                species_discussed=meeting_data.get('species_discussed', [])
            )
            db.session.add(meeting)
            db.session.flush()  # Get ID
            result['created'] = 1
            logger.info(f"Created new meeting: {meeting.title}")

        # Import documents
        if download_documents:
            result['documents'] += self._import_meeting_documents(meeting, meeting_data)
            result['recommendations'] += self._import_meeting_recommendations(meeting, meeting_data)

        return result

    def _import_meeting_documents(self, meeting: SSCMeeting, meeting_data: Dict) -> int:
        """
        Import documents for a meeting
        Returns count of documents created
        """
        count = 0

        # Document types to import
        doc_types = {
            'agenda_url': 'Agenda',
            'briefing_book_url': 'Briefing Book',
            'report_url': 'Final Report'
        }

        for url_key, doc_type in doc_types.items():
            url = meeting_data.get(url_key)
            if not url:
                continue

            # Check if document already exists
            existing_doc = SSCDocument.query.filter_by(
                meeting_id=meeting.id,
                url=url
            ).first()

            if existing_doc:
                continue

            # Create document record
            document = SSCDocument(
                meeting_id=meeting.id,
                document_type=doc_type,
                title=f"{meeting.title} - {doc_type}",
                url=url,
                upload_date=meeting.meeting_date_start.date() if meeting.meeting_date_start else None
            )
            db.session.add(document)
            count += 1
            logger.info(f"Added document: {doc_type} for {meeting.title}")

        return count

    def _import_meeting_recommendations(self, meeting: SSCMeeting, meeting_data: Dict) -> int:
        """
        Download and parse meeting report to extract recommendations
        Returns count of recommendations created
        """
        count = 0

        report_url = meeting_data.get('report_url')
        if not report_url:
            return count

        try:
            # Download report
            logger.info(f"Downloading report from {report_url}")
            report_bytes = self.scraper.download_document(report_url)
            if not report_bytes:
                return count

            # Extract text from PDF
            report_text = self.scraper.extract_text_from_pdf(report_bytes)
            if not report_text:
                return count

            # Parse recommendations
            recommendations_data = self.scraper.parse_recommendations_from_report(report_text)
            logger.info(f"Found {len(recommendations_data)} recommendations in report")

            # Store recommendations
            for rec_data in recommendations_data:
                # Check if recommendation already exists
                existing_rec = SSCRecommendation.query.filter_by(
                    meeting_id=meeting.id,
                    recommendation_number=rec_data.get('recommendation_number')
                ).first()

                if existing_rec:
                    continue

                recommendation = SSCRecommendation(
                    meeting_id=meeting.id,
                    recommendation_number=rec_data.get('recommendation_number'),
                    title=rec_data.get('title'),
                    recommendation_text=rec_data.get('recommendation_text'),
                    recommendation_type=rec_data.get('recommendation_type'),
                    species=rec_data.get('species', []),
                    abc_value=rec_data.get('abc_value'),
                    abc_units=rec_data.get('abc_units'),
                    status=rec_data.get('status', 'pending')
                )
                db.session.add(recommendation)
                count += 1

            logger.info(f"Imported {count} recommendations for {meeting.title}")

        except Exception as e:
            logger.error(f"Error importing recommendations for {meeting.title}: {e}")

        return count

    def update_meeting_from_web(self, meeting_id: str) -> bool:
        """
        Re-scrape and update a specific meeting
        """
        try:
            meeting = SSCMeeting.query.get(meeting_id)
            if not meeting:
                logger.error(f"Meeting not found: {meeting_id}")
                return False

            # Re-scrape all meetings and find this one
            meetings_data = self.scraper.scrape_all_meetings()

            for meeting_data in meetings_data:
                if meeting_data['title'] == meeting.title:
                    # Update meeting
                    self._import_meeting(meeting_data, download_documents=True)
                    db.session.commit()
                    logger.info(f"Updated meeting: {meeting.title}")
                    return True

            logger.warning(f"Meeting not found on website: {meeting.title}")
            return False

        except Exception as e:
            logger.error(f"Error updating meeting {meeting_id}: {e}")
            db.session.rollback()
            return False


def run_import():
    """
    Standalone function to run SSC import
    """
    from app import app

    with app.app_context():
        service = SSCImportService()
        stats = service.import_all_meetings(download_documents=True)

        print("\n=== SSC Import Complete ===")
        print(f"Meetings created: {stats['meetings_created']}")
        print(f"Meetings updated: {stats['meetings_updated']}")
        print(f"Documents created: {stats['documents_created']}")
        print(f"Recommendations created: {stats['recommendations_created']}")
        print(f"Errors: {stats['errors']}")


if __name__ == '__main__':
    run_import()
