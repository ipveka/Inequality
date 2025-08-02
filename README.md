# Gini Inequality Visualizer

A comprehensive Python web application built with Streamlit to visualize income inequality trends using the Gini coefficient. This application fetches real-time data from the World Bank API and provides interactive visualizations and detailed analysis of inequality patterns across different countries and time periods.

## 📊 Features

- **Interactive Country Selection**: Choose from 200+ countries with data from the World Bank
- **Real-time Data**: Fetches the latest Gini coefficient data directly from World Bank API
- **Interactive Visualizations**: Plotly-powered charts with hover details, zoom, and pan functionality
- **Detailed Data Tables**: Chronologically sorted data with export capabilities
- **Comprehensive Error Handling**: User-friendly error messages and recovery options
- **Data Insights**: Trend analysis and summary statistics
- **Professional UI**: Clean, responsive interface with loading states and status indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for World Bank API access)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gini-inequality-visualizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 📋 Dependencies

The application requires the following Python packages (see `requirements.txt`):

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
requests>=2.31.0
numpy>=1.24.0
```

## 🎯 Usage

### Basic Usage

1. **Start the application** by running `streamlit run app.py`
2. **Select a country** from the sidebar dropdown menu
3. **View the interactive chart** showing Gini coefficient trends over time
4. **Examine detailed data** in the table below the chart
5. **Download data** as CSV for further analysis

### Understanding the Gini Coefficient

The Gini coefficient measures income inequality within a country:

- **0**: Perfect equality (everyone has the same income)
- **100**: Perfect inequality (one person has all the income)

**Typical ranges:**
- **20-35**: Relatively equal distribution (Nordic countries)
- **35-50**: Moderate inequality (most developed countries)
- **50+**: High inequality (some developing countries)

### Countries with Good Data Coverage

The following countries typically have comprehensive Gini data:
- 🇺🇸 United States
- 🇩🇪 Germany
- 🇧🇷 Brazil
- 🇫🇷 France
- 🇬🇧 United Kingdom
- 🇮🇹 Italy
- 🇯🇵 Japan
- Most European Union countries

## 🏗️ Architecture

The application follows a clean, modular architecture with organized folder structure and clear separation of concerns:

```
gini-inequality-visualizer/
├── app.py                 # Main Streamlit application
├── utils/                 # Core utility modules
│   ├── __init__.py        # Package initialization with exports
│   ├── data_models.py     # Data models and validation utilities
│   ├── data_service.py    # World Bank API client and data fetching
│   ├── ui_components.py   # Streamlit UI components and layouts
│   └── visualization.py   # Chart and table creation using Plotly
├── tests/                 # Comprehensive test suite
│   ├── __init__.py        # Test package initialization
│   ├── test_integration.py # End-to-end integration tests
│   ├── test_data_models.py # Data model and validation tests
│   └── test_visualization.py # Visualization component tests
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
```

### Utils Package

The `utils/` package contains all core functionality with clean imports and proper module organization:

```python
# Import from utils package
from utils import WorldBankClient, create_gini_line_plot, render_sidebar

# Or import specific modules
from utils.data_service import WorldBankClient
from utils.visualization import create_gini_line_plot, create_gini_table
from utils.ui_components import render_sidebar, show_error_message
```

### Core Components

1. **Data Service** (`utils/data_service.py`):
   - `WorldBankClient`: API client with caching and error handling
   - Fetches country lists and Gini coefficient data
   - Implements retry logic and rate limiting

2. **Data Models** (`utils/data_models.py`):
   - `Country`: Country information model
   - `GiniDataPoint`: Individual data point model
   - `GiniTimeSeries`: Time series container
   - Data validation and processing utilities

3. **Visualization** (`utils/visualization.py`):
   - `create_gini_line_plot()`: Interactive Plotly line charts
   - `create_gini_table()`: Formatted data tables
   - Professional styling and responsive design

4. **UI Components** (`utils/ui_components.py`):
   - `render_sidebar()`: Country selection interface
   - `render_main_dashboard()`: Main content area
   - Error handling and loading states

5. **Main Application** (`app.py`):
   - Streamlit configuration and orchestration
   - Session state management
   - Comprehensive error handling

## 🌐 Data Sources

### World Bank Open Data API

The application uses the World Bank Open Data API to fetch real-time Gini coefficient data:

- **Base URL**: `https://api.worldbank.org/v2`
- **Countries Endpoint**: `/country` - Fetches list of available countries
- **Gini Data Endpoint**: `/country/{country_code}/indicator/SI.POV.GINI` - Fetches Gini coefficient data
- **Indicator Code**: `SI.POV.GINI` - Gini index (World Bank estimate)

### API Features Used

- **JSON Format**: All data retrieved in JSON format
- **Date Filtering**: Requests data for specific year ranges (1990-2023)
- **Pagination**: Handles large datasets with per_page parameter
- **Error Handling**: Comprehensive handling of API errors and rate limits

### Data Quality

- **Coverage**: 200+ countries and territories
- **Time Range**: Data available from 1960s to present (varies by country)
- **Update Frequency**: World Bank updates data annually
- **Data Sources**: National statistical offices, household surveys, and World Bank estimates

## 🔧 Configuration

### Environment Variables

The application supports optional configuration through environment variables:

- `WORLDBANK_API_TIMEOUT`: Request timeout in seconds (default: 30)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `MAX_RETRIES`: Maximum API retry attempts (default: 3)

### Streamlit Configuration

The app uses the following Streamlit configuration:

```python
st.set_page_config(
    page_title="Gini Inequality Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

## 🧪 Testing

The application includes comprehensive test coverage with a clean, organized test suite:

### Running Tests

```bash
# Run all tests with pytest
python -m pytest tests/

# Run specific test files
python tests/test_integration.py      # Comprehensive integration tests
python tests/test_data_models.py      # Data model and validation tests
python tests/test_visualization.py    # Visualization component tests

# Run with coverage
python -m pytest tests/ --cov=utils --cov=app --cov-report=html

# Quick integration test
python tests/test_integration.py
```

### Test Categories

1. **Integration Tests** (`tests/test_integration.py`):
   - End-to-end user workflows from country selection to visualization
   - Real World Bank API connectivity and data retrieval
   - Application performance with multiple countries and datasets
   - Streamlit application startup verification

2. **Data Model Tests** (`tests/test_data_models.py`):
   - Data model classes (Country, GiniDataPoint, GiniTimeSeries)
   - Validation functions for data integrity
   - Data processing and transformation utilities
   - Summary statistics generation

3. **Visualization Tests** (`tests/test_visualization.py`):
   - Interactive line plot creation with Plotly
   - Data table formatting and display
   - Empty data handling and edge cases
   - Chart styling and accessibility features

## 🚨 Error Handling

The application provides comprehensive error handling for various scenarios:

### Connection Issues
- Network connectivity problems
- API timeouts and server errors
- DNS resolution failures

### Data Issues
- Missing or invalid country data
- No Gini data available for selected country
- Malformed API responses

### User Experience
- Clear error messages with actionable guidance
- Automatic retry mechanisms
- Graceful degradation when services are unavailable

## 🔒 Security Considerations

- **API Rate Limiting**: Respects World Bank API rate limits
- **Input Validation**: All user inputs are validated and sanitized
- **Error Information**: Sensitive error details are logged but not exposed to users
- **No Authentication**: Application uses public World Bank API (no API keys required)

## 🚀 Deployment

### Local Development

```bash
streamlit run app.py
```

### Production Deployment

The application can be deployed on various platforms:

1. **Streamlit Cloud**: Direct deployment from GitHub repository
2. **Heroku**: Using Procfile and requirements.txt
3. **Docker**: Containerized deployment
4. **AWS/GCP/Azure**: Cloud platform deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📈 Performance

### Optimization Features

- **Caching**: API responses cached for 1 hour to reduce load times
- **Lazy Loading**: Data fetched only when countries are selected
- **Efficient Data Processing**: Pandas operations optimized for performance
- **Responsive UI**: Progressive loading with status indicators

### Performance Metrics

- **Initial Load**: ~2-3 seconds (country list loading)
- **Country Selection**: ~1-2 seconds (with caching)
- **Chart Rendering**: <1 second (Plotly optimization)
- **Memory Usage**: ~50-100MB typical usage

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Follow code style** guidelines (PEP 8)
4. **Update documentation** for any changes
5. **Submit a pull request** with clear description

### Development Setup

```bash
# Clone your fork
git clone <your-fork-url>
cd gini-inequality-visualizer

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
python -m pytest

# Format code
black .

# Check code style
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **World Bank**: For providing free access to comprehensive inequality data
- **Streamlit**: For the excellent web application framework
- **Plotly**: For interactive visualization capabilities
- **Pandas**: For efficient data processing and manipulation

## 📞 Support

If you encounter any issues or have questions:

1. **Check the documentation** above for common solutions
2. **Review error messages** - they often contain helpful guidance
3. **Verify internet connection** - the app requires API access
4. **Try refreshing** the application if you encounter temporary issues

## 📚 Additional Documentation

- [API Documentation](API_DOCUMENTATION.md) - Detailed API reference and technical specifications
- [Test Summary](test_summary.md) - Comprehensive testing results and coverage

## 🔗 Useful Links

- [World Bank Open Data](https://data.worldbank.org/)
- [Gini Coefficient Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/114933)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)

---

**Built with ❤️ using Streamlit, Plotly, and World Bank Open Data**
