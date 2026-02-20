#!/usr/bin/env python3
"""
Export data from BigQuery to CSV files for PostgreSQL migration
"""
import os
import sys
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime

# GCP Configuration
PROJECT_ID = "gen-lang-client-0815236933"
DATASETS = {
    "macro_core": ["dim_series", "fact_observations"],
    "macro_mart": ["v_latest_snapshot"],
    "macro_ops": ["etl_runs"]
}

OUTPUT_DIR = Path("./migration_data")


def export_table_to_csv(client: bigquery.Client, dataset: str, table: str, output_dir: Path):
    """Export a BigQuery table to CSV"""
    full_table_id = f"{PROJECT_ID}.{dataset}.{table}"

    print(f"Exporting {full_table_id}...")

    # Create output directory
    table_dir = output_dir / dataset
    table_dir.mkdir(parents=True, exist_ok=True)

    # Query all data
    query = f"SELECT * FROM `{full_table_id}`"

    try:
        df = client.query(query).to_dataframe()

        # Save to CSV
        csv_path = table_dir / f"{table}.csv"
        df.to_csv(csv_path, index=False)

        print(f"  ✓ Exported {len(df)} rows to {csv_path}")
        return len(df)

    except Exception as e:
        print(f"  ✗ Error exporting {full_table_id}: {str(e)}")
        return 0


def main():
    """Main export function"""
    print("=" * 60)
    print("BigQuery to PostgreSQL Migration - Data Export")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Output: {OUTPUT_DIR.absolute()}")
    print()

    # Initialize BigQuery client
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print("✓ Connected to BigQuery")
    except Exception as e:
        print(f"✗ Failed to connect to BigQuery: {str(e)}")
        print("\nMake sure GOOGLE_APPLICATION_CREDENTIALS is set:")
        print("  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Export all tables
    total_rows = 0
    start_time = datetime.now()

    for dataset, tables in DATASETS.items():
        print(f"\nDataset: {dataset}")
        print("-" * 60)

        for table in tables:
            rows = export_table_to_csv(client, dataset, table, OUTPUT_DIR)
            total_rows += rows

    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("Export Complete!")
    print(f"Total rows exported: {total_rows:,}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the exported CSV files")
    print("2. Run the PostgreSQL initialization script")
    print("3. Import data using import_to_postgres.py")


if __name__ == "__main__":
    main()
