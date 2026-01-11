# 📖 Quant Fundamentals: User Guide

Welcome to the **Quant Fundamentals** web application! This guide will help you navigate the various tools available for quantitative finance analysis.

---

## 🎯 Getting Started

When you launch the application, you'll be greeted by the **Home Dashboard**. From here, you can access the three main modules:

1.  **📊 Options Pricing**: Price European options and analyze Greeks.
2.  **💼 Portfolio Optimization**: Build and analyze optimal asset allocations.
3.  **📈 Factor Models**: Decompose stock returns using Fama-French models.

---

## 📊 Options Pricing Tool

The Options tool allows you to calculate the fair value of Call and Put options using multiple methodologies.

### How to use:
1.  **Configure Parameters**: In the sidebar, set the Stock Price ($S_0$), Strike Price ($K$), Risk-free Rate, Volatility, and Time to Maturity.
2.  **Select Method**:
    *   **Black-Scholes**: Analytical solution (fastest).
    *   **Monte Carlo**: Simulation-based pricing (good for verification).
    *   **Parallel MC**: Optimized Monte Carlo using multiple CPU cores for high-path simulations.
3.  **Click "Calculate"**: View the price, Greeks (Delta, Gamma, Vega, Theta, Rho), and interactive payoff diagrams.

### Pro Tips:
*   Use the **Real Stock Data** checkbox to fetch live prices and volatility estimates automatically!
*   The **Greeks vs Spot** charts help you understand how your position's sensitivity changes with market movements.

---

## 💼 Portfolio Optimization

Build robust portfolios based on Modern Portfolio Theory and advanced risk-parity models.

### How to use:
1.  **Input Methodology**: Choose between example data (5-asset tech portfolio) or custom returns/covariance input.
2.  **Select Objective**:
    *   **Max Sharpe Ratio**: Maximizes risk-adjusted returns.
    *   **Min Variance**: Minimizes total portfolio volatility.
    *   **Risk Parity**: Equalizes risk contribution from each asset.
    *   **Inverse Volatility**: Simple weights based on 1/standard deviation.
3.  **Set Constraints**: Toggle "Allow Short Selling" if your strategy permits negative weights.
4.  **Analyze Results**: View the optimal weights, efficient frontier, and asset correlation matrix.

---

## 📈 Factor Model Analysis

Understand what drives your stock returns by decomposing them into market, size, and value factors.

### How to use:
1.  **Select Model**: Use the classic **Fama-French 3-Factor** or the enhanced **5-Factor** model.
2.  **Run Analysis**: Click "Analyze" to see how much of a stock's return is explained by Alpha (skill/idiosyncratic) vs. Beta (market factors).
3.  **Interpret Betas**:
    *   **Mkt-RF > 1**: High systematic risk (aggressive).
    *   **SMB > 0**: Small-cap tilted behavior.
    *   **HML > 0**: Value-oriented behavior.
    *   **RMW > 0**: Profitable company bias.
    *   **CMA > 0**: Conservative investment bias.

---

## ℹ️ Troubleshooting & Tips

*   **Caching**: The app uses intelligent caching. If you change a parameter to a previously used value, the results will appear instantly.
*   **Validation Errors**: Ensure your inputs are mathematically valid (e.g., Strike Price > 0, Volatility > 1%). The app will guide you if any parameter is out of bounds.
*   **Mobile Use**: The interface is responsive and works best on tablets and desktops.

---

*Build your quantitative edge with Quant Fundamentals.*
