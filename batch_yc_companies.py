"""
Batch processing script for YC Companies database
Processes companies in batches of 25, respecting Apollo's 200 requests/hour rate limit
"""

import pandas as pd
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from sourcing_workflow import SourcingWorkflow
from models.contact import PersonaType


class YCBatchProcessor:
    """
    Processes YC companies in batches with rate limiting
    - Batch size: 25 companies
    - Rate limit: 200 requests per hour (Apollo API limit)
    - Automatically resumes from last processed batch
    """

    def __init__(
        self,
        database_path: str = "databases/YC_COMPANIES.csv",
        progress_file: str = "batch_progress.json",
        batch_size: int = 25,
        max_requests_per_hour: int = 200
    ):
        self.database_path = database_path
        self.progress_file = progress_file
        self.batch_size = batch_size
        self.max_requests_per_hour = max_requests_per_hour
        self.workflow = SourcingWorkflow()

        # Load database
        self.df = pd.read_csv(database_path)
        self.company_col = self._find_company_column()
        print(f"📊 Loaded {len(self.df)} companies from {database_path}")
        print(f"🏢 Company column: {self.company_col}")

        # Load or initialize progress
        self.progress = self._load_progress()

    def _find_company_column(self) -> str:
        """Find the company name column in the CSV"""
        # Look for 'name' or 'company' in column names
        for col in self.df.columns:
            if 'name' in col.lower() and 'organization' not in col.lower():
                return col
        # Default to first column
        return self.df.columns[0]

    def _load_progress(self) -> dict:
        """Load progress from file or create new"""
        if Path(self.progress_file).exists():
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
                print(f"📂 Loaded progress: {progress['batches_completed']} batches completed, {progress['total_processed']} companies processed")
                return progress
        else:
            return {
                "last_batch_index": 0,
                "batches_completed": 0,
                "total_processed": 0,
                "last_run_time": None,
                "requests_this_hour": 0,
                "hour_start_time": None,
                "completed_companies": []
            }

    def _save_progress(self):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
        print(f"💾 Progress saved: {self.progress['batches_completed']} batches completed")

    def _wait_for_rate_limit(self):
        """Wait if we've hit the hourly rate limit"""
        # Reset counter if an hour has passed
        if self.progress['hour_start_time']:
            hour_start = datetime.fromisoformat(self.progress['hour_start_time'])
            now = datetime.now()
            if now - hour_start >= timedelta(hours=1):
                print("⏰ Hour elapsed, resetting rate limit counter")
                self.progress['requests_this_hour'] = 0
                self.progress['hour_start_time'] = now.isoformat()
                self._save_progress()
        else:
            self.progress['hour_start_time'] = datetime.now().isoformat()

        # Check if we need to wait
        if self.progress['requests_this_hour'] >= self.max_requests_per_hour:
            hour_start = datetime.fromisoformat(self.progress['hour_start_time'])
            elapsed = datetime.now() - hour_start
            wait_time = timedelta(hours=1) - elapsed

            if wait_time.total_seconds() > 0:
                print(f"⏸️  Rate limit reached ({self.max_requests_per_hour} requests/hour)")
                print(f"⏳ Waiting {int(wait_time.total_seconds() / 60)} minutes until next batch...")
                time.sleep(wait_time.total_seconds())
scrolllockscrolllock
                # Reset counter after waiting
                self.progress['requests_this_hour'] = 0
                self.progress['hour_start_time'] = datetime.now().isoformat()
                self._save_progress()

    def process_batch(
        self,
        batch_companies: List[str],
        batch_number: int,
        contacts_per_persona: int = 100,
        verified_only: bool = False
    ):
        """Process a single batch of companies"""
        print(f"\n{'='*60}")
        print(f"🚀 BATCH {batch_number}")
        print(f"📋 Companies in batch: {len(batch_companies)}")
        print(f"{'='*60}\n")

        for company in batch_companies:
            print(f"  • {company}")

        # Check rate limit before processing
        self._wait_for_rate_limit()

        # Search for Startup Career Fair persona
        persona = PersonaType.STARTUP_CAREER_FAIR

        print(f"\n🔍 Searching {persona.value} contacts...")
        print(f"   Requesting {contacts_per_persona} contacts per persona")
        print(f"   Verified only: {verified_only}")

        try:
            contacts = self.workflow.search_by_persona(
                persona=persona,
                organization_names=batch_companies,
                max_contacts=contacts_per_persona,
                verified_only=verified_only
            )

            print(f"✅ Found {len(contacts)} contacts from batch")

            # Export results for this batch
            from utils.spreadsheet_generator import export_by_persona

            output_dir = f"exports/yc_batch_{batch_number}"
            files = export_by_persona(
                contacts=contacts,
                output_dir=output_dir,
                max_per_file=200,
                file_format="csv"
            )

            print(f"📊 Exported to: {output_dir}")
            print(f"   Files: {sum(len(f) for f in files.values())} file(s)")

            # Update progress
            self.progress['requests_this_hour'] += len(batch_companies)
            self.progress['completed_companies'].extend(batch_companies)

            return len(contacts)

        except Exception as e:
            print(f"❌ Error processing batch: {str(e)}")
            raise

    def run(
        self,
        contacts_per_persona: int = 100,
        verified_only: bool = False,
        max_batches: int = None
    ):
        """
        Run the batch processing

        Args:
            contacts_per_persona: Number of contacts to fetch per persona
            verified_only: Only fetch verified profiles
            max_batches: Maximum number of batches to process (None = all)
        """
        # Get all companies
        all_companies = self.df[self.company_col].dropna().tolist()

        # Filter out already processed companies
        remaining_companies = [
            c for c in all_companies
            if c not in self.progress['completed_companies']
        ]

        print(f"\n{'='*60}")
        print(f"🎯 BATCH PROCESSING START")
        print(f"{'='*60}")
        print(f"📊 Total companies: {len(all_companies)}")
        print(f"✅ Already processed: {len(self.progress['completed_companies'])}")
        print(f"⏳ Remaining: {len(remaining_companies)}")
        print(f"📦 Batch size: {self.batch_size}")
        print(f"⏱️  Rate limit: {self.max_requests_per_hour} requests/hour")
        print(f"{'='*60}\n")

        if not remaining_companies:
            print("✅ All companies have been processed!")
            return

        # Calculate number of batches
        total_batches = (len(remaining_companies) + self.batch_size - 1) // self.batch_size

        if max_batches:
            total_batches = min(total_batches, max_batches)
            print(f"🎯 Processing maximum {max_batches} batches")

        print(f"📦 Total batches to process: {total_batches}\n")

        # Process batches
        batches_processed = 0
        total_contacts_found = 0

        try:
            for i in range(total_batches):
                start_idx = i * self.batch_size
                end_idx = min(start_idx + self.batch_size, len(remaining_companies))
                batch_companies = remaining_companies[start_idx:end_idx]

                batch_number = self.progress['batches_completed'] + i + 1

                contacts_found = self.process_batch(
                    batch_companies=batch_companies,
                    batch_number=batch_number,
                    contacts_per_persona=contacts_per_persona,
                    verified_only=verified_only
                )

                # Update progress
                self.progress['last_batch_index'] = batch_number
                self.progress['batches_completed'] = batch_number
                self.progress['total_processed'] = len(self.progress['completed_companies'])
                self.progress['last_run_time'] = datetime.now().isoformat()
                self._save_progress()

                batches_processed += 1
                total_contacts_found += contacts_found

                print(f"\n✅ Batch {batch_number} completed!")
                print(f"📈 Progress: {self.progress['total_processed']}/{len(all_companies)} companies")
                print(f"📊 Total contacts found so far: {total_contacts_found}")

                # Small delay between batches
                if i < total_batches - 1:
                    print(f"\n⏸️  Waiting 5 seconds before next batch...")
                    time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n⏸️  Processing interrupted by user")
            print(f"✅ Completed {batches_processed} batches")
            print(f"💾 Progress has been saved")
            print(f"🔄 Run the script again to resume from where you left off")

        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            print(f"💾 Progress has been saved")
            print(f"🔄 Run the script again to resume from where you left off")
            raise

        else:
            print(f"\n{'='*60}")
            print(f"🎉 BATCH PROCESSING COMPLETE!")
            print(f"{'='*60}")
            print(f"✅ Batches processed: {batches_processed}")
            print(f"✅ Companies processed: {self.progress['total_processed']}")
            print(f"✅ Total contacts found: {total_contacts_found}")
            print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process YC companies for Startup Career Fair"
    )
    parser.add_argument(
        "--database",
        default="databases/YC_COMPANIES.csv",
        help="Path to YC companies CSV file"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Number of companies per batch (default: 25)"
    )
    parser.add_argument(
        "--contacts-per-persona",
        type=int,
        default=100,
        help="Number of contacts to fetch per persona (default: 100)"
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Maximum number of batches to process (default: all)"
    )
    parser.add_argument(
        "--verified-only",
        action="store_true",
        help="Only fetch verified profiles"
    )
    parser.add_argument(
        "--progress-file",
        default="batch_progress.json",
        help="Progress tracking file (default: batch_progress.json)"
    )

    args = parser.parse_args()

    # Create processor
    processor = YCBatchProcessor(
        database_path=args.database,
        progress_file=args.progress_file,
        batch_size=args.batch_size,
        max_requests_per_hour=200
    )

    # Run processing
    processor.run(
        contacts_per_persona=args.contacts_per_persona,
        verified_only=args.verified_only,
        max_batches=args.max_batches
    )


if __name__ == "__main__":
    main()
