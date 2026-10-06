# Technical Interview Notes & Architecture Q&A

This document provides concise, practical, and interview-ready answers to key technical questions regarding the architecture, design choices, error handling, testing, full-stack extension, and scaling strategies implemented in this project.

---

### 1. Why Requests + BeautifulSoup?
**Answer**:
Both target websites (`books.toscrape.com` and `quotes.toscrape.com`) serve standard server-side rendered (SSR) static HTML. `requests` combined with `BeautifulSoup4` is the most lightweight, fast, and resource-efficient Python stack for this task. It eliminates the heavy overhead, binary dependencies, memory footprint, and slow startup times associated with headless browser engines.

---

### 2. Why not Selenium or Playwright?
**Answer**:
Selenium and Playwright are intended for client-side rendered Single Page Applications (SPAs) that require a full browser JavaScript runtime (V8) to execute dynamic scripts, handle WebSockets, or emulate user events. Because our target sites do not use client-side hydration or JavaScript rendering, introducing Selenium/Playwright would introduce unnecessary complexity, fragile browser driver dependencies, high CPU/RAM consumption, and 10x slower execution speeds without any technical benefit.

---

### 3. How does pagination work?
**Answer**:
Pagination is completely dynamic and discovery-driven. The scraper begins at the root catalog URL. On each page, after extracting items, it queries the DOM for the next page link (`li.next a`). If the element is present, the scraper extracts its relative `href` attribute, resolves it into an absolute URL using `urllib.parse.urljoin`, and requests the next page. When `li.next a` is no longer found in the DOM, the pagination loop gracefully terminates.

---

### 4. How do you detect the next page?
**Answer**:
Using the CSS selector `li.next a`:
- On `Books to Scrape`: `<li class="next"><a href="catalogue/page-2.html">next</a></li>` (or relative `page-3.html` on subsequent pages).
- On `Quotes to Scrape`: `<li class="next"><a href="/page/2/">Next</a></li>`.
By evaluating `soup.select_one("li.next a")` and checking if an element exists with a non-empty `href`, we avoid hardcoded page counts like `range(1, 51)`.

---

### 5. How do you handle missing HTML elements?
**Answer**:
We use defensive selector extraction with `.select_one()`, `.get()`, and conditional guards:
```python
title_tag = pod.select_one("h3 a")
title = (title_tag.get("title") or title_tag.get_text(strip=True)) if title_tag else None
```
If an optional element (such as tags, description, or author link) is missing from the DOM, the extractor assigns `None` instead of throwing an `AttributeError` or `IndexError`. If a mandatory element is absent, the scraper logs a warning and skips the corrupted item without crashing the entire page or pipeline.

---

### 6. How do you handle connection failures?
**Answer**:
Connection drops, DNS resolution errors, and socket resets are caught via `requests.exceptions.RequestException` and `requests.exceptions.Timeout`. The `BaseScraper` wraps network operations inside a retry loop with exponential backoff (e.g. 1.5s, 3.0s, 6.0s). If a connection error persists beyond the maximum retry threshold (`MAX_RETRIES = 3`), it logs an error and returns `None`, allowing the caller to halt that source's pagination safely without crashing the remaining pipeline.

---

### 7. How does retry work?
**Answer**:
We implement a two-layer retry architecture:
1. **Transport Layer**: `urllib3.util.Retry` attached to `requests.adapters.HTTPAdapter` manages automatic TCP connection and idempotent GET retries within `requests.Session`.
2. **Application Layer**: A custom retry loop in `BaseScraper.fetch()` with exponential backoff (`delay = BACKOFF_FACTOR * (2 ** attempt)`) to handle transient server-side failures and rate-limiting signals.

---

### 8. Which HTTP errors should be retried?
**Answer**:
- **Retryable (Transient Errors)**:
  - `429 Too Many Requests` (rate limited — wait and retry with backoff).
  - `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` (temporary upstream server overload).
- **Non-Retryable (Permanent Client Errors)**:
  - `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `410 Gone`.
  Retrying a 404 or 403 wastes bandwidth and increases server strain because the resource permanently does not exist or access is forbidden.

---

### 9. How do you normalize prices?
**Answer**:
Raw price strings (e.g. `£51.77`, `Â£51.77`, `$19.99`) often contain currency symbols, HTML entity encoding artifacts, or whitespace. Our `parse_price()` function uses regular expression extraction:
```python
match = re.search(r"(\d+(?:\.\d+)?)", val_str)
```
This extracts the exact numeric substring, converts it to a standard `float`, and rounds it to 2 decimal places. Missing, unparseable, or invalid inputs cleanly return `None`.

---

### 10. How do you normalize ratings?
**Answer**:
On Books to Scrape, ratings are stored as CSS classes on `<p class="star-rating Three">`. The scraper extracts the class name (e.g. `"Three"`), and the `parse_rating()` function maps it through a lookup dictionary:
```python
RATING_WORD_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
```
It also validates that numeric ratings fall strictly within the integer range `1 <= rating <= 5`. Any out-of-bounds or unrecognized values resolve to `None`.

---

### 11. How does validation work?
**Answer**:
Validation acts as a quality gate before output generation. The `validate_record()` function inspects each cleaned record:
- **Mandatory Fields**: Confirms `source`, `source_url`, and `name_or_title` are non-empty strings.
- **URL Schema**: Validates that `source_url` contains a valid HTTP/HTTPS scheme and network location.
- **Range & Type Bounds**: Ensures `price >= 0` and `1 <= rating <= 5` whenever present.
- **Rejection Logging**: If validation fails, `ValidationResult.is_valid` is set to `False`, the specific errors are recorded, and the rejected item is logged in `summary_report.json` with its rejection reason. Missing optional fields (`None`) are permitted and do not trigger rejections.

---

### 12. How does deduplication work?
**Answer**:
Deduplication is performed in `processing/deduplication.py` using deterministic hash keys. Each record passes through `generate_duplicate_key()`. The pipeline iterates over records, tracking seen keys in an in-memory set. The first occurrence is preserved, while subsequent identical records are appended to a duplicate tracking list to update audit metrics.

---

### 13. Why normalize before deduplication?
**Answer**:
Raw scraped text frequently exhibits subtle variations such as trailing whitespace, different casing, or multi-space formatting (e.g. `"A Light in the Attic"`, `" a light in the attic "`, `"A LIGHT IN THE ATTIC"`). If deduplication occurred prior to normalization, these identical entities would produce different hashes and slip through as false negatives. Normalizing first ensures deterministic, consistent key evaluation.

---

### 14. Why is source included in duplicate keys?
**Answer**:
To prevent cross-source key collisions. A book and a quote may share identical titles (e.g., `"To Kill a Mockingbird"` as a book title on Books to Scrape vs. a quote reference on Quotes to Scrape). Prefixing the key with `source` (`f"{norm_source}|{norm_name}|..."`) guarantees that distinct data entities from different sources remain isolated.

---

### 15. Why use None for missing values?
**Answer**:
Using Python's native `None` creates a single, unambiguous representation of missing data in memory. Mixing arbitrary sentinel strings like `"N/A"`, `"unknown"`, `"-"`, or `"null"` corrupts downstream data analytics, causes type validation errors (e.g., expecting a float price but receiving a string `"N/A"`), and violates database NULL conventions. In CSV export, `None` cleanly translates to empty fields (`""`).

---

### 16. What happens if one source fails?
**Answer**:
The pipeline implements source-level fault isolation. The extraction loop wraps each scraper in independent `try...except` blocks. If Quotes to Scrape crashes due to a network outage or server error, Books to Scrape records are fully preserved, cleaned, validated, deduplicated, and exported to CSV. The error details are captured and recorded under the `"errors"` key in `summary_report.json`.

---

### 17. How did you test the scrapers?
**Answer**:
We developed 90 automated unit and integration tests with `pytest`:
- Unit tests for string cleaning, regex price extraction, rating word mappings, URL normalization, and tag deduplication.
- Schema validation tests checking mandatory fields, negative prices, invalid ratings, and URL syntax.
- Scraper tests using mocked HTML DOM fixtures (`unittest.mock.patch.object`) to test book/quote parsing, dynamic multi-page pagination, and HTTP retry logic without making live network requests.
- Integration tests for FastAPI endpoints verifying status responses, search queries, pagination, and download endpoints.

---

### 18. Why mock HTTP responses in tests?
**Answer**:
- **Determinism**: Live websites can change their content, experience downtime, or rate-limit test runners.
- **Speed & Isolation**: Mocked tests run offline in under 0.5 seconds without internet connectivity.
- **Edge Case Simulation**: Allows simulating edge cases (e.g., HTTP 500 crashes, network timeouts, malformed HTML, missing tags) that cannot be easily triggered against live production servers.

---

### 19. Why React for the frontend?
**Answer**:
React provides a component-driven, responsive UI paradigm that makes building interactive dashboards straightforward. It allows dynamic search filtering, instant source switching, pagination, and real-time status updates without full page reloads.

---

### 20. Why FastAPI for the backend?
**Answer**:
FastAPI is a modern, high-performance Python web framework with native async support, automatic OpenAPI documentation (`/docs`), Pydantic validation, and seamless integration with existing Python codebases. It allows us to expose the core scraping pipeline as REST endpoints in just a few lines of code without altering the underlying scraping logic.

---

### 21. Why are CSV and JSON the sources of truth?
**Answer**:
The assignment specification explicitly mandates CSV and JSON outputs. By having the FastAPI backend query `output/final_dataset.csv` and `output/summary_report.json` directly, we maintain a clear, single source of truth without introducing unnecessary database dependencies or fake in-memory stores.

---

### 22. Why not scrape directly from React / Frontend?
**Answer**:
Scraping belongs strictly on the backend for several reasons:
1. **CORS Restrictions**: Browsers enforce Same-Origin Policies, preventing JavaScript from fetching cross-origin HTML without permissive server headers or CORS proxies.
2. **Performance & Memory**: Heavy DOM parsing and regex normalization are CPU-intensive operations best handled by server processes.
3. **Security & IP Management**: Backend scrapers can manage session pools, rotate User-Agents, apply polite delays, and protect scraping strategies from client inspection.
4. **Separation of Concerns**: The frontend remains solely responsible for presentation, while data extraction and normalization stay in the domain layer.

---

### 23. Why not add a relational database (e.g., PostgreSQL/MySQL)?
**Answer**:
For the scope of this take-home assignment, CSV and JSON files fully satisfy all requirements with zero external infrastructure overhead. Introducing a database would require Docker containers, migration scripts (Alembic), and connection pool configurations that increase deployment complexity without adding functional value. In a production enterprise system, migrating the CSV layer to PostgreSQL with composite unique indexes and an ORM (SQLAlchemy) would be the next logical step.

---

### 24. How is concurrency handled when clicking "Run Scraper"?
**Answer**:
In `backend/services/scraper_service.py`, we use a thread-safe in-memory execution lock (`threading.Lock`). When a user triggers `/api/scrape`, the service attempts non-blocking lock acquisition (`acquire(blocking=False)`). If a scraping job is already active, the backend immediately responds with `{"status": "running", "message": "Scraper is already running."}` rather than starting parallel colliding jobs. In a distributed multi-instance production environment, this would be upgraded to a Redis distributed lock or a Celery task queue.

---

### 25. How would you productionize this entire architecture?
**Answer**:
1. **Containerization**: Use a multi-stage Docker setup (FastAPI container + Nginx serving React static assets).
2. **Task Queue**: Move scraping jobs to Celery or Temporal workers backed by Redis/RabbitMQ to handle long-running runs asynchronously.
3. **Database & Object Storage**: Store structured records in PostgreSQL and raw HTML snapshots in AWS S3 or Google Cloud Storage.
4. **CI/CD & Monitoring**: Automated GitHub Actions running pytest, and Prometheus/Grafana metrics monitoring response latencies, success rates, and extraction volumes.

---

### 26. What did AI help you with?
**Answer**:
AI assisted in scaffolding the initial modular directory structure, generating regex patterns for price and whitespace sanitization, creating parameterized pytest test cases with mocked HTML fixtures, drafting the Tailwind CSS dashboard components, and documenting architecture details.

---

### 27. What did you personally verify and test?
**Answer**:
- Executed `pytest` locally and verified all 90 test assertions pass.
- Ran `python main.py` against both live target websites, verifying that dynamic pagination successfully retrieved 1,000 books across 50 pages and 100 quotes across 10 pages in 45.73 seconds.
- Verified FastAPI backend endpoints (`/api/dashboard`, `/api/records`, `/api/scrape`, `/api/download/csv`, `/api/download/summary`) with automated tests and live requests.
- Built and validated the React + Vite frontend (`npm run build`), confirming clean compilation and responsive UI rendering.
- Inspected the generated `output/final_dataset.csv` (1,102 rows) and `output/summary_report.json` to ensure clean UTF-8 encoding, correct headers, and accurate calculated metrics.

---

### 28. How would you handle website HTML structural changes?
**Answer**:
- **Selector Fallbacks**: Use flexible, semantic fallback selectors (e.g. `article.product_pod h3 a` falling back to `h3 a`).
- **Contract / Schema Tests**: Run daily automated synthetic tests asserting that expected CSS selectors match at least one element on sample live pages.
- **Alerting on Zero Extractions**: If a page returns 0 extracted items while returning HTTP 200, raise an alert immediately.

---

### 29. How would you prevent duplicate records across repeated pipeline runs?
**Answer**:
By introducing persistent deduplication backed by a primary key or unique index in a relational database (PostgreSQL/SQLite) or a persistent key-value store (Redis). When scraping in subsequent runs, the pipeline checks the persistent store before inserting, either updating existing records with fresh timestamps/prices (upsert) or ignoring already ingested identical records.
