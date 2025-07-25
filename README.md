# 🌍 Global Inequality Visualization Dashboard

A comprehensive Python project for collecting, analyzing, and visualizing inequality data from reliable public sources including World Bank, OECD, WID.world, and Eurostat.

## 📊 Project Overview

This project provides a complete solution for inequality analysis with:

- **Data Collection**: Automated fetching from multiple public APIs and databases
- **Data Processing**: Cleaning, normalization, and validation of inequality metrics
- **Analysis**: Calculation of Gini coefficient, Palma ratio, income shares, and more
- **Visualization**: Interactive charts and dashboards using Streamlit and Plotly
- **Documentation**: Comprehensive guides and examples

## 🚀 Features

### Core Functionalities
- **Multi-source Data Integration**: World Bank, OECD, WID.world, Eurostat
- **Inequality Metrics**: Gini coefficient, Palma ratio, Theil index, Atkinson index
- **Income Distribution Analysis**: Top/bottom income shares, Lorenz curves
- **Interactive Visualizations**: Trend analysis, country comparisons, distribution plots
- **Data Export**: CSV downloads and chart exports

### Dashboard Features
- **Geographic Filtering**: Filter by continent and country
- **Time Range Selection**: Analyze trends over custom time periods
- **Multi-metric Comparison**: Compare different inequality measures
- **Real-time Updates**: Live data fetching and caching
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
inequality_viz/
│
├── data/                     # Store raw or downloaded data
│   └── README.md             # Data sources and file descriptions
│
├── notebooks/                # Jupyter notebooks for experiments
│
├── src/                      # Core source code
│   ├── __init__.py
│   ├── data_fetch.py         # Functions to download & load public data
│   ├── data_cleaning.py      # Data cleaning and formatting functions
│   ├── metrics.py            # Functions to compute inequality metrics
│   ├── visualization.py      # Functions to create interactive plots
│   └── utils.py              # Utility functions
│
├── app/                      # Streamlit app code
│   └── main_app.py
│
├── tests/                    # Unit tests
│   ├── test_metrics.py
│   └── test_data_fetch.py
│
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└── README.md                 # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inequality_viz
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run app/main_app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to access the dashboard

### Development Installation

For development with additional tools:

```bash
pip install -r requirements.txt
pip install -e .[dev]
```

## 📈 Usage

### Running the Dashboard

1. **Start the application**:
   ```bash
   streamlit run app/main_app.py
   ```

2. **Configure your analysis**:
   - Select data sources (World Bank, OECD, WID.world, Eurostat)
   - Choose geographic region (continent/country)
   - Set time period for analysis
   - Select metrics to display

3. **Explore the visualizations**:
   - **Trends Tab**: View inequality trends over time
   - **Income Distribution Tab**: Analyze Lorenz curves and income shares
   - **Country Comparison Tab**: Compare multiple countries
   - **Data Table Tab**: View raw data and download CSV files
   - **About Tab**: Learn about data sources and methodology

### Programmatic Usage

```python
from src.data_fetch import fetch_world_bank_gini
from src.metrics import gini_coefficient, palma_ratio
from src.visualization import plot_lorenz_curve

# Fetch data
data = fetch_world_bank_gini("USA", 2010, 2020)

# Calculate metrics
gini = gini_coefficient([10, 20, 30, 40, 50])
palma = palma_ratio([10, 20, 30, 40, 50])

# Create visualizations
fig = plot_lorenz_curve(pd.Series([10, 20, 30, 40, 50]))
fig.show()
```

## 📊 Data Sources

### World Bank API
- **Source**: http://api.worldbank.org/v2/en/indicator/SI.POV.GINI?format=json
- **Data**: Gini coefficient and poverty indicators
- **Coverage**: Global, 1960-present
- **License**: World Bank Open Data License

### OECD Income Distribution Database
- **Source**: https://stats.oecd.org/
- **Data**: Income distribution for OECD countries
- **Coverage**: OECD member countries
- **License**: OECD Terms and Conditions

### World Inequality Database (WID.world)
- **Source**: https://wid.world/data/
- **Data**: Comprehensive inequality metrics including top/bottom shares
- **Coverage**: Global, historical data
- **License**: Creative Commons Attribution 4.0 International

### Eurostat
- **Source**: https://ec.europa.eu/eurostat/web/income-and-living-conditions/data/database
- **Data**: EU-specific inequality and income data
- **Coverage**: European Union countries
- **License**: Eurostat Open Data License

## 📈 Metrics Explained

### Gini Coefficient
- **Range**: 0 (perfect equality) to 1 (perfect inequality)
- **Interpretation**: Higher values indicate greater inequality
- **Formula**: G = (2 * Σ(i * x_i) - (n + 1) * Σ(x_i)) / (n * Σ(x_i))

### Palma Ratio
- **Definition**: Ratio of richest 10% to poorest 40% of population
- **Interpretation**: Values > 1 indicate inequality (richer 10% have more than poorer 40%)
- **Formula**: Palma = Top 10% share / Bottom 40% share

### Income Shares
- **Top 1% Share**: Percentage of total income held by top 1%
- **Top 10% Share**: Percentage of total income held by top 10%
- **Bottom 50% Share**: Percentage of total income held by bottom 50%

### Lorenz Curve
- **Purpose**: Visual representation of income distribution
- **Interpretation**: Closer to diagonal line = more equality
- **Gini**: Area between curve and diagonal line

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_metrics.py

# Run with coverage
pytest --cov=src tests/
```

### Test Coverage
- **Metrics Calculation**: Gini, Palma ratio, income shares, Lorenz curves
- **Data Fetching**: API calls, error handling, data validation
- **Data Cleaning**: Normalization, validation, merging
- **Visualization**: Chart generation and formatting

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set API rate limiting
WORLD_BANK_RATE_LIMIT=1  # seconds between requests
OECD_RATE_LIMIT=2
```

### Data Caching
Data is automatically cached in the `data/` directory to improve performance and reduce API calls.

## 📝 API Reference

### Data Fetching Functions

```python
# World Bank data
fetch_world_bank_gini(country_code: str, start_year: int, end_year: int) -> pd.DataFrame

# OECD data
fetch_oecd_data(country_code: str = None) -> pd.DataFrame

# WID.world data
fetch_wid_data(country_code: str = None) -> pd.DataFrame

# Eurostat data
fetch_eurostat_data(country_code: str = None) -> pd.DataFrame
```

### Metrics Functions

```python
# Basic metrics
gini_coefficient(values: List[float]) -> float
palma_ratio(values: List[float]) -> float
theil_index(values: List[float]) -> float
atkinson_index(values: List[float], epsilon: float = 1.0) -> float

# Income shares
income_shares(values: List[float], percentiles: List[float] = None) -> Dict[str, float]

# Lorenz curve
lorenz_curve_data(values: List[float], num_points: int = 100) -> Tuple[List[float], List[float]]
```

### Visualization Functions

```python
# Charts
plot_lorenz_curve(data: pd.Series, title: str = "Lorenz Curve") -> go.Figure
plot_gini_by_country(df: pd.DataFrame, year: int = None) -> go.Figure
plot_income_shares(df: pd.DataFrame, country_code: str = None, year: int = None) -> go.Figure
plot_inequality_trends(df: pd.DataFrame, country_codes: List[str] = None, metric: str = 'gini') -> go.Figure
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest`
5. **Submit a pull request**

### Development Setup
```bash
# Install development dependencies
pip install -e .[dev]

# Run linting
flake8 src/ tests/

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **World Bank**: For providing open access to global development data
- **OECD**: For comprehensive income distribution statistics
- **WID.world**: For historical inequality data and research
- **Eurostat**: For EU-specific economic indicators
- **Streamlit**: For the excellent web app framework
- **Plotly**: For interactive visualization capabilities

## 📞 Support

For questions, issues, or feature requests:

1. **Check the documentation** in this README
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information
4. **Contact the maintainers** for urgent matters

## 🔄 Changelog

### Version 0.1.0 (Current)
- Initial release
- Multi-source data integration
- Core inequality metrics calculation
- Interactive Streamlit dashboard
- Comprehensive test suite
- Documentation and examples

## 🚀 Roadmap

### Upcoming Features
- [ ] Additional data sources (UN, IMF, national statistics)
- [ ] Wealth inequality analysis
- [ ] Regional and sub-national data
- [ ] Advanced statistical models
- [ ] Machine learning predictions
- [ ] API endpoints for programmatic access
- [ ] Mobile app version
- [ ] Real-time data updates
- [ ] Custom metric definitions
- [ ] Data quality indicators

### Long-term Goals
- [ ] Global inequality monitoring system
- [ ] Policy impact analysis tools
- [ ] Educational modules for inequality studies
- [ ] Integration with academic research platforms
- [ ] Multi-language support

---

**Made with ❤️ for understanding global inequality**
