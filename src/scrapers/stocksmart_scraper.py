"""
StockSMART Scraper for Stock Status Data
Scrapes https://apps-st.fisheries.noaa.gov/stocksmart for stock status metrics
"""

import requests
from bs4 import BeautifulSoup
import logging
import re
import json
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StockSMARTScraper:
    """Scraper for NOAA StockSMART database"""

    def __init__(self):
        self.base_url = 'https://apps-st.fisheries.noaa.gov/stocksmart'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SAFMC FMP Tracker (aaron.kornbluth@gmail.com)'
        })

    def get_stock_status(self, filters: Optional[Dict] = None) -> Dict:
        """
        Get current stock status for all stocks or filtered stocks

        Args:
            filters: Optional dict with filters:
                - jurisdiction: Filter by jurisdiction (e.g., 'South Atlantic')
                - science_center: Filter by science center
                - fmp: Filter by FMP

        Returns:
            Dict with results: {'success': bool, 'stocks': List, 'count': int}
        """
        try:
            logger.info("Starting StockSMART stock status scrape...")

            # StockSMART may have an API or require special handling
            # This is a template implementation

            # Approach 1: Try to find API endpoint
            api_url = f'{self.base_url}/api/stocks'  # Hypothetical API endpoint

            # Approach 2: Scrape the main page
            response = self.session.get(f'{self.base_url}?app=homepage', timeout=30)
            response.raise_for_status()

            # StockSMART likely uses JavaScript/AJAX to load data
            # May need to inspect network requests to find actual data endpoints

            # For now, we'll return template structure
            # In production, this would parse actual StockSMART data

            stocks = self._parse_stocksmart_page(response.content)

            # Save to database
            saved_count = self._save_stock_status(stocks)

            logger.info(f"StockSMART scrape complete. Found {len(stocks)}, saved {saved_count}")

            return {
                'success': True,
                'stocks': stocks,
                'count': len(stocks),
                'saved': saved_count
            }

        except Exception as e:
            logger.error(f"Error scraping StockSMART: {e}")
            return {
                'success': False,
                'error': str(e),
                'stocks': [],
                'count': 0
            }

    def get_time_series(self, stock_name: str) -> Dict:
        """
        Get historical time series data for a stock

        Args:
            stock_name: Stock identifier

        Returns:
            Dict with time series data (catch, biomass, fishing mortality, recruitment)
        """
        try:
            # StockSMART provides time series via interactive charts
            # This would require finding the data endpoint or parsing chart data

            time_series = {
                'stock_name': stock_name,
                'catch': [],
                'biomass': [],
                'fishing_mortality': [],
                'recruitment': []
            }

            # Placeholder - in production, would scrape actual data

            return {
                'success': True,
                'time_series': time_series
            }

        except Exception as e:
            logger.error(f"Error getting time series for {stock_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_assessment_history(self, stock_name: str) -> List[Dict]:
        """
        Get history of assessments for a stock

        Args:
            stock_name: Stock identifier

        Returns:
            List of assessment records
        """
        try:
            # Parse assessment history from StockSMART

            history = []

            # Placeholder - in production, would scrape actual data

            return history

        except Exception as e:
            logger.error(f"Error getting assessment history for {stock_name}: {e}")
            return []

    def _parse_stocksmart_page(self, html_content: bytes) -> List[Dict]:
        """
        Parse StockSMART HTML page to extract stock data

        Args:
            html_content: Raw HTML content

        Returns:
            List of stock data dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            stocks = []

            # StockSMART uses JavaScript to load data dynamically
            # We need to find embedded JSON data or API calls

            # Look for embedded JSON in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                script_content = script.string
                if script_content and ('stocks' in script_content.lower() or 'data' in script_content.lower()):
                    # Try to extract JSON
                    json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script_content)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, dict) and ('stocks' in data or 'data' in data):
                                # Process stock data
                                stock_list = data.get('stocks', data.get('data', []))
                                for item in stock_list:
                                    stock = self._process_stock_item(item)
                                    if stock:
                                        stocks.append(stock)
                        except (json.JSONDecodeError, TypeError):
                            continue

            # Alternative: Look for data tables
            if not stocks:
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        # Parse table structure
                        headers = [th.text.strip().lower() for th in rows[0].find_all(['th', 'td'])]

                        for row in rows[1:]:
                            cells = row.find_all('td')
                            if len(cells) >= len(headers):
                                stock = {}
                                for i, header in enumerate(headers):
                                    if i < len(cells):
                                        stock[header] = cells[i].text.strip()

                                if stock:
                                    processed = self._process_stock_item(stock)
                                    if processed:
                                        stocks.append(processed)

            return stocks

        except Exception as e:
            logger.error(f"Error parsing StockSMART page: {e}")
            return []

    def _process_stock_item(self, item: Dict) -> Optional[Dict]:
        """
        Process a single stock item from StockSMART data

        Args:
            item: Raw stock data item

        Returns:
            Processed stock dictionary or None
        """
        try:
            stock = {
                'scraped_at': datetime.utcnow().isoformat(),
                'source': 'StockSMART'
            }

            # Map fields (field names may vary)
            field_mappings = {
                'stock_name': ['stock_name', 'stock', 'name'],
                'species': ['species', 'common_name'],
                'scientific_name': ['scientific_name', 'scientific name', 'sci_name'],
                'jurisdiction': ['jurisdiction', 'region'],
                'science_center': ['science_center', 'center'],
                'fmp': ['fmp', 'fishery management plan'],
                'ecosystem': ['ecosystem'],
                'overfished': ['overfished', 'overfished status'],
                'overfishing': ['overfishing', 'overfishing status', 'overfishing_occurring'],
                'b_bmsy': ['b/bmsy', 'b_bmsy', 'biomass ratio'],
                'f_fmsy': ['f/fmsy', 'f_fmsy', 'fishing mortality ratio'],
                'biomass_current': ['biomass', 'current biomass', 'b'],
                'biomass_msy': ['bmsy', 'msy biomass'],
                'fishing_mortality_current': ['f', 'fishing mortality', 'current f'],
                'fishing_mortality_msy': ['fmsy', 'msy fishing mortality'],
                'msy': ['msy', 'maximum sustainable yield'],
                'ofl': ['ofl', 'overfishing limit'],
                'abc': ['abc', 'acceptable biological catch'],
                'acl': ['acl', 'annual catch limit'],
                'assessment_year': ['assessment_year', 'year', 'assessment year']
            }

            # Map fields
            for target_field, possible_sources in field_mappings.items():
                for source_field in possible_sources:
                    if source_field in item:
                        value = item[source_field]

                        # Convert numeric fields
                        if target_field in ['b_bmsy', 'f_fmsy', 'biomass_current', 'biomass_msy',
                                           'fishing_mortality_current', 'fishing_mortality_msy',
                                           'msy', 'ofl', 'abc', 'acl']:
                            try:
                                stock[target_field] = float(value) if value else None
                            except (ValueError, TypeError):
                                stock[target_field] = None
                        # Convert boolean fields
                        elif target_field in ['overfished', 'overfishing']:
                            if isinstance(value, bool):
                                stock[target_field] = value
                            elif isinstance(value, str):
                                value_lower = value.lower()
                                stock[target_field] = value_lower in ['yes', 'true', 'y', '1']
                            else:
                                stock[target_field] = None
                        else:
                            stock[target_field] = value

                        break  # Found a match, move to next target field

            # Calculate ratios if we have raw biomass and F values
            if 'b_bmsy' not in stock and 'biomass_current' in stock and 'biomass_msy' in stock:
                try:
                    if stock['biomass_msy'] and stock['biomass_msy'] != 0:
                        stock['b_bmsy'] = stock['biomass_current'] / stock['biomass_msy']
                except (TypeError, ZeroDivisionError):
                    pass

            if 'f_fmsy' not in stock and 'fishing_mortality_current' in stock and 'fishing_mortality_msy' in stock:
                try:
                    if stock['fishing_mortality_msy'] and stock['fishing_mortality_msy'] != 0:
                        stock['f_fmsy'] = stock['fishing_mortality_current'] / stock['fishing_mortality_msy']
                except (TypeError, ZeroDivisionError):
                    pass

            # Determine stock status based on ratios
            if 'b_bmsy' in stock and 'f_fmsy' in stock:
                if stock['b_bmsy'] and stock['f_fmsy']:
                    if stock['b_bmsy'] >= 1.0 and stock['f_fmsy'] <= 1.0:
                        stock['stock_status'] = 'Healthy'
                    elif stock['b_bmsy'] < 1.0 and stock['f_fmsy'] > 1.0:
                        stock['stock_status'] = 'Critical'
                    elif stock['b_bmsy'] < 1.0:
                        stock['stock_status'] = 'Overfished'
                    elif stock['f_fmsy'] > 1.0:
                        stock['stock_status'] = 'Overfishing Occurring'
                    else:
                        stock['stock_status'] = 'Recovering'

            # Only return if we have meaningful data
            if stock.get('species') or stock.get('stock_name'):
                return stock

            return None

        except Exception as e:
            logger.error(f"Error processing stock item: {e}")
            return None

    def _save_stock_status(self, stocks: List[Dict]) -> int:
        """
        Save stock status data to database

        Args:
            stocks: List of stock data dictionaries

        Returns:
            Number of stocks saved
        """
        try:
            from src.database import get_db_connection

            conn = get_db_connection()
            cur = conn.cursor()

            saved_count = 0

            for stock in stocks:
                try:
                    # Try to match with existing assessment by species name
                    species = stock.get('species') or stock.get('stock_name')
                    if not species:
                        continue

                    cur.execute(
                        "SELECT id FROM stock_assessments WHERE species ILIKE %s LIMIT 1",
                        (f"%{species}%",)
                    )

                    existing = cur.fetchone()

                    if existing:
                        # Update existing with StockSMART data
                        cur.execute("""
                            UPDATE stock_assessments
                            SET
                                stock_status = COALESCE(%s, stock_status),
                                overfishing_occurring = COALESCE(%s, overfishing_occurring),
                                overfished = COALESCE(%s, overfished),
                                biomass_current = COALESCE(%s, biomass_current),
                                biomass_msy = COALESCE(%s, biomass_msy),
                                fishing_mortality_current = COALESCE(%s, fishing_mortality_current),
                                fishing_mortality_msy = COALESCE(%s, fishing_mortality_msy),
                                overfishing_limit = COALESCE(%s, overfishing_limit),
                                acceptable_biological_catch = COALESCE(%s, acceptable_biological_catch),
                                annual_catch_limit = COALESCE(%s, annual_catch_limit),
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (
                            stock.get('stock_status'),
                            stock.get('overfishing'),
                            stock.get('overfished'),
                            stock.get('biomass_current'),
                            stock.get('biomass_msy'),
                            stock.get('fishing_mortality_current'),
                            stock.get('fishing_mortality_msy'),
                            stock.get('ofl'),
                            stock.get('abc'),
                            stock.get('acl'),
                            existing[0]
                        ))
                        saved_count += 1
                    else:
                        # Create new assessment record with StockSMART data
                        cur.execute("""
                            INSERT INTO stock_assessments
                            (species, stock_name, scientific_name, stock_status,
                             overfishing_occurring, overfished,
                             biomass_current, biomass_msy,
                             fishing_mortality_current, fishing_mortality_msy,
                             overfishing_limit, acceptable_biological_catch, annual_catch_limit)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            stock.get('species'),
                            stock.get('stock_name'),
                            stock.get('scientific_name'),
                            stock.get('stock_status'),
                            stock.get('overfishing'),
                            stock.get('overfished'),
                            stock.get('biomass_current'),
                            stock.get('biomass_msy'),
                            stock.get('fishing_mortality_current'),
                            stock.get('fishing_mortality_msy'),
                            stock.get('ofl'),
                            stock.get('abc'),
                            stock.get('acl')
                        ))
                        saved_count += 1

                except Exception as e:
                    logger.error(f"Error saving stock {stock.get('species')}: {e}")
                    continue

            conn.commit()
            cur.close()
            conn.close()

            return saved_count

        except Exception as e:
            logger.error(f"Error saving stock status to database: {e}")
            return 0
