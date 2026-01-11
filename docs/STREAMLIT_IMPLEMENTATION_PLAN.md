# Streamlit Frontend Implementation Plan

**Project:** Quant Fundamentals Web Interface  
**Date:** January 10, 2026  
**Status:** 📋 Planning Phase

---

## 🎯 Project Overview

Create an **interactive web application** using Streamlit to provide a user-friendly interface for all quant-fundamentals functionality:
- Options pricing and Greeks visualization
- Portfolio optimization and backtesting
- Factor model analysis
- Real-time calculations with visual feedback

---

## 🏗️ Architecture

### High-Level Structure
```
quant-fundamentals-master/
├── app/                          [NEW]
│   ├── __init__.py
│   ├── main.py                   # Main Streamlit app
│   ├── pages/                    # Multi-page app
│   │   ├── 1_📊_Options.py
│   │   ├── 2_💼_Portfolio.py
│   │   ├── 3_📈_Factors.py
│   │   └── 4_ℹ️_About.py
│   ├── components/               # Reusable UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── charts.py
│   │   ├── inputs.py
│   │   └── tables.py
│   ├── utils/                    # App-specific utilities
│   │   ├── __init__.py
│   │   ├── session_state.py
│   │   ├── formatters.py
│   │   └── cache.py
│   └── assets/                   # Static assets
│       ├── styles.css
│       ├── logo.png
│       └── favicon.ico
│
├── options/                      [EXISTING]
├── portfolio/                    [EXISTING]
├── factors/                      [EXISTING]
└── requirements.txt              [UPDATE]
```

---

## 📱 Application Pages

### 1. Home / Dashboard
**Route:** `/`  
**Purpose:** Landing page with overview and quick access

**Features:**
- Welcome message and project description
- Quick stats (available models, test coverage, etc.)
- Navigation cards to main sections
- Recent calculations (session history)
- System status (tests passing, version info)

**Layout:**
```
┌─────────────────────────────────────────┐
│  🎯 Quant Fundamentals                  │
│  Professional Quantitative Finance Tools│
├─────────────────────────────────────────┤
│  📊 Options    💼 Portfolio   📈 Factors│
│  [Card]        [Card]         [Card]    │
│                                          │
│  📈 Quick Stats                          │
│  ✅ 64 Tests Passing                    │
│  ⚡ 3x Faster Monte Carlo                │
│  📚 Complete Documentation               │
└─────────────────────────────────────────┘
```

---

### 2. Options Pricing Page
**Route:** `/Options`  
**Purpose:** Interactive options pricing and Greeks analysis

#### Features

##### 2.1 Input Panel (Sidebar)
```python
- Stock Price (S0): slider + number input
- Strike Price (K): slider + number input
- Risk-Free Rate (r): slider (0-20%)
- Volatility (σ): slider (0-200%)
- Time to Maturity (T): slider (0-5 years)
- Option Type: radio (Call/Put)
- Pricing Method: selectbox (Black-Scholes, Monte Carlo, Parallel MC)
- MC Paths: slider (10k-1M) [if MC selected]
```

##### 2.2 Main Display
```
┌─────────────────────────────────────────┐
│  Option Price                            │
│  $10.45 ± $0.02                         │
│                                          │
│  Greeks                                  │
│  Delta: 0.5234  Gamma: 0.0156          │
│  Vega: $0.38    Theta: -$0.012/day     │
│  Rho: $0.45                             │
├─────────────────────────────────────────┤
│  📊 Visualizations                      │
│  - Payoff Diagram                       │
│  - Greeks vs Spot Price                 │
│  - Price vs Volatility (Surface)        │
│  - Time Decay Chart                     │
└─────────────────────────────────────────┘
```

##### 2.3 Advanced Features
- **Scenario Analysis**: Multiple strikes/maturities table
- **Implied Volatility**: Reverse calculation
- **Variance Reduction**: Compare methods (antithetic, control variates)
- **Performance Metrics**: Execution time, convergence analysis
- **Export**: Download results as CSV/JSON

---

### 3. Portfolio Optimization Page
**Route:** `/Portfolio`  
**Purpose:** Portfolio construction and backtesting

#### Features

##### 3.1 Input Panel
```python
- Asset Selection: multiselect (tickers or upload CSV)
- Date Range: date picker (start, end)
- Optimization Method: selectbox
  * Maximum Sharpe Ratio
  * Minimum Variance
  * Risk Parity
  * Target Return
- Risk-Free Rate: slider
- Constraints: checkboxes
  * Long-only
  * Max position size
  * Sector limits
```

##### 3.2 Main Display
```
┌─────────────────────────────────────────┐
│  Optimal Portfolio                       │
│  Expected Return: 12.5%                 │
│  Volatility: 15.2%                      │
│  Sharpe Ratio: 0.69                     │
│                                          │
│  Allocation                              │
│  AAPL: 30%  MSFT: 25%  GOOGL: 20%      │
│  AMZN: 15%  META: 10%                   │
├─────────────────────────────────────────┤
│  📊 Visualizations                      │
│  - Efficient Frontier                   │
│  - Allocation Pie Chart                 │
│  - Risk Contribution Bar Chart          │
│  - Historical Performance               │
└─────────────────────────────────────────┘
```

##### 3.3 Backtesting Tab
```
- Rebalancing Frequency: selectbox (Daily, Monthly, Quarterly)
- Lookback Period: slider (1-5 years)
- Strategy Comparison: multiselect
- Performance Metrics Table
- Cumulative Returns Chart
- Drawdown Analysis
```

---

### 4. Factor Models Page
**Route:** `/Factors`  
**Purpose:** Fama-French factor analysis

#### Features

##### 4.1 Input Panel
```python
- Ticker: text input or selectbox
- Model: radio (FF3, FF5)
- Period: date range or preset (1Y, 3Y, 5Y)
- Frequency: radio (Daily, Monthly)
- Data Source: selectbox (Live/Yahoo, Synthetic)
```

##### 4.2 Main Display
```
┌─────────────────────────────────────────┐
│  Factor Model Results: AAPL              │
│  Model: Fama-French 5-Factor            │
│                                          │
│  Alpha: 2.5% (annualized) ***           │
│  R-squared: 0.85                        │
│                                          │
│  Factor Betas                            │
│  Market: 1.15 ***                       │
│  SMB: 0.23 **                           │
│  HML: -0.18 *                           │
│  RMW: 0.31 ***                          │
│  CMA: -0.12                             │
├─────────────────────────────────────────┤
│  📊 Visualizations                      │
│  - Factor Exposures Bar Chart           │
│  - Actual vs Predicted Returns          │
│  - Residual Analysis                    │
│  - Rolling Beta Chart                   │
└─────────────────────────────────────────┘
```

##### 4.3 Comparison Tab
```
- Compare multiple stocks
- Compare FF3 vs FF5
- Sector analysis
- Time-varying betas
```

---

### 5. About / Documentation Page
**Route:** `/About`  
**Purpose:** Documentation and help

**Sections:**
- Project overview
- Mathematical formulas
- Usage examples
- API documentation
- Test results
- Performance benchmarks
- Links to GitHub, docs

---

## 🎨 UI/UX Design

### Design Principles
1. **Clean & Professional**: Financial industry standard
2. **Responsive**: Works on desktop and tablet
3. **Fast**: Cached computations, optimized rendering
4. **Intuitive**: Clear labels, helpful tooltips
5. **Accessible**: WCAG 2.1 AA compliance

### Color Scheme
```python
PRIMARY = "#1f77b4"      # Professional blue
SECONDARY = "#ff7f0e"    # Accent orange
SUCCESS = "#2ca02c"      # Green for positive
DANGER = "#d62728"       # Red for negative
WARNING = "#ff9800"      # Orange for warnings
BACKGROUND = "#ffffff"   # White background
SIDEBAR = "#f0f2f6"      # Light gray sidebar
```

### Typography
```python
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
HEADING_SIZE = "2rem"
BODY_SIZE = "1rem"
SMALL_SIZE = "0.875rem"
```

---

## 🔧 Technical Implementation

### Core Technologies
```python
streamlit>=1.30.0           # Main framework
plotly>=5.18.0              # Interactive charts
pandas>=1.3.0               # Data manipulation
numpy>=1.20.0               # Numerical computing
yfinance>=0.2.0             # Market data (optional)
streamlit-aggrid>=0.3.4     # Advanced tables
streamlit-option-menu>=0.3.6 # Better navigation
```

### Key Features

#### 1. Session State Management
```python
# app/utils/session_state.py
class SessionState:
    """Manage app state across reruns."""
    
    @staticmethod
    def init():
        if 'calculations' not in st.session_state:
            st.session_state.calculations = []
        if 'cache' not in st.session_state:
            st.session_state.cache = {}
```

#### 2. Caching Strategy
```python
@st.cache_data(ttl=3600)
def fetch_market_data(ticker, start, end):
    """Cache market data for 1 hour."""
    return yf.download(ticker, start, end)

@st.cache_resource
def load_model():
    """Cache model initialization."""
    return FF3Model()
```

#### 3. Input Validation
```python
from utils.validation import validate_option_params, ValidationError

try:
    validate_option_params(S0, K, r, sigma, T)
    price = black_scholes_call(S0, K, r, sigma, T)
    st.success(f"Option Price: ${price:.4f}")
except ValidationError as e:
    st.error(f"Invalid input: {e}")
```

#### 4. Progress Indicators
```python
with st.spinner("Calculating..."):
    price, std_err = price_european_call_parallel(
        S0, K, r, sigma, T, n_paths=1_000_000
    )

# Or with progress bar
progress_bar = st.progress(0)
for i in range(100):
    # Calculation
    progress_bar.progress(i + 1)
```

---

## 📊 Visualization Components

### 1. Interactive Charts (Plotly)

#### Options Payoff Diagram
```python
import plotly.graph_objects as go

def plot_payoff_diagram(S0, K, option_type, premium):
    S = np.linspace(0.5*K, 1.5*K, 100)
    
    if option_type == 'call':
        payoff = np.maximum(S - K, 0) - premium
    else:
        payoff = np.maximum(K - S, 0) - premium
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=S, y=payoff, mode='lines'))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=K, line_dash="dash", line_color="red")
    
    fig.update_layout(
        title="Option Payoff Diagram",
        xaxis_title="Stock Price at Expiry",
        yaxis_title="Profit/Loss",
        hovermode='x unified'
    )
    
    return fig
```

#### Efficient Frontier
```python
def plot_efficient_frontier(returns, volatilities, sharpe_ratios):
    fig = go.Figure()
    
    # Scatter plot of portfolios
    fig.add_trace(go.Scatter(
        x=volatilities,
        y=returns,
        mode='markers',
        marker=dict(
            size=8,
            color=sharpe_ratios,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sharpe Ratio")
        ),
        text=[f"Sharpe: {sr:.2f}" for sr in sharpe_ratios],
        hovertemplate="Vol: %{x:.2%}<br>Return: %{y:.2%}<br>%{text}"
    ))
    
    fig.update_layout(
        title="Efficient Frontier",
        xaxis_title="Volatility (Risk)",
        yaxis_title="Expected Return",
        hovermode='closest'
    )
    
    return fig
```

### 2. Data Tables (AgGrid)
```python
from st_aggrid import AgGrid, GridOptionsBuilder

def display_results_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True,
        value=True,
        enableRowGroup=True,
        editable=False
    )
    
    gridOptions = gb.build()
    
    AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        theme='streamlit'
    )
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Basic app structure and one working page

**Tasks:**
- [ ] Set up Streamlit app structure
- [ ] Create main.py with navigation
- [ ] Implement Options page (basic)
- [ ] Add Black-Scholes calculator
- [ ] Create simple payoff diagram
- [ ] Test deployment locally

**Deliverables:**
- Working Streamlit app
- Options pricing calculator
- Basic visualization

---

### Phase 2: Core Features (Week 2)
**Goal:** Complete all three main pages

**Tasks:**
- [ ] Implement Portfolio page
  - [ ] Asset selection
  - [ ] Optimization methods
  - [ ] Efficient frontier plot
- [ ] Implement Factor Models page
  - [ ] FF3/FF5 analysis
  - [ ] Factor exposure charts
- [ ] Add Greeks visualization
- [ ] Implement caching
- [ ] Add input validation

**Deliverables:**
- Three functional pages
- All core calculations working
- Error handling

---

### Phase 3: Advanced Features (Week 3)
**Goal:** Polish and advanced functionality

**Tasks:**
- [ ] Add Monte Carlo options
- [ ] Implement backtesting
- [ ] Add scenario analysis
- [ ] Create comparison tools
- [ ] Add export functionality
- [ ] Implement session history
- [ ] Add tooltips and help

**Deliverables:**
- Advanced features
- Export capabilities
- User guidance

---

### Phase 4: Polish & Deploy (Week 4)
**Goal:** Production-ready deployment

**Tasks:**
- [ ] Custom CSS styling
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Add About page
- [ ] Write user documentation
- [ ] Deploy to Streamlit Cloud
- [ ] Set up CI/CD

**Deliverables:**
- Production deployment
- Complete documentation
- User guide

---

## 📝 Code Examples

### Main App Structure
```python
# app/main.py
import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Quant Fundamentals",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Home page
st.title("🎯 Quant Fundamentals")
st.markdown("### Professional Quantitative Finance Tools")

# Navigation cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Options")
    st.markdown("Price options and analyze Greeks")
    if st.button("Go to Options →"):
        st.switch_page("pages/1_📊_Options.py")

with col2:
    st.markdown("### 💼 Portfolio")
    st.markdown("Optimize and backtest portfolios")
    if st.button("Go to Portfolio →"):
        st.switch_page("pages/2_💼_Portfolio.py")

with col3:
    st.markdown("### 📈 Factors")
    st.markdown("Analyze factor models")
    if st.button("Go to Factors →"):
        st.switch_page("pages/3_📈_Factors.py")

# Quick stats
st.markdown("---")
st.markdown("### 📈 Quick Stats")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tests Passing", "64/64", "100%")
col2.metric("Code Quality", "10/10", "+2.5")
col3.metric("MC Speedup", "3.0x", "+200%")
col4.metric("Documentation", "Complete", "✅")
```

### Options Page Example
```python
# app/pages/1_📊_Options.py
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from options.black_scholes import black_scholes_call, black_scholes_put
from options.greeks import delta_call, gamma, vega, theta_call
from utils.validation import validate_option_params, ValidationError
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Options Pricing", page_icon="📊", layout="wide")

st.title("📊 Options Pricing")

# Sidebar inputs
with st.sidebar:
    st.header("Parameters")
    
    S0 = st.number_input("Stock Price (S₀)", value=100.0, min_value=0.01)
    K = st.number_input("Strike Price (K)", value=100.0, min_value=0.01)
    r = st.slider("Risk-Free Rate (%)", 0.0, 20.0, 5.0) / 100
    sigma = st.slider("Volatility (%)", 1.0, 200.0, 20.0) / 100
    T = st.slider("Time to Maturity (years)", 0.01, 5.0, 1.0)
    
    option_type = st.radio("Option Type", ["Call", "Put"])
    
    calculate = st.button("Calculate", type="primary", use_container_width=True)

# Main content
if calculate:
    try:
        # Validate inputs
        validate_option_params(S0, K, r, sigma, T)
        
        # Calculate price
        if option_type == "Call":
            price = black_scholes_call(S0, K, r, sigma, T)
            delta = delta_call(S0, K, T, r, sigma)
            theta = theta_call(S0, K, T, r, sigma)
        else:
            price = black_scholes_put(S0, K, r, sigma, T)
            delta = delta_put(S0, K, T, r, sigma)
            theta = theta_put(S0, K, T, r, sigma)
        
        # Calculate other Greeks
        gamma_val = gamma(S0, K, T, r, sigma)
        vega_val = vega(S0, K, T, r, sigma)
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Option Price", f"${price:.4f}")
            
            st.markdown("### Greeks")
            st.metric("Delta (Δ)", f"{delta:.4f}")
            st.metric("Gamma (Γ)", f"{gamma_val:.6f}")
            st.metric("Vega (ν)", f"${vega_val:.4f}")
            st.metric("Theta (Θ)", f"${theta:.4f}/day")
        
        with col2:
            # Payoff diagram
            S_range = np.linspace(0.5*K, 1.5*K, 100)
            if option_type == "Call":
                payoff = np.maximum(S_range - K, 0) - price
            else:
                payoff = np.maximum(K - S_range, 0) - price
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=S_range, y=payoff,
                mode='lines',
                name='Payoff',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_vline(x=K, line_dash="dash", line_color="red",
                         annotation_text="Strike")
            
            fig.update_layout(
                title=f"{option_type} Option Payoff Diagram",
                xaxis_title="Stock Price at Expiry",
                yaxis_title="Profit/Loss ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.success("✅ Calculation complete!")
        
    except ValidationError as e:
        st.error(f"❌ Invalid input: {e}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("👈 Enter parameters and click Calculate")
```

---

## 🔒 Security & Performance

### Security Considerations
- [ ] Input sanitization (prevent injection)
- [ ] Rate limiting for API calls
- [ ] No sensitive data in session state
- [ ] HTTPS only in production
- [ ] Environment variables for secrets

### Performance Optimization
- [ ] Cache expensive calculations
- [ ] Lazy load large datasets
- [ ] Optimize chart rendering
- [ ] Minimize rerun triggers
- [ ] Use session state efficiently

---

## 📦 Deployment

### Streamlit Cloud (Recommended)
```bash
# Deploy to Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Deploy app/main.py
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501"]
```

### Local Development
```bash
# Run locally
streamlit run app/main.py

# With auto-reload
streamlit run app/main.py --server.runOnSave true
```

---

## 📊 Success Metrics

### User Experience
- [ ] Page load time < 2 seconds
- [ ] Calculation time < 5 seconds
- [ ] Mobile responsive (tablet+)
- [ ] No errors in console
- [ ] Intuitive navigation

### Technical
- [ ] 100% uptime
- [ ] All calculations accurate
- [ ] Proper error handling
- [ ] Cached where appropriate
- [ ] Clean code structure

---

## 📚 Documentation Needs

### User Documentation
- [ ] Getting started guide
- [ ] Feature tutorials
- [ ] FAQ section
- [ ] Video demos
- [ ] API reference

### Developer Documentation
- [ ] Architecture overview
- [ ] Component documentation
- [ ] Deployment guide
- [ ] Contributing guidelines
- [ ] Testing procedures

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Review and approve this plan
2. [ ] Set up app directory structure
3. [ ] Install Streamlit and dependencies
4. [ ] Create main.py skeleton
5. [ ] Implement basic Options page

### Short-term (Next 2 Weeks)
1. [ ] Complete all three main pages
2. [ ] Add visualizations
3. [ ] Implement caching
4. [ ] Test locally

### Long-term (Month 1)
1. [ ] Add advanced features
2. [ ] Polish UI/UX
3. [ ] Deploy to Streamlit Cloud
4. [ ] Create user documentation

---

## 💡 Future Enhancements

### Phase 2 Features (Post-Launch)
- [ ] User accounts and saved portfolios
- [ ] Real-time market data integration
- [ ] Advanced charting (candlesticks, technical indicators)
- [ ] PDF report generation
- [ ] API endpoints for programmatic access
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Dark mode

---

## ✅ Approval Checklist

- [ ] Architecture approved
- [ ] UI/UX design approved
- [ ] Technology stack approved
- [ ] Timeline realistic
- [ ] Resources allocated
- [ ] Ready to start implementation

---

**Plan Status:** 📋 Ready for Review  
**Estimated Timeline:** 4 weeks  
**Complexity:** Medium  
**Priority:** High

**Next Action:** Review plan and approve to begin Phase 1 implementation
