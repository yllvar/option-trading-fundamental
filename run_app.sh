#!/bin/bash

# Quant Fundamentals - Streamlit App Launcher
# Quick start script for running the web interface

echo "🚀 Starting Quant Fundamentals Web Interface..."
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run the app
echo "✅ Launching app at http://localhost:8501"
echo ""
echo "📊 Features available:"
echo "  - Options Pricing (Black-Scholes, Monte Carlo)"
echo "  - Greeks Calculation"
echo "  - Interactive Visualizations"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app/main.py
