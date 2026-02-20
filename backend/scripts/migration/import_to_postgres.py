#!/usr/bin/env python3
"""
Import CSV data from BigQuery export into PostgreSQL
"""
import os
import sys
import psycopg2
from pathlib import Path
from datetime import datetime
import csv

# PostgreSQL Configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "macro_dashboard"),
    "user": os.getenv("POSTGRES_USER", "macro_user"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
}

INPUT_DIR = Path("./migration_data")


def import_csv_to_table(conn, schema: str, table: str, csv_path: Path):
    """Import CSV file into PostgreSQL table"""
    print(f"Importing {schema}.{table}...")

    try:
        with conn.cursor() as cur:
            # Read CSV to get column names
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)

            # Use COPY command for fast import
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Skip header
                next(f)

                # COPY command
                copy_sql = f"""
                COPY {schema}.{table} ({','.join(headers)})
                FROM STDIN WITH CSV
                """
                cur.copy_expert(copy_sql, f)

            conn.commit()

            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            count = cur.fetchone()[0]

            print(f"  ✓ Imported {count:,} rows")
            return count

    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error importing {schema}.{table}: {str(e)}")
        return 0


def main():
    """Main import function"""
    print("=" * 60)
    print("BigQuery to PostgreSQL Migration - Data Import")
    print("=" * 60)
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Input: {INPUT_DIR.absolute()}")
    print()

    # Check input directory
    if not INPUT_DIR.exists():
        print(f"✗ Input directory not found: {INPUT_DIR.absolute()}")
        print("\nRun export_from_bigquery.py first to export data.")
        sys.exit(1)

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to PostgreSQL")
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL: {str(e)}")
        print("\nMake sure PostgreSQL is running and credentials are correct:")
        print("  export POSTGRES_PASSWORD=your_password")
        sys.exit(1)

    # Import tables
    total_rows = 0
    start_time = datetime.now()

    # Schema mapping: BigQuery dataset -> PostgreSQL schema
    schema_map = {
        "macro_core": "core",
        "macro_mart": "mart",
        "macro_ops": "ops"
    }

    for bq_dataset, pg_schema in schema_map.items():
        dataset_dir = INPUT_DIR / bq_dataset

        if not dataset_dir.exists():
            print(f"\nSkipping {bq_dataset} (directory not found)")
            continue

        print(f"\nSchema: {pg_schema}")
        print("-" * 60)

        for csv_file in dataset_dir.glob("*.csv"):
            table_name = csv_file.stem
            rows = import_csv_to_table(conn, pg_schema, table_name, csv_file)
            total_rows += rows

    # Close connection
    conn.close()

    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("Import Complete!")
    print(f"Total rows imported: {total_rows:,}")
    print(f"Duration: {duration:.2f} seconds")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify data integrity")
    print("2. Update API configuration to use PostgreSQL")
    print("3. Test API endpoints")


if __name__ == "__main__":
    main()
