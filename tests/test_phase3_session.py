"""
Unit tests for Phase 3 session state management.
Tests history tracking, preferences, caching, and comparison mode.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

# Mock streamlit
sys.modules['streamlit'] = MagicMock()
import streamlit as st

from utils.session_state import (
    init_session_state,
    add_to_history,
    get_history,
    clear_history,
    get_history_dataframe,
    add_to_comparison,
    remove_from_comparison,
    clear_comparison,
    get_comparison_items,
    set_preference,
    get_preference,
    CalculationCache
)


class TestSessionStateInitialization:
    """Test session state initialization."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
    
    def test_init_session_state(self):
        """Test session state initialization."""
        init_session_state()
        
        assert 'calculation_history' in st.session_state
        assert 'options_history' in st.session_state
        assert 'portfolio_history' in st.session_state
        assert 'factor_history' in st.session_state
        assert 'preferences' in st.session_state
        assert 'comparison_mode' in st.session_state
        assert 'comparison_items' in st.session_state
    
    def test_init_session_state_idempotent(self):
        """Test that init_session_state can be called multiple times."""
        init_session_state()
        init_session_state()
        
        # Should not raise error and state should exist
        assert 'calculation_history' in st.session_state


class TestHistoryManagement:
    """Test history tracking functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
        init_session_state()
    
    def test_add_to_history_options(self):
        """Test adding options calculation to history."""
        params = {'S0': 100, 'K': 100, 'r': 0.05, 'sigma': 0.2, 'T': 1.0}
        results = {'price': 10.45, 'delta': 0.52}
        
        add_to_history('options', params, results)
        
        assert len(st.session_state.calculation_history) == 1
        assert len(st.session_state.options_history) == 1
        
        entry = st.session_state.options_history[0]
        assert entry['type'] == 'options'
        assert entry['params'] == params
        assert entry['results'] == results
    
    def test_add_to_history_portfolio(self):
        """Test adding portfolio calculation to history."""
        params = {'method': 'max_sharpe'}
        results = {'return': 0.12, 'volatility': 0.18, 'sharpe': 0.56}
        
        add_to_history('portfolio', params, results)
        
        assert len(st.session_state.portfolio_history) == 1
        assert st.session_state.portfolio_history[0]['type'] == 'portfolio'
    
    def test_add_to_history_factors(self):
        """Test adding factor analysis to history."""
        params = {'model': 'FF3', 'ticker': 'AAPL'}
        results = {'alpha': 0.02, 'r_squared': 0.65}
        
        add_to_history('factors', params, results)
        
        assert len(st.session_state.factor_history) == 1
        assert st.session_state.factor_history[0]['type'] == 'factors'
    
    def test_get_history_all(self):
        """Test getting all history."""
        add_to_history('options', {'S0': 100}, {'price': 10})
        add_to_history('portfolio', {'method': 'sharpe'}, {'return': 0.12})
        
        history = get_history()
        
        assert len(history) == 2
    
    def test_get_history_by_type(self):
        """Test getting history by type."""
        add_to_history('options', {'S0': 100}, {'price': 10})
        add_to_history('portfolio', {'method': 'sharpe'}, {'return': 0.12})
        
        options_history = get_history('options')
        portfolio_history = get_history('portfolio')
        
        assert len(options_history) == 1
        assert len(portfolio_history) == 1
        assert options_history[0]['type'] == 'options'
        assert portfolio_history[0]['type'] == 'portfolio'
    
    def test_clear_history_all(self):
        """Test clearing all history."""
        add_to_history('options', {}, {})
        add_to_history('portfolio', {}, {})
        
        clear_history()
        
        assert len(st.session_state.calculation_history) == 0
        assert len(st.session_state.options_history) == 0
        assert len(st.session_state.portfolio_history) == 0
    
    def test_clear_history_by_type(self):
        """Test clearing history by type."""
        add_to_history('options', {}, {})
        add_to_history('portfolio', {}, {})
        
        clear_history('options')
        
        assert len(st.session_state.options_history) == 0
        assert len(st.session_state.portfolio_history) == 1
    
    def test_history_limit(self):
        """Test that history is limited to 50 entries."""
        # Add 60 entries
        for i in range(60):
            add_to_history('options', {'i': i}, {'result': i})
        
        # Should keep only last 50
        assert len(st.session_state.calculation_history) == 50
        # First entry should be from iteration 10 (0-9 removed)
        assert st.session_state.calculation_history[0]['params']['i'] == 10
    
    def test_get_history_dataframe_options(self):
        """Test getting history as DataFrame for options."""
        add_to_history('options', 
                      {'option_type': 'Call', 'method': 'BS'},
                      {'price': 10.45})
        
        df = get_history_dataframe('options')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert 'Option Type' in df.columns
        assert 'Price' in df.columns
    
    def test_get_history_dataframe_empty(self):
        """Test getting empty history DataFrame."""
        df = get_history_dataframe('options')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestComparisonMode:
    """Test comparison mode functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
        init_session_state()
    
    def test_add_to_comparison(self):
        """Test adding item to comparison."""
        item_data = {'price': 10.45, 'delta': 0.52}
        
        add_to_comparison('item1', item_data)
        
        items = get_comparison_items()
        assert len(items) == 1
        assert items[0]['id'] == 'item1'
        assert items[0]['data'] == item_data
    
    def test_add_duplicate_to_comparison(self):
        """Test that duplicate IDs are not added."""
        add_to_comparison('item1', {'price': 10})
        add_to_comparison('item1', {'price': 20})
        
        items = get_comparison_items()
        assert len(items) == 1
    
    def test_remove_from_comparison(self):
        """Test removing item from comparison."""
        add_to_comparison('item1', {'price': 10})
        add_to_comparison('item2', {'price': 20})
        
        remove_from_comparison('item1')
        
        items = get_comparison_items()
        assert len(items) == 1
        assert items[0]['id'] == 'item2'
    
    def test_clear_comparison(self):
        """Test clearing comparison list."""
        add_to_comparison('item1', {})
        add_to_comparison('item2', {})
        
        clear_comparison()
        
        items = get_comparison_items()
        assert len(items) == 0


class TestPreferences:
    """Test user preferences functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
        init_session_state()
    
    def test_set_preference(self):
        """Test setting preference."""
        set_preference('theme', 'dark')
        
        assert st.session_state.preferences['theme'] == 'dark'
    
    def test_get_preference(self):
        """Test getting preference."""
        set_preference('risk_free_rate', 0.03)
        
        value = get_preference('risk_free_rate')
        assert value == 0.03
    
    def test_get_preference_default(self):
        """Test getting preference with default."""
        value = get_preference('nonexistent', default=0.02)
        
        assert value == 0.02
    
    def test_get_preference_none(self):
        """Test getting nonexistent preference without default."""
        value = get_preference('nonexistent')
        
        assert value is None


class TestCalculationCache:
    """Test calculation caching functionality."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
    
    def test_cache_set_and_get(self):
        """Test setting and getting cached result."""
        params = {'S0': 100, 'K': 100, 'r': 0.05}
        result = {'price': 10.45}
        
        CalculationCache.set('options', params, result)
        cached = CalculationCache.get('options', params)
        
        assert cached is not None
        assert cached['result'] == result
    
    def test_cache_miss(self):
        """Test cache miss."""
        params = {'S0': 100}
        
        cached = CalculationCache.get('options', params)
        
        assert cached is None
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        params1 = {'S0': 100, 'K': 100}
        params2 = {'K': 100, 'S0': 100}  # Different order
        
        key1 = CalculationCache.get_cache_key('options', params1)
        key2 = CalculationCache.get_cache_key('options', params2)
        
        # Should generate same key regardless of order
        assert key1 == key2
    
    def test_cache_limit(self):
        """Test cache size limit."""
        # Add 110 entries (limit is 100)
        for i in range(110):
            CalculationCache.set('test', {'i': i}, {'result': i})
        
        # Should keep only 90 (removes oldest 20)
        assert len(st.session_state.calc_cache) == 90
    
    def test_cache_clear(self):
        """Test clearing cache."""
        CalculationCache.set('test', {'a': 1}, {'result': 1})
        
        CalculationCache.clear()
        
        assert 'calc_cache' not in st.session_state or len(st.session_state.calc_cache) == 0


class TestEdgeCases:
    """Test edge cases for session state."""
    
    def setup_method(self):
        """Reset session state before each test."""
        st.session_state = {}
        init_session_state()
    
    def test_add_history_with_complex_data(self):
        """Test adding history with complex nested data."""
        params = {
            'nested': {'a': 1, 'b': 2},
            'list': [1, 2, 3]
        }
        results = {
            'array': [1.0, 2.0, 3.0],
            'dict': {'x': 10}
        }
        
        add_to_history('options', params, results)
        
        history = get_history('options')
        assert len(history) == 1
        assert history[0]['params']['nested']['a'] == 1
    
    def test_cache_with_float_params(self):
        """Test caching with floating point parameters."""
        params = {'S0': 100.0, 'sigma': 0.2}
        result = {'price': 10.45}
        
        CalculationCache.set('options', params, result)
        cached = CalculationCache.get('options', params)
        
        assert cached is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
