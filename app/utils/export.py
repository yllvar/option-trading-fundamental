"""
Export utilities for Streamlit app.
Handles exporting data to various formats (CSV, JSON, PDF).
"""

import pandas as pd
import json
from io import BytesIO, StringIO
from datetime import datetime
import base64


def export_to_csv(data, filename=None):
    """
    Export data to CSV format.
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Data to export
    filename : str, optional
        Filename for download
        
    Returns:
    --------
    str : CSV string
    """
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data
    
    return df.to_csv(index=False)


def export_to_json(data, filename=None):
    """
    Export data to JSON format.
    
    Parameters:
    -----------
    data : dict or pd.DataFrame
        Data to export
    filename : str, optional
        Filename for download
        
    Returns:
    --------
    str : JSON string
    """
    if isinstance(data, pd.DataFrame):
        data_dict = data.to_dict(orient='records')
    else:
        data_dict = data
    
    return json.dumps(data_dict, indent=2, default=str)


def create_download_link(data, filename, file_format='csv'):
    """
    Create a download link for data.
    
    Parameters:
    -----------
    data : str or bytes
        Data to download
    filename : str
        Name of file
    file_format : str
        Format (csv, json, txt)
        
    Returns:
    --------
    str : HTML download link
    """
    if isinstance(data, str):
        data = data.encode()
    
    b64 = base64.b64encode(data).decode()
    
    mime_types = {
        'csv': 'text/csv',
        'json': 'application/json',
        'txt': 'text/plain'
    }
    
    mime = mime_types.get(file_format, 'text/plain')
    
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href


def format_results_for_export(results, result_type='options'):
    """
    Format calculation results for export.
    
    Parameters:
    -----------
    results : dict
        Calculation results
    result_type : str
        Type of results (options, portfolio, factors)
        
    Returns:
    --------
    pd.DataFrame : Formatted results
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if result_type == 'options':
        data = {
            'Timestamp': [timestamp],
            'Stock Price': [results.get('S0')],
            'Strike Price': [results.get('K')],
            'Risk-Free Rate': [results.get('r')],
            'Volatility': [results.get('sigma')],
            'Time to Maturity': [results.get('T')],
            'Option Type': [results.get('option_type')],
            'Option Price': [results.get('price')],
            'Delta': [results.get('delta')],
            'Gamma': [results.get('gamma')],
            'Vega': [results.get('vega')],
            'Theta': [results.get('theta')],
            'Rho': [results.get('rho')]
        }
    
    elif result_type == 'portfolio':
        # Create allocation dataframe
        weights = results.get('weights', [])
        assets = results.get('assets', [f'Asset_{i}' for i in range(len(weights))])
        
        data = {
            'Timestamp': [timestamp] * len(assets),
            'Asset': assets,
            'Weight': weights,
            'Weight %': [w * 100 for w in weights]
        }
        
        # Add summary row
        summary = pd.DataFrame({
            'Timestamp': [timestamp],
            'Metric': ['Portfolio Summary'],
            'Expected Return': [results.get('return')],
            'Volatility': [results.get('volatility')],
            'Sharpe Ratio': [results.get('sharpe')]
        })
        
        return pd.DataFrame(data), summary
    
    elif result_type == 'factors':
        betas = results.get('betas', {})
        
        data = {
            'Timestamp': [timestamp] * len(betas),
            'Factor': list(betas.keys()),
            'Beta': list(betas.values()),
            't-stat': [results.get('beta_t_stats', {}).get(f) for f in betas.keys()],
            'p-value': [results.get('beta_p_values', {}).get(f) for f in betas.keys()]
        }
        
        # Add alpha row
        alpha_row = pd.DataFrame({
            'Timestamp': [timestamp],
            'Metric': ['Alpha'],
            'Value': [results.get('alpha')],
            't-stat': [results.get('alpha_t_stat')],
            'p-value': [results.get('alpha_p_value')],
            'R-squared': [results.get('r_squared')]
        })
        
        return pd.DataFrame(data), alpha_row
    
    return pd.DataFrame(data)


def export_chart_data(fig, filename='chart_data.json'):
    """
    Export Plotly chart data.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        Plotly figure
    filename : str
        Filename for export
        
    Returns:
    --------
    str : JSON string of chart data
    """
    chart_data = {
        'data': [trace.to_plotly_json() for trace in fig.data],
        'layout': fig.layout.to_plotly_json()
    }
    
    return json.dumps(chart_data, indent=2, default=str)


class ExportManager:
    """Manage exports across the application."""
    
    def __init__(self):
        self.export_history = []
    
    def add_export(self, export_type, filename, data_size):
        """Add export to history."""
        self.export_history.append({
            'timestamp': datetime.now(),
            'type': export_type,
            'filename': filename,
            'size': data_size
        })
    
    def get_history(self):
        """Get export history."""
        return pd.DataFrame(self.export_history)
    
    def clear_history(self):
        """Clear export history."""
        self.export_history = []
