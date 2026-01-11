"""
Unit tests for Phase 3 export utilities.
Tests CSV/JSON export, formatting, and download link generation.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from utils.export import (
    export_to_csv,
    export_to_json,
    format_results_for_export,
    export_chart_data,
    ExportManager
)


class TestExportUtilities:
    """Test export utility functions."""
    
    def test_export_to_csv_from_dict(self):
        """Test CSV export from dictionary."""
        data = {
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Value': [100, 200, 300]
        }
        
        csv_result = export_to_csv(data)
        
        assert isinstance(csv_result, str)
        assert 'Name,Value' in csv_result
        assert 'Alice,100' in csv_result
        assert 'Bob,200' in csv_result
    
    def test_export_to_csv_from_dataframe(self):
        """Test CSV export from DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        
        csv_result = export_to_csv(df)
        
        assert isinstance(csv_result, str)
        assert 'A,B' in csv_result
        assert '1,4' in csv_result
    
    def test_export_to_json_from_dict(self):
        """Test JSON export from dictionary."""
        data = {
            'name': 'Test',
            'value': 123,
            'nested': {'key': 'value'}
        }
        
        json_result = export_to_json(data)
        
        assert isinstance(json_result, str)
        parsed = json.loads(json_result)
        assert parsed['name'] == 'Test'
        assert parsed['value'] == 123
        assert parsed['nested']['key'] == 'value'
    
    def test_export_to_json_from_dataframe(self):
        """Test JSON export from DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2],
            'B': [3, 4]
        })
        
        json_result = export_to_json(df)
        
        assert isinstance(json_result, str)
        parsed = json.loads(json_result)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
    
    def test_format_results_for_export_options(self):
        """Test formatting options results for export."""
        results = {
            'S0': 100.0,
            'K': 100.0,
            'r': 0.05,
            'sigma': 0.20,
            'T': 1.0,
            'option_type': 'Call',
            'price': 10.45,
            'delta': 0.52,
            'gamma': 0.015,
            'vega': 38.5,
            'theta': -5.2,
            'rho': 45.3
        }
        
        df = format_results_for_export(results, 'options')
        
        assert isinstance(df, pd.DataFrame)
        assert 'Timestamp' in df.columns
        assert 'Option Price' in df.columns
        assert df['Option Price'].iloc[0] == 10.45
    
    def test_format_results_for_export_portfolio(self):
        """Test formatting portfolio results for export."""
        results = {
            'weights': [0.3, 0.3, 0.4],
            'assets': ['AAPL', 'MSFT', 'GOOGL'],
            'return': 0.12,
            'volatility': 0.18,
            'sharpe': 0.56
        }
        
        allocation_df, summary_df = format_results_for_export(results, 'portfolio')
        
        assert isinstance(allocation_df, pd.DataFrame)
        assert isinstance(summary_df, pd.DataFrame)
        assert len(allocation_df) == 3
        assert 'Asset' in allocation_df.columns
        assert 'Weight' in allocation_df.columns
    
    def test_format_results_for_export_factors(self):
        """Test formatting factor results for export."""
        results = {
            'betas': {'Mkt-RF': 1.2, 'SMB': 0.3, 'HML': -0.2},
            'beta_t_stats': {'Mkt-RF': 5.2, 'SMB': 2.1, 'HML': -1.5},
            'beta_p_values': {'Mkt-RF': 0.001, 'SMB': 0.04, 'HML': 0.13},
            'alpha': 0.02,
            'alpha_t_stat': 1.8,
            'alpha_p_value': 0.07,
            'r_squared': 0.65
        }
        
        betas_df, alpha_df = format_results_for_export(results, 'factors')
        
        assert isinstance(betas_df, pd.DataFrame)
        assert isinstance(alpha_df, pd.DataFrame)
        assert len(betas_df) == 3
        assert 'Factor' in betas_df.columns
        assert 'Beta' in betas_df.columns


class TestExportManager:
    """Test ExportManager class."""
    
    def test_export_manager_initialization(self):
        """Test ExportManager initialization."""
        manager = ExportManager()
        
        assert hasattr(manager, 'export_history')
        assert isinstance(manager.export_history, list)
        assert len(manager.export_history) == 0
    
    def test_add_export(self):
        """Test adding export to history."""
        manager = ExportManager()
        
        manager.add_export('csv', 'test.csv', 1024)
        
        assert len(manager.export_history) == 1
        assert manager.export_history[0]['type'] == 'csv'
        assert manager.export_history[0]['filename'] == 'test.csv'
        assert manager.export_history[0]['size'] == 1024
    
    def test_get_history(self):
        """Test getting export history."""
        manager = ExportManager()
        
        manager.add_export('csv', 'file1.csv', 100)
        manager.add_export('json', 'file2.json', 200)
        
        history_df = manager.get_history()
        
        assert isinstance(history_df, pd.DataFrame)
        assert len(history_df) == 2
        assert 'type' in history_df.columns
        assert 'filename' in history_df.columns
    
    def test_clear_history(self):
        """Test clearing export history."""
        manager = ExportManager()
        
        manager.add_export('csv', 'test.csv', 100)
        assert len(manager.export_history) == 1
        
        manager.clear_history()
        assert len(manager.export_history) == 0


class TestExportEdgeCases:
    """Test edge cases for export utilities."""
    
    def test_export_empty_dataframe(self):
        """Test exporting empty DataFrame."""
        df = pd.DataFrame()
        
        csv_result = export_to_csv(df)
        
        assert isinstance(csv_result, str)
        assert len(csv_result) > 0  # Should have headers
    
    def test_export_with_special_characters(self):
        """Test exporting data with special characters."""
        data = {
            'Name': ['Test, Inc.', 'Test "Quote"', 'Test\nNewline'],
            'Value': [1, 2, 3]
        }
        
        csv_result = export_to_csv(data)
        
        assert isinstance(csv_result, str)
        # CSV should handle special characters
        assert 'Test' in csv_result
    
    def test_export_with_none_values(self):
        """Test exporting data with None values."""
        data = {
            'A': [1, None, 3],
            'B': [None, 2, None]
        }
        
        csv_result = export_to_csv(data)
        json_result = export_to_json(data)
        
        assert isinstance(csv_result, str)
        assert isinstance(json_result, str)
    
    def test_export_large_numbers(self):
        """Test exporting large numbers."""
        data = {
            'Value': [1e10, 1e-10, 1.23456789012345]
        }
        
        csv_result = export_to_csv(data)
        
        assert isinstance(csv_result, str)
        assert '1' in csv_result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
