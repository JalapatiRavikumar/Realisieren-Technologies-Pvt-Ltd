# AI Usage Disclosure & Verification Report

This document transparently details the utilization of Artificial Intelligence tooling during the conception, architecture, development, testing, and documentation of the **Multi-Source Web Scraping & Data Consolidation Pipeline**.

---

## 1. AI Tools Used

- **AI Assistant**: Antigravity IDE Agentic Coding Assistant (powered by Google DeepMind advanced reasoning models).
- **Environment**: Local Windows development environment with integrated terminal execution and diagnostic tools.

---

## 2. Purpose of AI Assistance

AI tooling was utilized across the following domains:

1. **Architecture Design**: Drafting a clean, modular package structure (`scrapers`, `models`, `processing`, `pipeline`, `utils`, `tests`) adhering to Single Responsibility and Open/Closed design principles.
2. **HTML Parsing & Scraper Implementation**: Formulating robust CSS selectors for `Books to Scrape` and `Quotes to Scrape` (e.g. handling word ratings such as `'star-rating Three'`, extracting full titles from `<a title="...">`, extracting comma-separated tags).
3. **Data Quality & Normalization Primitives**: Generating regex patterns for stripping non-numeric currency symbols (`£`, `Â£`, `$`, `€`) and zero-width unicode characters.
4. **Test Case Fixture Generation**: Authoring comprehensive test fixtures and mocked HTML responses for dynamic pagination, schema validation, and deduplication logic without live network dependencies.
5. **Interview Preparation & Documentation**: Structuring comprehensive technical explanations in `INTERVIEW_NOTES.md` and `README.md`.

---

## 3. Representative Prompts Used

The following representative prompts reflect the guidance provided during the development session:

- *"Design a reusable BaseScraper class using requests.Session, urllib3 Retry, exponential backoff, custom User-Agent, and a clean context manager interface."*
- *"Implement dynamic pagination for Books to Scrape and Quotes to Scrape where the scraper queries li.next a and resolves relative URLs with urljoin without hardcoding any page numbers."*
- *"Create a unified dataclass ScrapedRecord capable of representing both books and quotes without fabricating missing attributes, using None as the standard missing value."*
- *"Write unit tests with pytest testing text normalization, price parsing (handling £ and Â£ artifacts), word-to-integer rating conversions, and deduplication key generation."*
- *"Generate an interview preparation guide answering 29+ core engineering questions covering scraping reliability, rate limiting, deduplication, incremental crawling, and database scaling."*

---

## 4. AI-Assisted Files

The following files received AI assistance during scaffolding and implementation:

| File Path | Description of AI Assistance |
|---|---|
| `config.py` | Centralized constants, paths, and HTTP configuration parameters |
| `models/record.py` | `ScrapedRecord` dataclass definition with serialization helpers |
| `scrapers/base_scraper.py` | Reusable HTTP session wrapper with backoff and error handling |
| `scrapers/books_scraper.py` | Books HTML extractor with dynamic pagination |
| `scrapers/quotes_scraper.py` | Quotes HTML extractor with tag extraction and dynamic pagination |
| `processing/cleaning.py` | Normalizers for text, price, rating, tags, URLs, and missing values |
| `processing/validation.py` | Quality gate rules and `ValidationResult` dataclass |
| `processing/deduplication.py` | Deterministic duplicate key generator and deduplication engine |
| `pipeline/pipeline.py` | End-to-end orchestrator with fault isolation and metrics tracking |
| `utils/http.py` | Session factory, retry adapters, and URL validation helpers |
| `utils/helpers.py` | CSV exporter, JSON serializer, and UTC timestamp utilities |
| `utils/logging_config.py` | Structured dual console and file logging setup |
| `main.py` | CLI interface and summary console formatting |
| `tests/test_cleaning.py` | 38 parameterized test cases for normalizers |
| `tests/test_validation.py` | 9 test cases verifying schema constraints and rejection reasons |
| `tests/test_deduplication.py` | 4 test cases testing duplicate detection and cross-source isolation |
| `tests/test_scrapers.py` | Mocked unit tests for HTML extraction and dynamic pagination |
| `README.md` | Comprehensive architectural and user documentation |
| `INTERVIEW_NOTES.md` | In-depth technical interview questions and answers |

---

## 5. Human Review and Engineering Decisions

All AI-generated code underwent human review and manual validation:

1. **Character Encoding Verification**:
   - Initial tests identified Windows terminal `cp1252` encoding exceptions when printing quotes containing curly quotation marks (`“`, `”`) or arrows (`→`).
   - *Resolution*: Explicitly configured UTF-8 encoding across file writers (`encoding="utf-8"`), CSV outputs, and file loggers.
2. **Missing Value URL Normalization**:
   - The initial AI test fixture expected `normalize_url("", "https://example.com")` to return `"https://example.com"`.
   - *Review & Fix*: Verified that an empty or missing string `""` represents an absent URL and should strictly return `None` to prevent invalid URL generation. The test was aligned accordingly.
3. **Detail Page Crawl Optimization**:
   - Scraped books listing pages directly for title, price, rating, and availability to avoid 1,000 extra HTTP requests for description/category during default runs, keeping full execution under 46 seconds while supporting on-demand detail crawls via `CONFIG.FETCH_BOOK_DETAILS`.

---

## 6. Incorrect AI Suggestions & Corrections

- **Issue**: An initial draft of the deduplication key did not prefix the source identifier into the hash key, creating a theoretical collision risk if a book title happened to match a quote text identically.
- **Correction**: Updated `generate_duplicate_key` to explicitly incorporate `norm_source` as the primary key component (`f"{norm_source}|{norm_name}|{norm_url}"`), guaranteeing complete cross-source separation.
- **Summary**: *No significant incorrect AI-generated implementation was retained in the final solution.*

---

## 7. Verification & Testing

The solution was verified through empirical testing:

1. **Automated Unit Testing**:
   - Executed `pytest -v` across the entire test suite.
   - **Result**: `83 passed in 0.48s` (100% pass rate).
2. **Live Integration Run**:
   - Executed `python main.py` against both live target websites (`https://books.toscrape.com/` and `https://quotes.toscrape.com/`).
   - **Result**:
     - Books dynamically paginated across 50 pages $\rightarrow$ 1,000 records extracted.
     - Quotes dynamically paginated across 10 pages $\rightarrow$ 100 records extracted.
     - Total raw records: 1,100.
     - Total clean records: 1,100.
     - Validation rejections: 0.
     - Duplicates detected: 0.
     - Total execution time: 45.73s.
     - Generated `output/final_dataset.csv` (1,102 lines, 228 KB) and `output/summary_report.json` with accurate metrics.
3. **Log & File Audit**:
   - Verified that `logs/scraper.log` recorded every request, pagination step, and summary output cleanly without unhandled exceptions.
