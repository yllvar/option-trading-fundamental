"""
Session state management for Streamlit app.
Handles calculation history, user preferences, and state persistence.
"""

import streamlit as st
from datetime import datetime
import pandas as pd


def init_session_state():
    """Initialize session state variables."""
    
    # Calculation history
    if 'calculation_history' not in st.session_state:
        st.session_state.calculation_history = []
    
    # Options history
    if 'options_history' not in st.session_state:
        st.session_state.options_history = []
    
    # Portfolio history
    if 'portfolio_history' not in st.session_state:
        st.session_state.portfolio_history = []
    
    # Factor analysis history
    if 'factor_history' not in st.session_state:
        st.session_state.factor_history = []
    
    # User preferences
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            'theme': 'light',
            'default_risk_free_rate': 0.02,
            'default_paths': 100000,
            'show_advanced': False
        }
    
    # Comparison mode
    if 'comparison_mode' not in st.session_state:
        st.session_state.comparison_mode = False
    
    # Selected items for comparison
    if 'comparison_items' not in st.session_state:
        st.session_state.comparison_items = []


def add_to_history(calculation_type, params, results):
    """
    Add calculation to history.
    
    Parameters:
    -----------
    calculation_type : str
        Type of calculation (options, portfolio, factors)
    params : dict
        Input parameters
    results : dict
        Calculation results
    """
    entry = {
        'timestamp': datetime.now(),
        'type': calculation_type,
        'params': params.copy(),
        'results': results.copy()
    }
    
    # Add to general history
    st.session_state.calculation_history.append(entry)
    
    # Add to specific history
    if calculation_type == 'options':
        st.session_state.options_history.append(entry)
    elif calculation_type == 'portfolio':
        st.session_state.portfolio_history.append(entry)
    elif calculation_type == 'factors':
        st.session_state.factor_history.append(entry)
    
    # Keep only last 50 entries
    if len(st.session_state.calculation_history) > 50:
        st.session_state.calculation_history = st.session_state.calculation_history[-50:]


def get_history(calculation_type=None):
    """
    Get calculation history.
    
    Parameters:
    -----------
    calculation_type : str, optional
        Filter by type (options, portfolio, factors)
        
    Returns:
    --------
    list : History entries
    """
    if calculation_type is None:
        return st.session_state.calculation_history
    elif calculation_type == 'options':
        return st.session_state.options_history
    elif calculation_type == 'portfolio':
        return st.session_state.portfolio_history
    elif calculation_type == 'factors':
        return st.session_state.factor_history
    else:
        return []


def clear_history(calculation_type=None):
    """
    Clear calculation history.
    
    Parameters:
    -----------
    calculation_type : str, optional
        Clear specific type or all if None
    """
    if calculation_type is None:
        st.session_state.calculation_history = []
        st.session_state.options_history = []
        st.session_state.portfolio_history = []
        st.session_state.factor_history = []
    elif calculation_type == 'options':
        st.session_state.options_history = []
    elif calculation_type == 'portfolio':
        st.session_state.portfolio_history = []
    elif calculation_type == 'factors':
        st.session_state.factor_history = []


def get_history_dataframe(calculation_type=None):
    """
    Get history as DataFrame.
    
    Parameters:
    -----------
    calculation_type : str, optional
        Filter by type
        
    Returns:
    --------
    pd.DataFrame : History as dataframe
    """
    history = get_history(calculation_type)
    
    if not history:
        return pd.DataFrame()
    
    # Extract key information
    data = []
    for entry in history:
        row = {
            'Timestamp': entry['timestamp'],
            'Type': entry['type']
        }
        
        # Add type-specific info
        if entry['type'] == 'options':
            row['Option Type'] = entry['params'].get('option_type', 'N/A')
            row['Price'] = entry['results'].get('price', 'N/A')
            row['Method'] = entry['params'].get('method', 'N/A')
        
        elif entry['type'] == 'portfolio':
            row['Method'] = entry['params'].get('method', 'N/A')
            row['Return'] = entry['results'].get('return', 'N/A')
            row['Sharpe'] = entry['results'].get('sharpe', 'N/A')
        
        elif entry['type'] == 'factors':
            row['Model'] = entry['params'].get('model', 'N/A')
            row['Alpha'] = entry['results'].get('alpha', 'N/A')
            row['R-squared'] = entry['results'].get('r_squared', 'N/A')
        
        data.append(row)
    
    return pd.DataFrame(data)


def add_to_comparison(item_id, item_data):
    """
    Add item to comparison list.
    
    Parameters:
    -----------
    item_id : str
        Unique identifier
    item_data : dict
        Item data
    """
    if item_id not in [item['id'] for item in st.session_state.comparison_items]:
        st.session_state.comparison_items.append({
            'id': item_id,
            'data': item_data,
            'added_at': datetime.now()
        })


def remove_from_comparison(item_id):
    """Remove item from comparison list."""
    st.session_state.comparison_items = [
        item for item in st.session_state.comparison_items
        if item['id'] != item_id
    ]


def clear_comparison():
    """Clear comparison list."""
    st.session_state.comparison_items = []


def get_comparison_items():
    """Get items in comparison list."""
    return st.session_state.comparison_items


def set_preference(key, value):
    """Set user preference."""
    st.session_state.preferences[key] = value


def get_preference(key, default=None):
    """Get user preference."""
    return st.session_state.preferences.get(key, default)


def toggle_comparison_mode():
    """Toggle comparison mode."""
    st.session_state.comparison_mode = not st.session_state.comparison_mode


def is_comparison_mode():
    """Check if in comparison mode."""
    return st.session_state.comparison_mode


class CalculationCache:
    """Cache for expensive calculations."""
    
    @staticmethod
    def get_cache_key(calc_type, params):
        """Generate cache key from parameters."""
        # Create sorted string of params
        param_str = '_'.join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{calc_type}_{param_str}"
    
    @staticmethod
    def get(calc_type, params):
        """Get cached result."""
        if 'calc_cache' not in st.session_state:
            st.session_state.calc_cache = {}
        
        key = CalculationCache.get_cache_key(calc_type, params)
        return st.session_state.calc_cache.get(key)
    
    @staticmethod
    def set(calc_type, params, result):
        """Cache result."""
        if 'calc_cache' not in st.session_state:
            st.session_state.calc_cache = {}
        
        key = CalculationCache.get_cache_key(calc_type, params)
        st.session_state.calc_cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        # Keep cache size manageable (max 100 entries)
        if len(st.session_state.calc_cache) > 100:
            # Remove oldest entries
            sorted_keys = sorted(
                st.session_state.calc_cache.keys(),
                key=lambda k: st.session_state.calc_cache[k]['timestamp']
            )
            for key in sorted_keys[:20]:  # Remove oldest 20
                del st.session_state.calc_cache[key]
    
    @staticmethod
    def clear():
        """Clear cache."""
        if 'calc_cache' in st.session_state:
            st.session_state.calc_cache = {}
