# 🚀 Deployment Blueprint: Quant Fundamentals

This comprehensive guide outlines the best strategies for deploying the **Quant Fundamentals** platform to high-availability environments.

---

## 🏛️ Recommended: Streamlit Community Cloud
**Best for: Open Source, Portfolios, and Research Sharing.**
The fastest way to go from local code to a live URL.

1.  **Push to GitHub**: Ensure your latest changes are committed and pushed.
2.  **Connect Repo**: Visit [share.streamlit.io](https://share.streamlit.io) and link your GitHub account.
3.  **Config**:
    *   **Main File**: `app/main.py`
    *   **Python Version**: `3.11`
4.  **Launch**: Click **Deploy**. Streamlit will automatically handle the `requirements.txt` and SSL certificates.

---

## 🚂 Professional: Railway.app
**Best for: Production tools requiring dedicated CPU/RAM.**
Since our Monte Carlo engine uses **Multiprocessing**, Railway allows you to scale up the virtual CPU cores for significant performance gains.

1.  **Install Railway CLI**: `npm i -g @railway/cli`
2.  **Initialize**: `railway init`
3.  **Deployment**: Railway will detect the `Dockerfile` I created. It will automatically build and expose port `8501`.
4.  **Scaling**: In the Railway dashboard, increase **CPU Shares** to 2 or 4 to unlock the full potential of the Parallel MC engine.

---

## 📦 Containerization: Docker
**Best for: Self-hosting, AWS, or GCP.**
I have provided a production-grade `Dockerfile` in the root directory.

### 1. Build and Run Locally
```bash
# Build the image
docker build -t quant-fundamentals .

# Run the container
docker run -p 8501:8501 quant-fundamentals
```

### 2. Push to Registry (GCP/AWS)
```bash
docker tag quant-fundamentals gcr.io/[PROJECT-ID]/quant-app
docker push gcr.io/[PROJECT-ID]/quant-app
```

---

## 🛠️ Deployment Checklist
- [ ] **Python Version**: Ensure environment uses `Python 3.11+`.
- [ ] **Dependencies**: Verify `requirements.txt` includes `statsmodels` and `requests`.
- [ ] **Memory**: High-intensity Portfolio Backtesting may require at least 2GB of RAM.
- [ ] **Parallel Processing**: Ensure the host allows for multiple worker processes (Standard on Railway/Docker).

---

## 🔒 Security & Secrets
If you plan to integrate authenticated data providers in the future:
1.  **Streamlit Cloud**: Use the **Secrets** manager in the dashboard.
2.  **Local/Docker**: Use a `.env` file (ensure it is in `.gitignore`).
3.  **Railway**: Use the **Variables** tab in the dashboard.

---
**Quant Fundamentals v1.0.0** | *Engineered for Stability* ✅
