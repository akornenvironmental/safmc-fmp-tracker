"""
SAFE Reports Import Service
Orchestrates SAFE report scraping, AI analysis, and database import
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import anthropic
import os
import json

from src.config.extensions import db
from src.models.safe_sedar import (
    SAFEReport, SAFEReportStock, SAFEReportSection,
    SAFESEDARScrapeLog
)
from src.scrapers.safe_report_scraper import SAFEReportScraper

logger = logging.getLogger(__name__)


class SAFEImportService:
    """Service for importing SAFE reports with AI-powered stock data extraction"""

    def __init__(self):
        self.scraper = SAFEReportScraper()
        self.claude_client = None

        # Initialize Claude if API key available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
        else:
            logger.warning("ANTHROPIC_API_KEY not set - AI extraction will be skipped")

    def import_all_safe_reports(self) -> Dict:
        """
        Import all SAFE reports from SAFMC website

        Returns:
            Dict with import results
        """
        logger.info("Starting SAFE reports import...")

        # Create scrape log
        scrape_log = SAFESEDARScrapeLog(
            scrape_type='safe_reports',
            scrape_target='All FMPs',
            status='started',
            triggered_by='manual',
            started_at=datetime.now()
        )
        db.session.add(scrape_log)
        db.session.commit()

        try:
            # Step 1: Discover all reports
            logger.info("Discovering SAFE reports...")
            discovered_reports = self.scraper.discover_all_safe_reports()
            scrape_log.items_found = len(discovered_reports)

            # Step 2: Scrape and import each report
            created_count = 0
            updated_count = 0
            errors = []

            for report_metadata in discovered_reports:
                try:
                    logger.info(f"Processing {report_metadata['fmp']} SAFE report...")

                    # Scrape report content
                    report_data = self.scraper.scrape_report(report_metadata)

                    if report_data.get('error'):
                        errors.append(f"{report_metadata['fmp']}: {report_data['error']}")
                        scrape_log.errors_count += 1
                        continue

                    # Import to database
                    result = self._import_safe_report(report_data)

                    if result == 'created':
                        created_count += 1
                    elif result == 'updated':
                        updated_count += 1

                    scrape_log.items_processed += 1

                except Exception as e:
                    error_msg = f"Error importing {report_metadata.get('fmp', 'Unknown')}: {str(e)}"
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
                scrape_log.error_messages = errors[:100]

            db.session.commit()

            logger.info(f"SAFE reports import complete: {created_count} created, {updated_count} updated, {scrape_log.errors_count} errors")

            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': scrape_log.errors_count,
                'total_processed': scrape_log.items_processed,
                'error_messages': errors[:10]
            }

        except Exception as e:
            logger.error(f"Critical error in import_all_safe_reports: {e}")

            scrape_log.status = 'failed'
            scrape_log.completed_at = datetime.now()
            scrape_log.error_messages = [str(e)]
            db.session.commit()

            return {
                'success': False,
                'error': str(e)
            }

    def _import_safe_report(self, report_data: Dict) -> str:
        """
        Import a single SAFE report into database

        Args:
            report_data: Dictionary from scraper with AI-extracted data

        Returns:
            'created', 'updated', or 'skipped'
        """
        fmp = report_data.get('fmp')
        report_year = report_data.get('report_year', datetime.now().year)

        if not fmp:
            raise ValueError("FMP required")

        # Check if report exists
        existing = SAFEReport.query.filter_by(
            fmp=fmp,
            report_year=report_year
        ).first()

        # Create or update report
        if existing:
            safe_report = existing
            action = 'updated'
        else:
            safe_report = SAFEReport()
            action = 'created'

        # Update report fields
        safe_report.fmp = fmp
        safe_report.report_year = report_year
        safe_report.report_title = report_data.get('report_title')
        safe_report.source_url = report_data.get('source_url')
        safe_report.source_format = report_data.get('source_format')
        safe_report.html_content = report_data.get('html_content')
        safe_report.pdf_file_path = report_data.get('pdf_file_path')
        safe_report.is_current = report_data.get('is_current', True)
        safe_report.last_scraped = datetime.now()

        if action == 'created':
            db.session.add(safe_report)

        db.session.flush()  # Get ID

        # Extract and import stock data using AI
        if self.claude_client:
            self._extract_and_import_stock_data(safe_report, report_data)

        # Import sections
        self._import_sections(safe_report, report_data)

        db.session.commit()

        logger.info(f"{action.capitalize()} SAFE report: {fmp} {report_year}")
        return action

    def _extract_and_import_stock_data(self, safe_report: SAFEReport, report_data: Dict):
        """
        Use AI to extract stock-specific data from report and create SAFEReportStock records

        Args:
            safe_report: SAFEReport database object
            report_data: Scraped report data with content
        """
        logger.info(f"Extracting stock data for {safe_report.fmp}...")

        # Get relevant content for AI analysis
        content = self._prepare_content_for_ai(report_data)

        if not content or len(content) < 200:
            logger.warning("Insufficient content for AI extraction")
            return

        try:
            # Use AI to extract stock data
            stocks_data = self._ai_extract_stock_data(safe_report.fmp, content)

            if not stocks_data:
                logger.warning("No stock data extracted")
                return

            # Delete existing stocks for this report (for updates)
            SAFEReportStock.query.filter_by(safe_report_id=safe_report.id).delete()

            # Create new stock records
            for stock_data in stocks_data:
                stock = SAFEReportStock(
                    safe_report_id=safe_report.id,
                    species_name=stock_data.get('species_name'),
                    common_name=stock_data.get('common_name'),
                    scientific_name=stock_data.get('scientific_name'),
                    stock_status=stock_data.get('stock_status'),
                    overfishing_status=stock_data.get('overfishing_status'),
                    acl=stock_data.get('acl'),
                    abc=stock_data.get('abc'),
                    ofl=stock_data.get('ofl'),
                    total_landings=stock_data.get('total_landings'),
                    commercial_landings=stock_data.get('commercial_landings'),
                    recreational_landings=stock_data.get('recreational_landings'),
                    acl_utilization=stock_data.get('acl_utilization'),
                    acl_exceeded=stock_data.get('acl_exceeded'),
                    ex_vessel_value=stock_data.get('ex_vessel_value'),
                    last_assessment_year=stock_data.get('last_assessment_year'),
                    sedar_number=stock_data.get('sedar_number')
                )

                db.session.add(stock)

            logger.info(f"Imported {len(stocks_data)} stocks for {safe_report.fmp}")

        except Exception as e:
            logger.error(f"Error extracting stock data: {e}")

    def _prepare_content_for_ai(self, report_data: Dict) -> str:
        """Prepare report content for AI analysis"""
        content_parts = []

        # Include title
        if report_data.get('report_title'):
            content_parts.append(f"Title: {report_data['report_title']}")

        # Include sections (prioritize stock status sections)
        sections = report_data.get('sections', [])
        stock_sections = [s for s in sections if s.get('section_type') == 'stock_status']
        other_sections = [s for s in sections if s.get('section_type') != 'stock_status']

        for section in (stock_sections + other_sections)[:10]:  # Max 10 sections
            if section.get('content'):
                content_parts.append(f"\n## {section.get('section_title', 'Section')}\n{section['content'][:2000]}")

        # Include table data if available
        tables = report_data.get('tables', [])
        for table in tables[:5]:  # Max 5 tables
            if table.get('rows'):
                content_parts.append(f"\n## Table\n")
                for row in table['rows'][:20]:  # Max 20 rows per table
                    content_parts.append(' | '.join(str(cell) for cell in row))

        # If no sections, use raw text
        if not content_parts:
            if report_data.get('pdf_text'):
                content_parts.append(report_data['pdf_text'][:20000])
            elif report_data.get('html_content'):
                # Strip HTML tags
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(report_data['html_content'], 'html.parser')
                content_parts.append(soup.get_text()[:20000])

        return '\n'.join(content_parts)

    def _ai_extract_stock_data(self, fmp: str, content: str) -> List[Dict]:
        """
        Use Claude AI to extract stock-specific data from SAFE report content

        Args:
            fmp: Fishery Management Plan name
            content: Report content text

        Returns:
            List of stock data dictionaries
        """
        if not self.claude_client:
            return []

        prompt = f"""Analyze this SAFE (Stock Assessment and Fishery Evaluation) report for {fmp} FMP and extract stock-specific data.

IMPORTANT: Extract data for EACH individual species/stock mentioned in the report.

Report Content:
{content[:15000]}  # Limit to fit in context

For EACH species/stock in the report, extract:

1. Species Name (common name)
2. Scientific Name (if available)
3. Stock Status: "Overfished" or "Not Overfished" or "Unknown"
4. Overfishing Status: "Overfishing Occurring" or "No Overfishing" or "Unknown"
5. ACL (Annual Catch Limit) in pounds (number only)
6. ABC (Acceptable Biological Catch) in pounds (number only)
7. OFL (Overfishing Limit) in pounds (number only)
8. Total Landings in pounds (commercial + recreational)
9. Commercial Landings in pounds
10. Recreational Landings in pounds
11. ACL Utilization (percentage: landings/ACL * 100)
12. ACL Exceeded (true if utilization > 100%)
13. Ex-vessel Value (commercial fishery value in dollars)
14. Last Assessment Year (year of most recent assessment)
15. SEDAR Number (if mentioned, e.g., "SEDAR 80")

Return a JSON array with one object per species. Use null for missing values.

Example format:
[
  {{
    "species_name": "Red Snapper",
    "common_name": "Red Snapper",
    "scientific_name": "Lutjanus campechanus",
    "stock_status": "Not Overfished",
    "overfishing_status": "No Overfishing",
    "acl": 5500000,
    "abc": 5200000,
    "ofl": 6000000,
    "total_landings": 4800000,
    "commercial_landings": 2900000,
    "recreational_landings": 1900000,
    "acl_utilization": 87.3,
    "acl_exceeded": false,
    "ex_vessel_value": 15000000,
    "last_assessment_year": 2023,
    "sedar_number": "SEDAR 73"
  }},
  {{
    "species_name": "Gag Grouper",
    ...
  }}
]

Return ONLY the JSON array, no other text.
"""

        try:
            logger.info(f"Requesting AI stock data extraction for {fmp}...")

            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            # Parse JSON response
            stocks_data = json.loads(response_text)

            logger.info(f"AI extracted {len(stocks_data)} stocks for {fmp}")
            return stocks_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"AI stock extraction failed for {fmp}: {e}")
            return []

    def _import_sections(self, safe_report: SAFEReport, report_data: Dict):
        """Import report sections into database"""
        sections = report_data.get('sections', [])

        if not sections:
            return

        # Delete existing sections for this report (for updates)
        SAFEReportSection.query.filter_by(safe_report_id=safe_report.id).delete()

        # Import new sections
        for section_data in sections:
            section = SAFEReportSection(
                safe_report_id=safe_report.id,
                section_type=section_data.get('section_type'),
                section_title=section_data.get('section_title'),
                content=section_data.get('content'),
                word_count=section_data.get('word_count')
            )

            db.session.add(section)

        logger.info(f"Imported {len(sections)} sections")

    def import_single_fmp_report(self, fmp: str) -> Dict:
        """
        Import SAFE report for a specific FMP only

        Args:
            fmp: FMP name ('Snapper Grouper', 'Dolphin Wahoo', 'Shrimp')

        Returns:
            Import result dictionary
        """
        logger.info(f"Importing SAFE report for {fmp} only...")

        try:
            # Discover reports
            all_reports = self.scraper.discover_all_safe_reports()

            # Filter to specific FMP
            fmp_reports = [r for r in all_reports if r.get('fmp') == fmp]

            if not fmp_reports:
                return {
                    'success': False,
                    'error': f'No reports found for {fmp}'
                }

            # Import first (most current) report
            report_metadata = fmp_reports[0]
            report_data = self.scraper.scrape_report(report_metadata)

            if report_data.get('error'):
                return {
                    'success': False,
                    'error': report_data['error']
                }

            # Import to database
            result = self._import_safe_report(report_data)

            return {
                'success': True,
                'action': result,
                'fmp': fmp
            }

        except Exception as e:
            logger.error(f"Error importing {fmp} SAFE report: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Test the SAFE import service"""
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
        service = SAFEImportService()

        print("Testing SAFE Import Service...")
        print("=" * 60)

        # Test: Import Dolphin Wahoo SAFE report (smaller, faster)
        print("\nImporting Dolphin Wahoo SAFE report...")
        result = service.import_single_fmp_report('Dolphin Wahoo')

        print(f"\nResults:")
        if result.get('success'):
            print(f"  Action: {result.get('action')}")
            print(f"  FMP: {result.get('fmp')}")
        else:
            print(f"  Error: {result.get('error')}")


if __name__ == '__main__':
    main()
