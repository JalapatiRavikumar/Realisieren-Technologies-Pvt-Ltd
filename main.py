"""
Main CLI Entry Point for Web Scraping Pipeline.

Usage:
    python main.py
    python main.py --source all
    python main.py --source books
    python main.py --source quotes
    python main.py --max-pages 2
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import CONFIG
from pipeline.pipeline import Pipeline
from utils.logging_config import setup_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-Source Web Scraping and Data Consolidation Pipeline"
    )
    parser.add_argument(
        "--source",
        choices=["all", "books", "quotes"],
        default="all",
        help="Target data source(s) to scrape (default: all)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional upper limit on pages to scrape per source (default: all pages)",
    )
    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_args()
    logger = setup_logger("Main")

    logger.info("Initializing scraping pipeline...")
    pipeline = Pipeline(config=CONFIG, logger=logger)

    try:
        records, result = pipeline.run(
            source_filter=args.source,
            max_pages=args.max_pages,
        )

        books_count = result.sources.get(CONFIG.SOURCE_BOOKS, {}).get("records_collected", 0)
        quotes_count = result.sources.get(CONFIG.SOURCE_QUOTES, {}).get("records_collected", 0)

        print("\n" + "=" * 50)
        print("Scraping completed.")
        print(f"Books collected: {books_count}")
        print(f"Quotes collected: {quotes_count}")
        print(f"Clean records: {result.total_records_after_cleaning}")
        print(f"Rejected records: {result.total_records_rejected}")
        print(f"Duplicates: {result.total_duplicates_detected}")
        print(f"Final records: {result.final_record_count}")
        print(f"Execution time: {result.execution_time_seconds:.2f}s")
        print("Output:")
        print(f"  {CONFIG.CSV_OUTPUT_PATH.relative_to(CONFIG.BASE_DIR)}")
        print(f"  {CONFIG.SUMMARY_JSON_PATH.relative_to(CONFIG.BASE_DIR)}")
        print("=" * 50 + "\n")

        return 0

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        return 130
    except Exception as exc:
        logger.error(f"Fatal error during pipeline execution: {exc}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
