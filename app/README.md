# Quant Fundamentals - Streamlit Web Interface

Interactive web application for quantitative finance tools.

## 🚀 Quick Start

### Run Locally
```bash
# From project root
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 📁 Structure

```
app/
├── main.py                    # Home page
├── pages/                     # Multi-page app
│   ├── 1_📊_Options.py       # Options pricing (Phase 1 ✅)
│   ├── 2_💼_Portfolio.py     # Portfolio optimization (Phase 2)
│   └── 3_📈_Factors.py       # Factor models (Phase 2)
├── components/                # Reusable UI components
├── utils/                     # App utilities
└── assets/                    # Static assets
```

## ✨ Features

### Phase 1 (Current) ✅
- **Home Page**: Navigation and system status
- **Options Page**: 
  - Black-Scholes pricing
  - Monte Carlo simulation (standard & parallel)
  - Greeks calculation
  - Interactive payoff diagrams
  - Greeks visualization

### Phase 2 (Coming Soon) 🚧
- **Portfolio Page**: Optimization and backtesting
- **Factor Models Page**: FF3/FF5 analysis

## 🎨 Pages

### 1. Home (`main.py`)
- Feature cards with navigation
- System status metrics
- Quick links

### 2. Options (`pages/1_📊_Options.py`)
- Parameter inputs (sidebar)
- Pricing methods:
  - Black-Scholes (analytical)
  - Monte Carlo
  - Parallel Monte Carlo
- Greeks display
- Interactive charts:
  - Payoff diagram
  - Greeks vs spot price

### 3. Portfolio (`pages/2_💼_Portfolio.py`)
- Coming in Phase 2

### 4. Factor Models (`pages/3_📈_Factors.py`)
- Coming in Phase 2

## 🛠️ Development

### Run with Auto-Reload
```bash
streamlit run app/main.py --server.runOnSave true
```

### Debug Mode
```bash
streamlit run app/main.py --logger.level=debug
```

### Custom Port
```bash
streamlit run app/main.py --server.port=8502
```

## 📊 Technology Stack

- **Streamlit**: Web framework
- **Plotly**: Interactive charts
- **NumPy/Pandas**: Data processing
- **Custom modules**: Options, Portfolio, Factors

## 🎯 Usage

1. **Navigate**: Use home page cards or sidebar
2. **Configure**: Enter parameters in sidebar
3. **Calculate**: Click calculate button
4. **Visualize**: View results and charts
5. **Export**: (Coming in Phase 3)

## 🔧 Configuration

### Streamlit Config
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
enableCORS = false
```

## 📝 Notes

- Phase 1 focuses on Options pricing
- Portfolio and Factors pages are placeholders
- Full implementation in Phase 2 (Week 2)

## 🐛 Troubleshooting

### Import Errors
Make sure you're running from project root:
```bash
cd /path/to/quant-fundamentals-master
streamlit run app/main.py
```

### Module Not Found
Install all dependencies:
```bash
pip install -r requirements.txt
```

## 📚 Documentation

- [Streamlit Docs](https://docs.streamlit.io)
- [Plotly Docs](https://plotly.com/python/)
- [Project Documentation](../COMPREHENSIVE_DOCUMENTATION.md)

## ✅ Status

- **Phase 1**: ✅ Complete (Options page functional)
- **Phase 2**: 🚧 In Progress (Portfolio & Factors)
- **Phase 3**: 📋 Planned (Advanced features)
- **Phase 4**: 📋 Planned (Polish & deploy)

---

**Version**: 1.0.0 (Phase 1)  
**Status**: Development  
**Last Updated**: January 10, 2026
