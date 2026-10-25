# DiviTracker 💰

A Flask application for tracking dividend income from your investments. Calculate annualized dividend yields and monitor your passive income portfolio.

## Features

- **Investment Management**: Add, edit, and delete investments with ticker symbols
- **Dividend Tracking**: Record dividends with monthly, quarterly, semi-annual, or yearly frequency
- **Yield Calculation**: Automatic computation of annualized dividend yields
- **Yield Breakdown Page**: Detailed, printable computation breakdown for yield calculations
- **Dividend Graph**: Visual bar chart representation of dividends with cumulative line graph and data table, filters by year and investment
- **Portfolio Dashboard**: Overview of currently invested, annual dividends, and overall yield with year filtering and toggles to hide zero-dividend or zero-balance investments
- **Privacy Mode (Hide Amounts)**: One-click navbar toggle (`Hide amounts` / `Show amounts`) that blurs monetary values across the UI and persists in `localStorage`
- **Pagination**: Configurable items per page for dashboard and dividend history views
- **Real-time Preview**: See yield calculations before recording dividends
- **Historical Tracking**: Track investment amount at time of dividend for accurate yield calculations
- **Timezone Support**: Configurable timezone for accurate local time display (default: GMT+8)
- **Settings Page**: Configure currency, formatting, pagination, and timezone; download/upload database backups
- **RESTful URLs**: SEO-friendly URL structure following best practices (e.g., `/investments/new`, `/dividends/<id>/edit`)
- **Code Quality**: Templates pass djlint (Jinja2-aware HTML linter) with zero errors

## Architecture

```
divitracker/
├── app/                      # Application package
│   ├── __init__.py          # Package marker
│   ├── factory.py           # Application factory (create_app)
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── exceptions.py        # Custom exceptions
│   ├── models.py            # SQLAlchemy models
│   ├── settings.py          # User settings management
│   ├── utils.py             # Utility functions
│   ├── routes/              # Blueprint routes
│   │   ├── __init__.py      # Package marker
│   │   ├── main.py          # Dashboard routes
│   │   ├── investments.py   # Investment CRUD routes
│   │   ├── dividends.py     # Dividend CRUD routes
│   │   └── admin.py         # Admin settings & DB management
│   └── services/            # Business logic layer
│       ├── __init__.py      # Package marker
│       ├── investment_service.py
│       ├── dividend_service.py
│       └── portfolio_service.py
├── templates/               # Jinja2 templates
├── static/                  # Static assets (style.css, favicon.svg)
├── config/                  # User configuration (user_settings.json)
├── tests/                   # BDD test suite (pytest-bdd)
│   ├── conftest.py         # Test fixtures
│   ├── features/           # Gherkin feature files
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
│   └── step_defs/          # Step definitions
│       ├── shared_steps.py # Reusable step definitions
│       └── test_*.py       # Feature-specific steps
├── instance/               # Instance-specific data (SQLite DB)
├── Dockerfile              # Multi-stage Docker image (Python 3.14.9-slim + Gunicorn)
├── docker-compose.yml      # Docker Compose configuration
├── pyproject.toml          # Tooling & pytest configuration
├── VERSION                 # Application version file
├── run.py                  # Application entry point
└── requirements.txt        # Python dependencies
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

1. Click **"Add Investment"** in the navigation
2. Enter the investment name (or select an existing one)
3. Optionally add a ticker symbol
4. Enter the amount invested
5. Click **"Add Investment"**

### Recording a Dividend

1. Click **"Add Dividend"** in the navigation
2. Select the investment from the dropdown
3. Enter the dividend amount received
4. Select the frequency:
   - **Monthly**: Paid every month (×12 annually)
   - **Quarterly**: Paid every 3 months (×4 annually)
   - **Semi-Annual**: Paid every 6 months (×2 annually)
   - **Yearly**: Paid once per year
5. Optionally specify the period (month/year) and investment amount at time
6. Click **"Record Dividend"**

### Viewing Portfolio

The dashboard displays:
- Total amount invested across all holdings
- Total dividends received for the selected year
- Overall annualized portfolio yield percentage (clickable for detailed breakdown)
- Year filter to view dividends for specific years
- Toggle to hide investments with zero dividends received (for selected year, `hide_zero=true` by default)
- Toggle to hide investments with zero amount invested (`hide_zero_investments=true` by default)
- Paginated list of all investments with individual yields (actual | projected format)
- Configurable items per page selector

### Dividend Graph

Access the graph page via the **"Graph"** link in the navigation to view:
- Bar chart visualization of dividend income by month
- Cumulative line graph showing total earnings growth over time (toggle on/off)
- Filter by year to see monthly breakdown or view all years
- Filter by specific investment (dropdown limited to prevent overflow with long names)
- Summary statistics: Total Displayed and Highest dividend amounts
- Data table with Period, Amount, and Cumulative Total columns

### Yield Breakdown Page

Click on the "Annualized Yield" card in the dashboard to view:
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
# Run all tests (188 scenarios; automatically enforces >= 80% coverage via pyproject.toml)
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

Current coverage: **95.44%** (188 BDD scenarios; minimum required threshold of **80%** enforced via `pyproject.toml`):

| Module | Coverage |
|--------|----------|
| `app/factory.py` | 100% |
| `app/routes/dividends.py` | 100% |
| `app/services/investment_service.py` | 100% |
| `app/services/portfolio_service.py` | 100% |
| `app/exceptions.py` | 100% |
| `app/extensions.py` | 100% |
| `app/settings.py` | 98% |
| `app/models.py` | 97% |
| `app/routes/admin.py` | 96% |
| `app/routes/investments.py` | 95% |
| `app/services/dividend_service.py` | 93% |
| `app/config.py` | 91% |
| `app/routes/main.py` | 91% |
| `app/utils.py` | 82% |

### Running Tests with Docker

```bash
# Build test image and run tests
docker build -t divitracker-test .
docker run --rm divitracker-test pytest tests/ -v

# Run tests with coverage
docker run --rm divitracker-test pytest tests/ -v --cov=app --cov-report=term-missing
```

## Linting

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

All templates pass djlint with zero errors.

## Configuration

### User Settings (Currency & Formatting)

The application supports customizable currency and number formatting through a configuration file:

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
    }
}
```

#### Pagination Configuration

The `pagination` setting controls the default number of items per page:
- `items_per_page`: Number of items to show per page (5-100, default: 10)
- Can be overridden per-request using the page selector dropdown

#### Timezone Configuration

The `timezone` setting controls the local time displayed in reports:
- `offset_hours`: Hours offset from UTC (e.g., 8 for GMT+8, -5 for EST)
- `name`: Display name shown in the UI (e.g., "GMT+8", "EST")

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

To change currency, edit the `config/user_settings.json` file.

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
| GET | `/` | Dashboard (paginated; supports `year`, `hide_zero`, `hide_zero_investments`, `page`, `per_page`) |
| GET | `/year/<year>` | Dashboard filtered by specific year |
| GET | `/favicon.ico` | Serves the SVG market-arrow favicon |
| GET | `/reports/yield-breakdown` | Yield calculation breakdown (printable) |
| GET | `/reports/dividends-chart` | Dividend visualization with charts |
| GET | `/investments/new` | Add investment form |
| POST | `/investments/new` | Create/update investment |
| GET | `/investments/<id>` | View investment details (paginated dividend history) |
| GET | `/investments/<id>/edit` | Edit investment form |
| POST | `/investments/<id>/edit` | Update investment |
| POST | `/investments/<id>/delete` | Delete investment |
| GET | `/investments/api` | JSON list of investments |
| GET | `/dividends/new` | Add dividend form |
| POST | `/dividends/new` | Create dividend record |
| GET | `/dividends/<id>/edit` | Edit dividend form |
| POST | `/dividends/<id>/edit` | Update dividend record |
| POST | `/dividends/<id>/delete` | Delete dividend record |
| GET | `/settings/` | Settings page |
| POST | `/settings/save` | Save configuration settings |
| GET | `/settings/database/download` | Download database backup |
| POST | `/settings/database/upload` | Upload/restore database |

## Technology Stack

- **Runtime**: Python 3.14.9 (in Docker) / Python 3.10+
- **Framework**: Flask 3.1.3
- **Database**: SQLite with Flask-SQLAlchemy 3.1.1 ORM
- **Migrations**: Flask-Migrate 4.1.0
- **Testing**: pytest 9.1.1, pytest-bdd 9.0.0, pytest-cov 7.1.0 (95.44% coverage, 188 BDD scenarios)
- **Styling**: Custom CSS (`static/style.css`) with SVG favicon (`static/favicon.svg`)
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
