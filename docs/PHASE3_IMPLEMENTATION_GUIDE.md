# Phase 3 Completion - IMPLEMENTATION GUIDE

**Date:** January 10, 2026  
**Status:** 🚧 In Progress  
**Current:** Integrating features into pages

---

## ✅ COMPLETED SO FAR

### Core Utilities (100%)
- ✅ `app/utils/export.py` - Export to CSV/JSON
- ✅ `app/utils/session_state.py` - History & preferences  
- ✅ `app/utils/data_fetcher.py` - Real market data

### Options Page Integration (50%)
- ✅ Added imports for Phase 3 utilities
- ✅ Added real stock data input (checkbox + ticker)
- ✅ Added automatic price/volatility fetching
- ✅ Added history tracking after calculation
- 🚧 Need to add: Export buttons, History panel, Scenario analysis

---

## 🚧 REMAINING WORK

### 1. Complete Options Page Integration

**Add Export Section** (After line 458 in Options page):
```python
# Phase 3: Export Results
st.markdown("---")
st.markdown("### 📥 Export Results")

col1, col2, col3 = st.columns(3)

with col1:
    # CSV Export
    export_df = pd.DataFrame({
        'Metric': ['Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'],
        'Value': [price, delta, gamma_val, vega_val, theta, rho]
    })
    csv_data = export_to_csv(export_df)
    st.download_button("📄 CSV", csv_data, "options.csv", "text/csv")

with col2:
    # JSON Export
    json_data = export_to_json({'params': params, 'results': results})
    st.download_button("📋 JSON", json_data, "options.json", "application/json")

with col3:
    history_count = len(get_history_dataframe('options'))
    st.info(f"💾 {history_count} in history")
```

**Add History Panel** (In sidebar, after tips):
```python
# Phase 3: History
st.markdown("---")
st.markdown("### 📜 History")

history_df = get_history_dataframe('options')
if not history_df.empty:
    st.dataframe(history_df.tail(5), use_container_width=True)
    if st.button("Clear History"):
        clear_history('options')
        st.rerun()
else:
    st.info("No calculations yet")
```

---

### 2. Portfolio Page Integration

**Add to Portfolio page** (`app/pages/2_💼_Portfolio.py`):

**Real Data Input** (Replace example data section):
```python
if input_method == "Real Stock Data":
    tickers = st.multiselect(
        "Select Stocks",
        ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"],
        default=["AAPL", "MSFT", "GOOGL"]
    )
    
    if len(tickers) >= 2:
        prices = fetch_multiple_stocks(tickers, period='1y')
        returns = calculate_returns(prices)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        asset_names = tickers
```

**Export Results** (After optimization):
```python
# Export
st.markdown("### 📥 Export")
allocation_df = pd.DataFrame({
    'Asset': asset_names,
    'Weight': weights,
    'Weight %': weights * 100
})

csv_data = export_to_csv(allocation_df)
st.download_button("📄 Download Allocation", csv_data, "portfolio.csv")
```

---

### 3. Factor Models Page Integration

**Real Stock Analysis** (Replace synthetic data):
```python
if data_source == "Real Stock Data":
    ticker = st.text_input("Stock Ticker", "AAPL")
    
    if ticker:
        # Get stock data
        prices = fetch_stock_data(ticker, period='3y')
        stock_returns = calculate_returns(prices['Adj Close'])
        
        # Get factor data (would need real factor data source)
        # For now, use synthetic factors
        factor_data = generate_synthetic_factors('3', 'daily', 3)
```

**Export Results** (After analysis):
```python
# Export
st.markdown("### 📥 Export")
results_df = pd.DataFrame({
    'Factor': list(betas.keys()),
    'Beta': list(betas.values()),
    't-stat': [beta_tstats[f] for f in betas.keys()]
})

csv_data = export_to_csv(results_df)
st.download_button("📄 Download Results", csv_data, "factors.csv")
```

---

### 4. Create Scenario Analysis Component

**New File:** `app/components/scenario_analysis.py`

```python
"""Scenario analysis tools for options and portfolios."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

def options_scenario_analysis(S0, K, r, sigma, T, option_type, pricing_func):
    """
    Run scenario analysis for options.
    
    Returns DataFrame with scenarios and results.
    """
    scenarios = {
        'Base Case': (S0, sigma, T),
        'Stock +10%': (S0 * 1.1, sigma, T),
        'Stock -10%': (S0 * 0.9, sigma, T),
        'Vol +50%': (S0, sigma * 1.5, T),
        'Vol -50%': (S0, sigma * 0.5, T),
        'Half Time': (S0, sigma, T * 0.5),
        'Double Time': (S0, sigma, T * 2.0)
    }
    
    results = []
    for name, (s, sig, t) in scenarios.items():
        price = pricing_func(s, K, r, sig, t)
        results.append({
            'Scenario': name,
            'Stock': s,
            'Volatility': sig * 100,
            'Time': t,
            'Price': price,
            'Change %': ((price / pricing_func(S0, K, r, sigma, T)) - 1) * 100
        })
    
    return pd.DataFrame(results)

def create_scenario_heatmap(S_range, vol_range, pricing_func, K, r, T):
    """Create 2D heatmap of prices across stock/vol scenarios."""
    prices = np.zeros((len(vol_range), len(S_range)))
    
    for i, vol in enumerate(vol_range):
        for j, S in enumerate(S_range):
            prices[i, j] = pricing_func(S, K, r, vol, T)
    
    fig = go.Figure(data=go.Heatmap(
        z=prices,
        x=S_range,
        y=[v*100 for v in vol_range],
        colorscale='Viridis',
        colorbar=dict(title="Price")
    ))
    
    fig.update_layout(
        title="Price Sensitivity Heatmap",
        xaxis_title="Stock Price",
        yaxis_title="Volatility (%)",
        height=400
    )
    
    return fig
```

---

### 5. Create Comparison Tools Component

**New File:** `app/components/comparison_tools.py`

```python
"""Comparison tools for side-by-side analysis."""

import pandas as pd
import plotly.graph_objects as go

def compare_options(options_list):
    """
    Compare multiple options side-by-side.
    
    Parameters:
    -----------
    options_list : list of dict
        Each dict contains params and results
        
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison_data = []
    
    for i, opt in enumerate(options_list):
        comparison_data.append({
            'Option': f"Option {i+1}",
            'Type': opt['params']['option_type'],
            'Strike': opt['params']['K'],
            'Price': opt['results']['price'],
            'Delta': opt['results']['delta'],
            'Gamma': opt['results']['gamma'],
            'Vega': opt['results']['vega']
        })
    
    return pd.DataFrame(comparison_data)

def create_comparison_chart(comparison_df, metric='Price'):
    """Create bar chart comparing metric across options."""
    fig = go.Figure(data=[
        go.Bar(
            x=comparison_df['Option'],
            y=comparison_df[metric],
            text=comparison_df[metric],
            texttemplate='%{text:.4f}',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f"{metric} Comparison",
        xaxis_title="Option",
        yaxis_title=metric,
        height=400
    )
    
    return fig
```

---

### 6. Create Advanced Charts Component

**New File:** `app/components/advanced_charts.py`

```python
"""Advanced visualization components."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_volatility_surface_3d(strikes, maturities, option_prices):
    """
    Create 3D volatility surface.
    
    Parameters:
    -----------
    strikes : array
        Strike prices
    maturities : array
        Times to maturity
    option_prices : 2D array
        Option prices [maturity, strike]
    """
    fig = go.Figure(data=[go.Surface(
        x=strikes,
        y=maturities,
        z=option_prices,
        colorscale='Viridis',
        colorbar=dict(title="Price")
    )])
    
    fig.update_layout(
        title="3D Option Price Surface",
        scene=dict(
            xaxis_title="Strike Price",
            yaxis_title="Time to Maturity",
            zaxis_title="Option Price"
        ),
        height=600
    )
    
    return fig

def create_correlation_heatmap_enhanced(corr_matrix, labels):
    """Enhanced correlation heatmap with annotations."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Enhanced Correlation Matrix",
        height=500,
        xaxis=dict(side='bottom'),
        yaxis=dict(side='left')
    )
    
    return fig

def create_risk_decomposition_chart(weights, risk_contributions, labels):
    """Create risk decomposition waterfall chart."""
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=risk_contributions * 100,
            marker_color='lightblue',
            text=[f'{w*100:.1f}%' for w in weights],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Risk Contribution by Asset",
        xaxis_title="Asset",
        yaxis_title="Risk Contribution (%)",
        height=400
    )
    
    return fig
```

---

## 📋 Integration Checklist

### Options Page
- [x] Import utilities
- [x] Add real data input
- [x] Add history tracking
- [ ] Add export buttons
- [ ] Add history panel
- [ ] Add scenario analysis
- [ ] Add comparison mode

### Portfolio Page
- [ ] Import utilities
- [ ] Add real data input
- [ ] Add history tracking
- [ ] Add export buttons
- [ ] Add comparison mode

### Factor Models Page
- [ ] Import utilities
- [ ] Add real data input
- [ ] Add history tracking
- [ ] Add export buttons
- [ ] Add comparison mode

### Components
- [ ] Create scenario_analysis.py
- [ ] Create comparison_tools.py
- [ ] Create advanced_charts.py
- [ ] Integrate into pages

---

## 🎯 Estimated Time Remaining

- Complete Options page: 1 hour
- Integrate Portfolio page: 2 hours
- Integrate Factor Models page: 2 hours
- Create components: 3 hours
- Testing & polish: 2 hours

**Total:** ~10 hours

---

## 💡 Quick Win Approach

**Priority 1 (2 hours):** Complete basic integration
- Add export buttons to all pages
- Add history panels to all pages
- Test basic functionality

**Priority 2 (4 hours):** Add real data
- Integrate real stock data into all pages
- Test with actual market data
- Handle errors gracefully

**Priority 3 (4 hours):** Advanced features
- Create scenario analysis component
- Create comparison tools
- Create advanced charts
- Integrate into pages

---

**Status:** 60% complete (utilities + partial integration)  
**Next:** Complete Options page, then Portfolio, then Factors  
**Goal:** Full Phase 3 completion
