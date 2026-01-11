# 🎯 Quant Fundamentals

**Professional Quantitative Finance Tools built with Python and Streamlit.**

Quant Fundamentals is a comprehensive platform designed for researchers, traders, and finance students. It implements foundational quantitative methods—from options pricing to modern portfolio theory and factor analysis—with a focus on mathematical clarity and computational performance.

---

## 🚀 Interactive Web Platform

The platform is available as a professional web application, allowing for direct interaction with market data and complex financial models without any coding.

### **Quick Setup & Run**
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Application**:
   ```bash
   streamlit run app/main.py
   ```
3. **Deploy to Cloud**:
   Fully compatible with **Streamlit Community Cloud** and **Railway.app**.

---

## 🏛️ Core Modules

### **� Options Engine**
Numerical and analytical pricing of European derivatives.
- **Methods**: Black-Scholes-Merton & High-Performance Parallel Monte Carlo.
- **Analytics**: Complete Greeks suite (Δ, Γ, ν, θ, ρ, Vanna, Volga) and convergence analysis.
- **Resilience**: Advanced variance reduction techniques (Antithetic, Control Variates).

### **�️ Portfolio Optimizer**
Strategic asset allocation and risk management.
- **Optimization**: Modern Portfolio Theory (Markowitz), Risk Parity, and Inverse Volatility.
- **Performance**: Backtesting engine with rebalancing, Max Drawdown, and Sharpe Ratio analysis.
- **Visuals**: Dynamic Efficient Frontier and Risk Contribution decomposition.

### **🧬 Factor Analysis**
Return decomposition using leading academic risk models.
- **Models**: Fama-French 3-Factor (1993) and 5-Factor (2015) implementations.
- **Data**: Real-time integration with Yahoo Finance and the Ken French Data Library.
- **Insights**: Statistical Alpha/Beta decomposition and factor exposure reporting.

---

## 🛠️ Technology Stack
- **Engine**: NumPy, Pandas, SciPy, Statsmodels.
- **UI/UX**: Streamlit, Plotly (Dynamic Visualizations), Custom Vanilla CSS.
- **Testing**: PyTest with 112+ verified test cases covering numerical accuracy.
- **Deployment**: Docker, Railway, Streamlit Cloud.

---

## 📂 Project Structure
For detailed technical information, please refer to the organized documentation in the `/docs` directory:

- 📖 **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)**: How to use the platform.
- 🧮 **[docs/COMPREHENSIVE_DOCUMENTATION.md](docs/COMPREHENSIVE_DOCUMENTATION.md)**: Deep dive into the math and APIs.
- � **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**: Cloud deployment blueprints.
- 🛡️ **[docs/BUG_FIXES_REPORT_JAN2026.md](docs/BUG_FIXES_REPORT_JAN2026.md)**: Recent system hardening details.

---

## 🧪 Development & Testing
To run the automated suite and verify numerical convergence:
```bash
pytest tests/
```

Individual module verification:
```bash
python options/black_scholes.py
python portfolio/markowitz.py
python factors/ff3_model.py
```

---

## 📜 Principles & Goals
These implementations are designed for **transparency and education**. While high-performance and stable, the codebase is architected to be readable, with mathematical formulas derived in-line where possible.

**License**: MIT 
**Status**: v1.0.0 Production Stable ✅
