# DiviTracker 💰

A Flask application for tracking dividend income from your investments. Calculate annualized dividend yields and monitor your passive income portfolio.

## Features

- **Investment Management**: Add, edit, and delete investments with ticker symbols
- **Dividend Tracking**: Record dividends with monthly, quarterly, semi-annual, or yearly frequency
- **Yield Calculation**: Automatic computation of annualized dividend yields
- **Yield Breakdown Page**: Detailed, printable computation breakdown for yield calculations
- **Portfolio Dashboard**: Overview of currently invested, annual dividends, and overall yield with year filtering
- **Real-time Preview**: See yield calculations before recording dividends
- **Historical Tracking**: Track investment amount at time of dividend for accurate yield calculations
- **Timezone Support**: Configurable timezone for accurate local time display (default: GMT+8)
- **Admin Settings**: Configure currency, formatting, and timezone; download/upload database backups

## Architecture

```
divitracker/
├── app/                      # Application package
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── exceptions.py        # Custom exceptions
│   ├── models.py            # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   │   ├── __init__.py
│   │   ├── main.py          # Dashboard routes
│   │   ├── investments.py   # Investment CRUD routes
│   │   ├── dividends.py     # Dividend CRUD routes
│   │   └── admin.py         # Admin settings & DB management
│   └── services/            # Business logic layer
│       ├── __init__.py
│       ├── investment_service.py
│       ├── dividend_service.py
│       └── portfolio_service.py
├── templates/               # Jinja2 templates
├── static/                  # CSS and static files
├── tests/                   # Pytest test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_services.py    # Service tests
│   ├── test_routes.py      # Route tests
│   └── test_settings.py    # Settings tests
├── instance/               # Instance-specific data (SQLite DB)
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
   cp .env.example .env
   # Edit .env and set a strong SECRET_KEY
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d --build
   ```

4. **Open your browser** and navigate to `http://127.0.0.1:5000`

#### Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View container status
docker-compose ps
```

#### Data Persistence

The SQLite database is stored in a Docker volume (`divitracker_data`) that persists across container restarts. To backup your data:

```bash
# Create a backup
docker cp divitracker:/app/instance/dividends.db ./backup_dividends.db

# Restore from backup
docker cp ./backup_dividends.db divitracker:/app/instance/dividends.db
docker-compose restart
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
- List of all investments with individual yields (actual | projected format)

### Yield Breakdown Page

Click on the "Annualized Yield" card in the dashboard to view:
- The complete yield calculation formula
- Step-by-step computation with actual values
- Per-investment breakdown showing contribution to overall yield
- Print-friendly format for record keeping

## Dividend Yield Calculation

The annualized dividend yield is calculated as:

```
Yield (%) = (Annual Dividends / Currently Invested) × 100
```

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

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Running Tests with Docker

```bash
# Build test image and run tests
docker build -t divitracker-test .
docker run --rm divitracker-test pytest tests/ -v

# Run tests with coverage
docker run --rm divitracker-test pytest tests/ -v --cov=app --cov-report=term-missing
```

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
    }
}
```

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
| `FLASK_ENV` | Environment name | `development` |
| `SECRET_KEY` | Session secret key | `dev-secret-key...` |
| `DATABASE_URL` | Database connection URI | SQLite in `instance/` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/yield-breakdown` | Yield calculation breakdown (printable) |
| GET | `/investment/add` | Add investment form |
| POST | `/investment/add` | Create/update investment |
| GET | `/investment/<id>` | View investment details |
| GET | `/investment/<id>/edit` | Edit investment form |
| POST | `/investment/<id>/edit` | Update investment |
| POST | `/investment/<id>/delete` | Delete investment |
| GET | `/investment/api/list` | JSON list of investments |
| GET | `/dividend/add` | Add dividend form |
| POST | `/dividend/add` | Create dividend record |
| GET | `/dividend/<id>/edit` | Edit dividend form |
| POST | `/dividend/<id>/edit` | Update dividend record |
| POST | `/dividend/<id>/delete` | Delete dividend record |
| GET | `/admin/` | Admin settings page |
| POST | `/admin/save-settings` | Save configuration settings |
| GET | `/admin/download-db` | Download database backup |
| POST | `/admin/upload-db` | Upload/restore database |

## Technology Stack

- **Framework**: Flask 3.0
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Testing**: pytest with pytest-cov (95% coverage)
- **Styling**: Custom CSS (no external dependencies)
- **Containerization**: Docker with multi-stage builds
- **CI/CD**: GitHub Actions (automated builds to GHCR)
- **Production Server**: Gunicorn WSGI

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
