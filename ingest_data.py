"""
Data Ingestion Script
Ingests activity logs into database
"""
import argparse
from src.parsers.activity_parser import ActivityParser
from src.database.database import Database
from src.analysis_pipeline import AnalysisPipeline
from src.models.configuration import Configuration


def main():
    parser = argparse.ArgumentParser(description="Ingest activity logs into Drishti")
    parser.add_argument("file", help="Activity log file path")
    parser.add_argument("--format", choices=["json", "csv", "syslog"], help="File format (auto-detect if not specified)")
    parser.add_argument("--db", default="intent_drift_ai.db", help="Database path")
    args = parser.parse_args()
    
    print(f"[<-] Ingesting data from: {args.file}")
    
    # Parse activities
    print("[-] Parsing activities...")
    activities = ActivityParser.parse_file(args.file, args.format)
    print(f"[OK] Parsed {len(activities):,} activities")
    
    # Initialize database and pipeline
    print("[DB] Connecting to database...")
    config = Configuration.default()
    db = Database(args.db, encryption_enabled=True)
    pipeline = AnalysisPipeline(config, db)
    
    # Ingest activities
    print("[>>] Ingesting into database...")
    result = pipeline.ingest_activities(activities)
    
    print(f"[OK] Ingestion complete!")
    print(f"   Activities ingested: {result['activities_ingested']:,}")
    print(f"   Duration: {result['duration_seconds']:.2f} seconds")
    print(f"   Rate: {result['rate_per_second']:.0f} activities/second")


if __name__ == "__main__":
    main()
