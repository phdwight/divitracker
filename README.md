# DiviTracker 💰

A Flask application for tracking dividend income from your investments. Calculate annualized dividend yields and monitor your passive income portfolio.

## Features

- **Investment Management**: Add, edit, and delete investments with ticker symbols, current market values, and a split-pane **Live Preview** card when adding or topping up holdings
- **Paper Gain / Loss Tracking**: View unrealized paper gain or loss (amount and percentage) alongside Currently Invested on the dashboard, investment detail pages, and Add Investment live preview
- **Dividend Tracking**: Record dividends with monthly, quarterly, semi-annual, or yearly frequency and real-time annualized yield preview
- **Yield Calculation**: Automatic computation of actual and projected annualized dividend yields (`actual | projected`)
- **Yield Breakdown Page**: Detailed, printable computation breakdown for yield calculations (`/reports/yield-breakdown`)
- **Dividend Graph**: Interactive Chart.js bar chart and cumulative line graph with clickable period breakdown modal, 4 summary KPI cards, collapsible period data table, and filters by year and investment (`/reports/dividends-chart`)
- **Portfolio Dashboard**: Unified topbar with inline year pills, 3 KPI summary cards (`Annualized Yield` hero card, `Currently Invested`, `Dividends Received`), compact holdings table with instant search (`?q=`), 5 sortable columns (`?sort=&dir=`), and dismissible filter chips
- **Configurable Sidebar Navigation**: Vertical icon+label navigation sidebar (`Dashboard`, `Graph`, `+ New` quick-create popover, `Settings`) docked on the left by default and configurable to the right side via the Settings page or the quick sidebar toggle button (adapting into a fixed bottom tab bar on mobile)
- **Consolidated View & Privacy Menu**: Unified topbar `View` popover menu consolidating `Hide amounts` (privacy blur with hover-to-peek, persisted in `localStorage`), `Hide zero dividends`, `Hide zero investments`, and `Show Cumulative Line` chart toggle with an active count badge
- **Forest & Amber Dark Theme**: High-contrast dark theme crafted from a 4-color palette — Deep Forest Green (`#09251C`, ~40% canvas/surfaces), Burnt Amber (`#A55704`, ~26% brand & interactive accents), Warm Sand (`#F3D2AF`, ~18% secondary highlights, borders & chart cumulative line), and Soft Cream (`#F8EADC`, ~15% WCAG AAA primary typography)
- **Pagination**: Configurable items per page (5–100) for dashboard holdings and investment dividend history views
- **Historical Tracking**: Track investment amount at time of dividend for accurate multi-period yield calculations
- **Timezone Support**: Configurable timezone for accurate local time display (default: GMT+8)
- **Settings Page**: Sectioned 2-column configuration for currency (16 quick-select presets), number formatting, pagination, timezone, sidebar position (`left`/`right`), and one-click SQLite database backup download/restore
- **RESTful URLs**: Clean URL structure following best practices (e.g., `/investments/new`, `/dividends/<id>/edit`, `/settings/sidebar-position`)
- **Code Quality**: Checked with `black`, `isort`, `flake8`, `pylint`, `mypy`, and `djlint` (Jinja2-aware HTML linter)

## Architecture

```
divitracker/
├── app/                      # Application package
│   ├── __init__.py          # Package marker
│   ├── factory.py           # Application factory (create_app) & context processors
│   ├── config.py            # Environment configuration classes
│   ├── extensions.py        # Flask extensions (SQLAlchemy, Migrate)
│   ├── exceptions.py        # Custom domain exceptions
│   ├── models.py            # SQLAlchemy models (Investment, Dividend)
│   ├── settings.py          # User settings manager (currency, formatting, timezone, pagination, layout)
│   ├── utils.py             # Utility & pagination helpers
│   ├── routes/              # Blueprint routes
│   │   ├── __init__.py      # Package marker
│   │   ├── main.py          # Dashboard, search/sort, yield breakdown & dividend chart routes
│   │   ├── investments.py   # Investment CRUD & JSON autocomplete routes
│   │   ├── dividends.py     # Dividend CRUD routes
│   │   └── admin.py         # Settings, sidebar position API & DB backup/restore routes
│   └── services/            # Business logic layer
│       ├── __init__.py      # Package marker
│       ├── investment_service.py
│       ├── dividend_service.py
│       └── portfolio_service.py
├── templates/               # Jinja2 templates
│   ├── base.html            # App shell (configurable left/right sidebar, unified topbar, View popover)
│   ├── index.html           # Portfolio dashboard (KPI cards, searchable/sortable holdings table)
│   ├── add_investment.html  # Split-pane investment form with live preview card
│   ├── edit_investment.html # Edit investment form
│   ├── view_investment.html # Holding detail view & paginated dividend history
│   ├── add_dividend.html    # Record dividend form with live annualized yield preview
│   ├── edit_dividend.html   # Edit dividend form
│   ├── dividend_graph.html  # Chart.js bar + cumulative line chart & collapsible breakdown table
│   ├── yield_breakdown.html # Printable step-by-step yield calculation breakdown
│   └── errors.html          # Custom 400/403/404/500 error page
├── static/                  # Static assets (style.css, favicon.svg)
├── config/                  # User configuration (user_settings.json)
├── tests/                   # BDD test suite (pytest-bdd, 208 scenarios)
│   ├── conftest.py          # Shared test fixtures
│   ├── features/            # Gherkin feature files (12 feature suites)
│   │   ├── admin_settings.feature
│   │   ├── annual_dividends.feature
│   │   ├── dividend_recording.feature
│   │   ├── dividend_yield.feature
│   │   ├── edge_cases.feature
│   │   ├── investment_management.feature
│   │   ├── model_details.feature
│   │   ├── period_validation.feature
│   │   ├── portfolio_summary.feature
│   │   ├── user_settings.feature
│   │   ├── utility_functions.feature
│   │   └── web_routes.feature
│   └── step_defs/           # Step definitions
│       ├── shared_steps.py  # Reusable step definitions
│       └── test_*.py        # Feature-specific steps
├── .github/workflows/       # GitHub Actions CI & multi-arch Docker build workflows
├── instance/                # Instance-specific data (SQLite DB)
├── Dockerfile               # Multi-stage Docker image (Python 3.14.9-slim + Gunicorn)
├── docker-compose.yml       # Docker Compose configuration
├── pyproject.toml           # Tooling & pytest configuration
├── instructions.md          # Engineering & GenAI code generation guidelines
├── VERSION                  # Application version file
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip

**Or for Docker deployment:**
- Docker 20.10+
- Docker Compose 2.0+

### Installation (Local)

1. **Clone the repository**:
   ```bash
   cd divitracker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Open your browser** and navigate to `http://127.0.0.1:5000`

### Installation (Docker)

1. **Clone the repository**:
   ```bash
   cd divitracker
   ```

2. **Create environment file**:
   ```bash
   cat <<EOF > .env
   SECRET_KEY=your-strong-secret-key
   PORT=8050
   FLASK_ENV=production
   EOF
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker compose up -d --build
   ```

4. **Open your browser** and navigate to `http://localhost:8050` (or the `PORT` configured in `.env`, default `5000`)

#### Docker Commands

```bash
# Start the application
docker compose up -d

# View logs
docker compose logs -f

# Stop the application
docker compose down

# Rebuild after code changes
docker compose up -d --build

# View container status
docker compose ps
```

#### Data Persistence

The SQLite database is stored in a Docker volume (`divitracker_data`) that persists across container restarts. To backup your data:

```bash
# Create a backup
docker cp divitracker:/app/instance/dividends.db ./backup_dividends.db

# Restore from backup
docker cp ./backup_dividends.db divitracker:/app/instance/dividends.db
docker compose restart
```

## Usage

### Adding an Investment

1. Click **`+ New` → `New Investment`** in the sidebar navigation (or **`+ Investment`** on the dashboard)
2. Enter the investment name (or select an existing holding to top up)
3. Optionally add a ticker symbol
4. Enter the amount invested
5. Optionally enter the current market value to track paper gain or loss
6. Review the **Live Preview** card on the right (showing whether a new holding will be created or an existing one updated, along with live Total Invested, Current Market Value, and Paper Gain / Loss)
7. Click **"Save Investment"**

### Recording a Dividend

1. Click **`+ New` → `Record Dividend`** in the sidebar navigation (or **`+ Dividend`** on the dashboard / holding detail page)
2. Select the investment from the dropdown
3. Enter the dividend amount received
4. Select the frequency:
   - **Monthly**: Paid every month (×12 annually)
   - **Quarterly**: Paid every 3 months (×4 annually)
   - **Semi-Annual**: Paid every 6 months (×2 annually)
   - **Yearly**: Paid once per year
5. Optionally specify the period (month/year) and investment amount at time
6. Review the real-time **Annualized Yield Preview** box
7. Click **"Record Dividend"**

### Viewing Portfolio

The dashboard displays:
- **Unified Topbar**: Inline segmented year pills (`2026`, `2025`, ...) and a consolidated **`View`** popover menu with an active count badge:
  - **Hide amounts**: Blurs sensitive currency figures across the app (hover to peek; persisted in `localStorage`)
  - **Hide zero dividends**: Filters out holdings with zero dividends received in the selected year (`hide_zero=true` by default)
  - **Hide zero investments**: Filters out holdings with zero amount invested (`hide_zero_investments=true` by default)
- **3 KPI Summary Cards**:
  - **Annualized Yield** (hero card): Displays overall actual yield and projected yield (`Projected: X%`) and links directly to the detailed Yield Breakdown report
  - **Currently Invested**: Displays total invested capital alongside overall unrealized paper gain/loss (amount and percentage) and current market value
  - **Dividends Received (`<Year>`)**: Displays total dividends collected in the selected year and projected full-year payout
- **Holdings Table**:
  - Live search input (`?q=`) filtering by holding name or ticker symbol
  - 5 sortable columns (`Holding`, `Invested`, `Current value`, `Received <Year>`, `Yield act | proj` via `?sort=&dir=`)
  - Dismissible active filter chips and quick **`Reset`** link when search/filters are modified
  - Configurable pagination (`5` to `100` items per page) and inline row actions (`+`, `Edit`, `×`)

### Dividend Graph

Access the graph page via **"Graph"** in the sidebar navigation (`/reports/dividends-chart`) to view:
- **Unified Topbar Controls**: Inline year pills (`All`, `2026`, `2025`, ...), holding filter dropdown, and the **`View`** popover menu (`Hide amounts` and **`Show Cumulative Line`** toggles)
- **4 Summary KPI Cards**: `Total Displayed`, `Average / Period`, `Highest Period`, and `Periods w/ Payouts`
- **Interactive Chart.js Visualization**: Combined bar chart (`#C46B0B` → `#A55704` amber bars) and cumulative growth line (`#F3D2AF` warm sand line with `#F8EADC` cream points); click any bar to open a modal breakdown of individual payouts for that period
- **Collapsible Period Breakdown Table**: Expandable `<details>` table showing `Period`, `Dividends Received`, `Cumulative Total`, and `Share of Total` percentage bars

### Yield Breakdown Page

Click on the **"Annualized Yield"** hero card on the dashboard (`/reports/yield-breakdown`) to view:
- The complete yield calculation formula
- Step-by-step computation with actual values
- Per-investment breakdown showing contribution to overall yield
- Print-friendly format for record keeping

## Dividend Yield Calculation

The annualized dividend yield is calculated as:

```
Yield (%) = (Annual Dividends / Average Investment Balance) × 100
```

The **Average Investment Balance** is calculated from the investment amounts recorded at the time of each dividend during the year. This provides a more accurate yield calculation that accounts for changes in your investment balance throughout the year.

Where **Annual Dividends** is computed based on frequency:
- Monthly dividends × 12
- Quarterly dividends × 4
- Semi-annual dividends × 2
- Yearly dividends × 1

### Actual vs Projected Yield

- **Actual Yield**: Based on dividends actually received during the selected year
- **Projected Yield**: Based on the most recent dividend, projected to a full year

The dashboard shows both values in "actual | projected" format for transparency.

## Running Tests

The project uses **BDD (Behavior-Driven Development)** with pytest-bdd for human-readable test scenarios.

### Test Organization

Tests are organized by actor and domain using tags:

| Actor | Tag | Description |
|-------|-----|-------------|
| Admin | `@admin` | Administrative functions |
| User | `@user` | User-facing features |
| System | `@system` | Internal system behavior |
| Developer | `@developer` | Developer utilities |

| Domain | Tag | Features Covered |
|--------|-----|------------------|
| `@dividends` | Dividend recording, yield calculation, annual totals |
| `@investments` | Investment CRUD operations |
| `@portfolio` | Portfolio summary and dashboard |
| `@settings` | User settings and configuration |
| `@routes` | Web route navigation |
| `@models` | Data model behavior |
| `@validation` | Input validation |
| `@utilities` | Utility and pagination helper functions |
| `@edge_cases` | Edge case and boundary condition coverage |

### Running Tests

```bash
# Run all tests (208 scenarios; automatically enforces >= 80% coverage via pyproject.toml)
pytest

# Run with HTML coverage report
pytest --cov=app --cov-report=html

# Run tests by actor
pytest -m admin          # Admin tests only
pytest -m user           # User tests only
pytest -m "not system"   # Exclude system tests

# Run tests by domain
pytest -m dividends      # Dividend-related tests
pytest -m investments    # Investment-related tests

# Run specific feature file
pytest tests/step_defs/test_dividend_steps.py

# Run with verbose output
pytest -v
```

### Test Coverage

Current coverage: **95.02%** (208 BDD scenarios; minimum required threshold of **80%** enforced via `pyproject.toml`):

| Module | Coverage |
|--------|----------|
| `app/routes/dividends.py` | 100% |
| `app/services/portfolio_service.py` | 100% |
| `app/exceptions.py` | 100% |
| `app/extensions.py` | 100% |
| `app/services/investment_service.py` | 99% |
| `app/factory.py` | 97% |
| `app/models.py` | 97% |
| `app/routes/admin.py` | 97% |
| `app/settings.py` | 96% |
| `app/routes/investments.py` | 95% |
| `app/services/dividend_service.py` | 92% |
| `app/config.py` | 91% |
| `app/routes/main.py` | 90% |
| `app/utils.py` | 82% |

### Running Tests with Docker

```bash
# Build test image and run tests
docker build -t divitracker-test .
docker run --rm -e FLASK_ENV=testing divitracker-test pytest -v

# Run tests with coverage
docker run --rm -e FLASK_ENV=testing divitracker-test pytest -v --cov=app --cov-report=term-missing
```

## Linting & Static Analysis

### Python Formatting, Linting & Type Checking

The project enforces code formatting, import ordering, linting, and static type checking in CI:

```bash
# Check code formatting (Black, line-length 100)
black --check --diff app/ tests/

# Check import ordering (isort)
isort --check-only --diff app/ tests/

# Lint with flake8
flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503

# Lint with pylint
pylint app/ --rcfile=.pylintrc

# Type check with mypy
mypy app/ --config-file=mypy.ini
```

### Template Linting (HTML/Jinja2)

The project uses [djlint](https://djlint.com/) for Jinja2-aware HTML template linting:

```bash
# Install djlint
pip install djlint

# Run linting on templates
djlint templates/ --profile=jinja --lint

# Auto-format templates (optional)
djlint templates/ --profile=jinja --reformat
```

## Configuration

### User Settings (Currency, Formatting & Layout)

The application supports customizable currency, number formatting, timezone, pagination, and sidebar layout through the **Settings UI (`/settings/`)** or via `config/user_settings.json`:

**File**: `config/user_settings.json`

```json
{
    "currency": {
        "code": "PHP",
        "symbol": "₱",
        "name": "Philippine Peso"
    },
    "formatting": {
        "thousands_separator": ",",
        "decimal_separator": ".",
        "decimal_places": 2
    },
    "timezone": {
        "offset_hours": 8,
        "name": "GMT+8"
    },
    "pagination": {
        "items_per_page": 10
    },
    "layout": {
        "sidebar_position": "left"
    }
}
```

#### Layout Configuration

The `layout` setting controls where the vertical navigation sidebar is docked:
- `sidebar_position`: `"left"` (default) or `"right"`
- Can be changed in the Settings page (`/settings/`) or toggled anytime using the quick button at the bottom of the sidebar

#### Pagination Configuration

The `pagination` setting controls the default number of items per page:
- `items_per_page`: Number of items to show per page (5–100, default: 10)
- Can be overridden per-request using the page selector dropdown

#### Timezone Configuration

The `timezone` setting controls the local time displayed in reports:
- `offset_hours`: Hours offset from UTC (`-12` to `+14`, e.g., `8` for GMT+8, `-5` for EST)
- `name`: Display name shown in the UI (e.g., `"GMT+8"`, `"EST"`)

#### Available Currency Presets

| Code | Symbol | Currency Name |
|------|--------|---------------|
| PHP | ₱ | Philippine Peso (default) |
| USD | $ | US Dollar |
| EUR | € | Euro |
| GBP | £ | British Pound |
| JPY | ¥ | Japanese Yen |
| CNY | ¥ | Chinese Yuan |
| KRW | ₩ | South Korean Won |
| INR | ₹ | Indian Rupee |
| AUD | A$ | Australian Dollar |
| CAD | C$ | Canadian Dollar |
| SGD | S$ | Singapore Dollar |
| HKD | HK$ | Hong Kong Dollar |
| MYR | RM | Malaysian Ringgit |
| THB | ฿ | Thai Baht |
| IDR | Rp | Indonesian Rupiah |
| VND | ₫ | Vietnamese Dong |

To change currency, select a preset on the **Settings page (`/settings/`)** or edit `config/user_settings.json`.

### Environment Configuration

The application supports multiple environments:

| Environment | Config Class | Database |
|-------------|--------------|----------|
| Development | `DevelopmentConfig` | SQLite file |
| Testing | `TestingConfig` | In-memory SQLite |
| Production | `ProductionConfig` | SQLite file |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment name (`development`, `testing`, `production`) | `development` (`production` in Docker) |
| `SECRET_KEY` | Session secret key (required in `production` / Docker Compose) | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection URI | `sqlite:///.../instance/dividends.db` |
| `PORT` | Host port mapped by Docker Compose | `5000` |
| `GITHUB_REPOSITORY` | Image repository name in `docker-compose.yml` | `divitracker` |
| `IMAGE_TAG` | Image tag in `docker-compose.yml` | `latest` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard (paginated; supports `year`, `q`, `sort`, `dir`, `hide_zero`, `hide_zero_investments`, `page`, `per_page`) |
| GET | `/year/<year>` | Dashboard filtered by specific year (supports `q`, `sort`, `dir`, `hide_zero`, `hide_zero_investments`, `page`, `per_page`) |
| GET | `/favicon.ico` | Serves the SVG market-arrow favicon |
| GET | `/reports/yield-breakdown` | Printable yield calculation breakdown (supports `year`) |
| GET | `/reports/dividends-chart` | Dividend visualization with charts (supports `year`, `investment_id`) |
| GET | `/investments/new` | Add investment form with live preview |
| POST | `/investments/new` | Create or top up an investment |
| GET | `/investments/<id>` | View investment details & paginated dividend history (supports `year`, `page`, `per_page`) |
| GET | `/investments/<id>/edit` | Edit investment form |
| POST | `/investments/<id>/edit` | Update investment |
| POST | `/investments/<id>/delete` | Delete investment |
| GET | `/investments/api` | JSON list of investments |
| GET | `/dividends/new` | Add dividend form (supports `investment_id`) |
| POST | `/dividends/new` | Create dividend record |
| GET | `/dividends/<id>/edit` | Edit dividend form |
| POST | `/dividends/<id>/edit` | Update dividend record |
| POST | `/dividends/<id>/delete` | Delete dividend record |
| GET | `/settings/` | Settings & database management page |
| POST | `/settings/save` | Save configuration settings |
| POST | `/settings/sidebar-position` | Update sidebar navigation position (`left` or `right`, JSON or form) |
| GET | `/settings/database/download` | Download SQLite database backup |
| POST | `/settings/database/upload` | Upload/restore SQLite database |

## Technology Stack

- **Runtime**: Python 3.14.9 (in Docker) / Python 3.10+
- **Framework**: Flask 3.1.3
- **Database**: SQLite with Flask-SQLAlchemy 3.1.1 ORM
- **Migrations**: Flask-Migrate 4.1.0
- **Testing**: pytest 9.1.1, pytest-bdd 9.0.0, pytest-cov 7.1.0 (95.02% coverage, 208 BDD scenarios)
- **Frontend & Styling**: Jinja2 templates, Chart.js 4.4.0, custom CSS (`static/style.css`) with Forest & Amber dark theme (`#09251C`, `#A55704`, `#F3D2AF`, `#F8EADC`), and SVG favicon (`static/favicon.svg`)
- **Containerization**: Docker with multi-stage `python:3.14.9-slim` builds
- **CI/CD**: GitHub Actions (automated lint, test, CodeQL, and multi-arch builds to GHCR)
- **Production Server**: Gunicorn 26.2.0 WSGI

## Docker Architecture

```
┌─────────────────────────────────────────────────┐
│  Docker Container (divitracker)                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Gunicorn (2 workers, 4 threads)          │  │
│  │  └── Flask Application                    │  │
│  │      └── SQLAlchemy ORM                   │  │
│  └───────────────────────────────────────────┘  │
│                      │                          │
│                      ▼                          │
│  ┌───────────────────────────────────────────┐  │
│  │  /app/instance/dividends.db               │  │
│  └───────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ Volume Mount
                       ▼
┌─────────────────────────────────────────────────┐
│  Docker Volume: divitracker_data                │
│  (Persists across container restarts)           │
└─────────────────────────────────────────────────┘
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Pull Request**: Runs tests and builds Docker image (no push)
2. **On Push to main/master**: 
   - Runs test suite
   - Builds multi-platform image (amd64, arm64)
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with: `latest`, branch name, git SHA, semver (if tagged)

### Pulling Pre-built Images

```bash
# Pull the latest image
docker pull ghcr.io/YOUR_USERNAME/divitracker:latest

# Or use a specific version
docker pull ghcr.io/YOUR_USERNAME/divitracker:v1.0.0
```

## License

MIT License
