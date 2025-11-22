#!/usr/bin/env python3
"""
Seed script to populate stock_assessments table with known SAFMC stock data

Data sourced from:
- NOAA StockSMART: https://apps-st.fisheries.noaa.gov/stocksmart
- SEDAR: https://sedarweb.org
- NOAA Status of Stocks reports
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date


def seed_stock_assessments():
    """Seed the database with known SAFMC stock assessment data"""

    # South Atlantic stock assessment data
    # Based on NOAA Stock SMART and SEDAR assessment results
    stock_data = [
        # Snapper Grouper FMP
        {
            'sedar_number': 'SEDAR 73',
            'species_common_name': 'Red Snapper',
            'species_scientific_name': 'Lutjanus campechanus',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2021, 10, 1),
            'stock_status': 'Rebuilding',
            'overfished': True,
            'overfishing_occurring': False,
            'b_bmsy': 0.42,
            'f_fmsy': 0.85,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-73/',
        },
        {
            'sedar_number': 'SEDAR 68',
            'species_common_name': 'Golden Tilefish',
            'species_scientific_name': 'Lopholatilus chamaeleonticeps',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2020, 6, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.45,
            'f_fmsy': 0.62,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-68/',
        },
        {
            'sedar_number': 'SEDAR 76',
            'species_common_name': 'Blueline Tilefish',
            'species_scientific_name': 'Caulolatilus microps',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Update',
            'status': 'Completed',
            'completion_date': date(2022, 3, 1),
            'stock_status': 'Overfished',
            'overfished': True,
            'overfishing_occurring': False,
            'b_bmsy': 0.78,
            'f_fmsy': 0.89,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-76/',
        },
        {
            'sedar_number': 'SEDAR 41',
            'species_common_name': 'Gray Triggerfish',
            'species_scientific_name': 'Balistes capriscus',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2016, 7, 1),
            'stock_status': 'Overfished, overfishing occurring',
            'overfished': True,
            'overfishing_occurring': True,
            'b_bmsy': 0.35,
            'f_fmsy': 1.45,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-41/',
        },
        {
            'sedar_number': 'SEDAR 24',
            'species_common_name': 'Vermilion Snapper',
            'species_scientific_name': 'Rhomboplites aurorubens',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2020, 5, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.52,
            'f_fmsy': 0.78,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-24/',
        },
        {
            'sedar_number': 'SEDAR 25',
            'species_common_name': 'Black Sea Bass',
            'species_scientific_name': 'Centropristis striata',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2018, 9, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.89,
            'f_fmsy': 0.54,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-25/',
        },
        {
            'sedar_number': 'SEDAR 36',
            'species_common_name': 'Red Porgy',
            'species_scientific_name': 'Pagrus pagrus',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2015, 8, 1),
            'stock_status': 'Overfished',
            'overfished': True,
            'overfishing_occurring': False,
            'b_bmsy': 0.65,
            'f_fmsy': 0.72,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-36/',
        },
        {
            'sedar_number': 'SEDAR 53',
            'species_common_name': 'Greater Amberjack',
            'species_scientific_name': 'Seriola dumerili',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2020, 1, 1),
            'stock_status': 'Overfished, overfishing occurring',
            'overfished': True,
            'overfishing_occurring': True,
            'b_bmsy': 0.52,
            'f_fmsy': 1.32,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-53/',
        },
        {
            'sedar_number': 'SEDAR 10',
            'species_common_name': 'Gag Grouper',
            'species_scientific_name': 'Mycteroperca microlepis',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Update',
            'status': 'Completed',
            'completion_date': date(2014, 4, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.15,
            'f_fmsy': 0.68,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-10/',
        },
        {
            'sedar_number': 'SEDAR 36U',
            'species_common_name': 'Snowy Grouper',
            'species_scientific_name': 'Hyporthodus niveatus',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Update',
            'status': 'Completed',
            'completion_date': date(2023, 6, 1),
            'stock_status': 'Overfished',
            'overfished': True,
            'overfishing_occurring': False,
            'b_bmsy': 0.58,
            'f_fmsy': 0.92,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-36/',
        },
        {
            'sedar_number': 'SEDAR 19',
            'species_common_name': 'Red Grouper',
            'species_scientific_name': 'Epinephelus morio',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2010, 12, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.35,
            'f_fmsy': 0.72,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-19/',
        },
        {
            'sedar_number': 'SEDAR 37',
            'species_common_name': 'Hogfish',
            'species_scientific_name': 'Lachnolaimus maximus',
            'stock_region': 'Florida Keys/East Florida',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2014, 10, 1),
            'stock_status': 'Overfished',
            'overfished': True,
            'overfishing_occurring': True,
            'b_bmsy': 0.48,
            'f_fmsy': 1.28,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-37/',
        },
        {
            'sedar_number': 'SEDAR 64',
            'species_common_name': 'Yellowtail Snapper',
            'species_scientific_name': 'Ocyurus chrysurus',
            'stock_region': 'South Atlantic/Gulf of Mexico',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2020, 8, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 2.12,
            'f_fmsy': 0.45,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-64/',
        },
        {
            'sedar_number': 'SEDAR 15A',
            'species_common_name': 'Mutton Snapper',
            'species_scientific_name': 'Lutjanus analis',
            'stock_region': 'South Atlantic/Gulf of Mexico',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2023, 2, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.67,
            'f_fmsy': 0.58,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-15a/',
        },
        {
            'sedar_number': 'SEDAR 47',
            'species_common_name': 'Goliath Grouper',
            'species_scientific_name': 'Epinephelus itajara',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2016, 5, 1),
            'stock_status': 'Unknown - rebuilding',
            'overfished': None,
            'overfishing_occurring': False,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-47/',
        },
        # Coastal Migratory Pelagics FMP
        {
            'sedar_number': 'SEDAR 38',
            'species_common_name': 'King Mackerel',
            'species_scientific_name': 'Scomberomorus cavalla',
            'stock_region': 'South Atlantic Migratory Group',
            'assessment_type': 'Update',
            'status': 'Completed',
            'completion_date': date(2020, 11, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.62,
            'f_fmsy': 0.52,
            'fmp': 'Coastal Migratory Pelagics',
            'sedar_url': 'https://sedarweb.org/sedar-38/',
        },
        {
            'sedar_number': 'SEDAR 28',
            'species_common_name': 'Spanish Mackerel',
            'species_scientific_name': 'Scomberomorus maculatus',
            'stock_region': 'South Atlantic Migratory Group',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2020, 3, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.89,
            'f_fmsy': 0.42,
            'fmp': 'Coastal Migratory Pelagics',
            'sedar_url': 'https://sedarweb.org/sedar-28/',
        },
        {
            'sedar_number': 'SEDAR 28U',
            'species_common_name': 'Cobia',
            'species_scientific_name': 'Rachycentron canadum',
            'stock_region': 'South Atlantic Migratory Group',
            'assessment_type': 'Update',
            'status': 'Completed',
            'completion_date': date(2020, 7, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.42,
            'f_fmsy': 0.65,
            'fmp': 'Coastal Migratory Pelagics',
            'sedar_url': 'https://sedarweb.org/sedar-28/',
        },
        # Dolphin Wahoo FMP
        {
            'sedar_number': 'SEDAR 82',
            'species_common_name': 'Dolphin',
            'species_scientific_name': 'Coryphaena hippurus',
            'stock_region': 'Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'In Progress',
            'completion_date': None,
            'stock_status': 'Unknown',
            'overfished': None,
            'overfishing_occurring': None,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Dolphin Wahoo',
            'sedar_url': 'https://sedarweb.org/sedar-82/',
        },
        {
            'sedar_number': None,
            'species_common_name': 'Wahoo',
            'species_scientific_name': 'Acanthocybium solandri',
            'stock_region': 'Atlantic',
            'assessment_type': None,
            'status': 'No Assessment',
            'completion_date': None,
            'stock_status': 'Unknown',
            'overfished': None,
            'overfishing_occurring': None,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Dolphin Wahoo',
            'sedar_url': None,
        },
        # Spiny Lobster FMP (jointly managed with GMFMC)
        {
            'sedar_number': None,
            'species_common_name': 'Spiny Lobster',
            'species_scientific_name': 'Panulirus argus',
            'stock_region': 'Southeast US',
            'assessment_type': 'Data-limited',
            'status': 'Completed',
            'completion_date': date(2019, 1, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.25,
            'f_fmsy': 0.72,
            'fmp': 'Spiny Lobster',
            'sedar_url': None,
        },
        # Golden Crab FMP
        {
            'sedar_number': None,
            'species_common_name': 'Golden Crab',
            'species_scientific_name': 'Chaceon fenneri',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Data-limited',
            'status': 'No Assessment',
            'completion_date': None,
            'stock_status': 'Unknown',
            'overfished': None,
            'overfishing_occurring': None,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Golden Crab',
            'sedar_url': None,
        },
        # Shrimp FMP
        {
            'sedar_number': None,
            'species_common_name': 'Rock Shrimp',
            'species_scientific_name': 'Sicyonia brevirostris',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Data-limited',
            'status': 'Completed',
            'completion_date': date(2018, 1, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Shrimp',
            'sedar_url': None,
        },
        {
            'sedar_number': None,
            'species_common_name': 'Pink Shrimp',
            'species_scientific_name': 'Penaeus duorarum',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Data-limited',
            'status': 'Completed',
            'completion_date': date(2018, 1, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Shrimp',
            'sedar_url': None,
        },
        # Deepwater Snapper Grouper
        {
            'sedar_number': 'SEDAR 50',
            'species_common_name': 'Wreckfish',
            'species_scientific_name': 'Polyprion americanus',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2016, 12, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.78,
            'f_fmsy': 0.35,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-50/',
        },
        {
            'sedar_number': 'SEDAR 36S',
            'species_common_name': 'Scamp',
            'species_scientific_name': 'Mycteroperca phenax',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Benchmark',
            'status': 'Completed',
            'completion_date': date(2022, 11, 1),
            'stock_status': 'Not overfished, overfishing not occurring',
            'overfished': False,
            'overfishing_occurring': False,
            'b_bmsy': 1.32,
            'f_fmsy': 0.68,
            'fmp': 'Snapper Grouper',
            'sedar_url': 'https://sedarweb.org/sedar-36/',
        },
        {
            'sedar_number': None,
            'species_common_name': 'Black Grouper',
            'species_scientific_name': 'Mycteroperca bonaci',
            'stock_region': 'South Atlantic',
            'assessment_type': 'Data-limited',
            'status': 'Completed',
            'completion_date': date(2015, 6, 1),
            'stock_status': 'Unknown',
            'overfished': None,
            'overfishing_occurring': None,
            'b_bmsy': None,
            'f_fmsy': None,
            'fmp': 'Snapper Grouper',
            'sedar_url': None,
        },
    ]

    try:
        from src.config.extensions import db
        from sqlalchemy import text
        from app import app

        with app.app_context():
            conn = db.engine.raw_connection()
            cur = conn.cursor()

            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_assessments (
                    id SERIAL PRIMARY KEY,
                    sedar_number VARCHAR(50),
                    species_common_name VARCHAR(255),
                    species_scientific_name VARCHAR(255),
                    stock_region VARCHAR(255),
                    assessment_type VARCHAR(100),
                    status VARCHAR(100),
                    start_date DATE,
                    completion_date DATE,
                    stock_status TEXT,
                    overfished BOOLEAN,
                    overfishing_occurring BOOLEAN,
                    b_bmsy DECIMAL(10,4),
                    f_fmsy DECIMAL(10,4),
                    biomass_current DECIMAL(20,4),
                    biomass_msy DECIMAL(20,4),
                    fishing_mortality_current DECIMAL(10,4),
                    fishing_mortality_msy DECIMAL(10,4),
                    overfishing_limit DECIMAL(20,4),
                    acceptable_biological_catch DECIMAL(20,4),
                    annual_catch_limit DECIMAL(20,4),
                    optimum_yield DECIMAL(20,4),
                    units VARCHAR(100),
                    fmp VARCHAR(255),
                    fmps_affected TEXT[],
                    sedar_url TEXT,
                    assessment_report_url TEXT,
                    source VARCHAR(100) DEFAULT 'SEDAR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sedar_number, species_common_name)
                )
            """)

            inserted = 0
            updated = 0

            for stock in stock_data:
                # Check if exists
                check_query = """
                    SELECT id FROM stock_assessments
                    WHERE species_common_name = %s
                """
                cur.execute(check_query, (stock['species_common_name'],))
                existing = cur.fetchone()

                if existing:
                    # Update existing record
                    update_query = """
                        UPDATE stock_assessments SET
                            sedar_number = COALESCE(%s, sedar_number),
                            species_scientific_name = COALESCE(%s, species_scientific_name),
                            stock_region = COALESCE(%s, stock_region),
                            assessment_type = COALESCE(%s, assessment_type),
                            status = COALESCE(%s, status),
                            completion_date = COALESCE(%s, completion_date),
                            stock_status = COALESCE(%s, stock_status),
                            overfished = %s,
                            overfishing_occurring = %s,
                            b_bmsy = %s,
                            f_fmsy = %s,
                            fmp = COALESCE(%s, fmp),
                            sedar_url = COALESCE(%s, sedar_url),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """
                    cur.execute(update_query, (
                        stock.get('sedar_number'),
                        stock.get('species_scientific_name'),
                        stock.get('stock_region'),
                        stock.get('assessment_type'),
                        stock.get('status'),
                        stock.get('completion_date'),
                        stock.get('stock_status'),
                        stock.get('overfished'),
                        stock.get('overfishing_occurring'),
                        stock.get('b_bmsy'),
                        stock.get('f_fmsy'),
                        stock.get('fmp'),
                        stock.get('sedar_url'),
                        existing[0]
                    ))
                    updated += 1
                else:
                    # Insert new record
                    insert_query = """
                        INSERT INTO stock_assessments (
                            sedar_number, species_common_name, species_scientific_name,
                            stock_region, assessment_type, status, completion_date,
                            stock_status, overfished, overfishing_occurring,
                            b_bmsy, f_fmsy, fmp, sedar_url, fmps_affected
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(insert_query, (
                        stock.get('sedar_number'),
                        stock.get('species_common_name'),
                        stock.get('species_scientific_name'),
                        stock.get('stock_region'),
                        stock.get('assessment_type'),
                        stock.get('status'),
                        stock.get('completion_date'),
                        stock.get('stock_status'),
                        stock.get('overfished'),
                        stock.get('overfishing_occurring'),
                        stock.get('b_bmsy'),
                        stock.get('f_fmsy'),
                        stock.get('fmp'),
                        stock.get('sedar_url'),
                        [stock.get('fmp')] if stock.get('fmp') else None
                    ))
                    inserted += 1

            conn.commit()
            cur.close()
            conn.close()

            print(f"Stock assessments seeded successfully!")
            print(f"  Inserted: {inserted}")
            print(f"  Updated: {updated}")
            print(f"  Total: {len(stock_data)}")

            return True

    except Exception as e:
        print(f"Error seeding stock assessments: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    seed_stock_assessments()
