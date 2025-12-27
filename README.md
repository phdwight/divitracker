# DiviTracker 💰

A Flask application for tracking dividend income from your investments. Calculate annualized dividend yields and monitor your passive income portfolio.

## Features

- **Investment Management**: Add, edit, and delete investments with ticker symbols
- **Dividend Tracking**: Record dividends with monthly, quarterly, semi-annual, or yearly frequency
- **Yield Calculation**: Automatic computation of actual and projected annualized dividend yields
- **Portfolio Dashboard**: Overview of total invested, annual dividends, and overall yield with year filtering
- **Real-time Preview**: See yield calculations before recording dividends
- **Historical Tracking**: Track investment amount at time of dividend for accurate yield calculations

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
│   │   └── dividends.py     # Dividend CRUD routes
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

### Installation

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
- Total annualized dividends (actual and projected)
- Overall portfolio yield percentage (actual and projected)
- Year filter to view dividends for specific years
- List of all investments with individual yields (actual | projected format)

## Dividend Yield Calculation

The annualized dividend yield is calculated as:

```
Yield (%) = (Annual Dividends / Total Invested) × 100
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
    }
}
```

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

## Technology Stack

- **Framework**: Flask 3.0
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Testing**: pytest with pytest-cov (95% coverage)
- **Styling**: Custom CSS (no external dependencies)

## License

MIT License
