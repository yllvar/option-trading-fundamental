"""
Unit tests for Phase 3 components.
Tests scenario analysis, comparison tools, and advanced charts.
"""

import pytest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from components.scenario_analysis import (
    options_scenario_analysis,
    create_scenario_heatmap,
    portfolio_scenario_analysis,
    create_stress_test_chart
)
from components.comparison_tools import (
    compare_options,
    create_options_comparison_chart,
    compare_portfolios,
    create_portfolio_comparison_chart,
    compare_factor_models,
    create_beta_comparison_chart
)
from components.advanced_charts import (
    create_volatility_surface_3d,
    create_correlation_heatmap_enhanced,
    create_risk_decomposition_chart,
    create_efficient_frontier_enhanced,
    create_factor_exposure_radar
)


class TestScenarioAnalysis:
    """Test scenario analysis functionality."""
    
    def test_options_scenario_analysis(self):
        """Test options scenario analysis."""
        def pricing_func(S, K, r, sigma, T):
            # Simple BS approximation for testing
            return max(S - K, 0) + 0.4 * S * sigma * np.sqrt(T)
        
        scenario_df = options_scenario_analysis(
            S0=100, K=100, r=0.05, sigma=0.2, T=1.0,
            option_type='Call', pricing_func=pricing_func
        )
        
        assert isinstance(scenario_df, pd.DataFrame)
        assert len(scenario_df) > 0
        assert 'Scenario' in scenario_df.columns
        assert 'Option Price' in scenario_df.columns
        assert 'Change' in scenario_df.columns
        assert 'Change %' in scenario_df.columns
        
        # Should have base case
        assert any('Base Case' in str(s) for s in scenario_df['Scenario'])
    
    def test_create_scenario_heatmap(self):
        """Test scenario heatmap creation."""
        def pricing_func(S, K, r, sigma, T):
            return max(S - K, 0)
        
        S_range = np.linspace(80, 120, 10)
        vol_range = np.linspace(0.1, 0.3, 10)
        
        fig = create_scenario_heatmap(S_range, vol_range, pricing_func, K=100, r=0.05, T=1.0)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_portfolio_scenario_analysis(self):
        """Test portfolio scenario analysis."""
        weights = np.array([0.4, 0.3, 0.3])
        mean_returns = np.array([0.10, 0.12, 0.08])
        cov_matrix = np.array([
            [0.04, 0.006, 0.008],
            [0.006, 0.0225, 0.00525],
            [0.008, 0.00525, 0.0625]
        ])
        asset_names = ['Asset A', 'Asset B', 'Asset C']
        
        scenario_df = portfolio_scenario_analysis(weights, mean_returns, cov_matrix, asset_names)
        
        assert isinstance(scenario_df, pd.DataFrame)
        assert len(scenario_df) > 0
        assert 'Scenario' in scenario_df.columns
        assert 'Return' in scenario_df.columns
        assert 'Volatility' in scenario_df.columns
        assert 'Sharpe' in scenario_df.columns
        
        # Should have base case
        assert any('Base Case' in str(s) for s in scenario_df['Scenario'])
    
    def test_create_stress_test_chart(self):
        """Test stress test chart creation."""
        scenario_df = pd.DataFrame({
            'Scenario': ['Base', 'Stress 1', 'Stress 2'],
            'Return Change': ['+0.0%', '+10.0%', '-15.0%'],
            'Vol Change': ['+0.0%', '+20.0%', '+30.0%'],
            'Sharpe Change': ['+0.0%', '-5.0%', '-25.0%']
        })
        
        fig = create_stress_test_chart(scenario_df)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestComparisonTools:
    """Test comparison tools functionality."""
    
    def test_compare_options(self):
        """Test options comparison."""
        options_list = [
            {
                'params': {'option_type': 'Call', 'S0': 100, 'K': 100, 'sigma': 0.2, 'T': 1.0, 'method': 'BS'},
                'results': {'price': 10.45, 'delta': 0.52, 'gamma': 0.015, 'vega': 38.5, 'theta': -5.2, 'rho': 45.3}
            },
            {
                'params': {'option_type': 'Put', 'S0': 100, 'K': 100, 'sigma': 0.2, 'T': 1.0, 'method': 'BS'},
                'results': {'price': 5.57, 'delta': -0.48, 'gamma': 0.015, 'vega': 38.5, 'theta': -2.8, 'rho': -49.7}
            }
        ]
        
        comparison_df = compare_options(options_list)
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 2
        assert 'Option' in comparison_df.columns
        assert 'Type' in comparison_df.columns
        assert 'Price' in comparison_df.columns
        assert 'Delta' in comparison_df.columns
    
    def test_create_options_comparison_chart(self):
        """Test options comparison chart."""
        options_list = [
            {'params': {}, 'results': {'price': 10.45}},
            {'params': {}, 'results': {'price': 5.57}}
        ]
        
        fig = create_options_comparison_chart(options_list, metric='price')
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_compare_portfolios(self):
        """Test portfolio comparison."""
        portfolios_list = [
            {
                'name': 'Max Sharpe',
                'weights': np.array([0.4, 0.3, 0.3]),
                'return': 0.12,
                'volatility': 0.18,
                'sharpe': 0.56
            },
            {
                'name': 'Min Variance',
                'weights': np.array([0.2, 0.5, 0.3]),
                'return': 0.10,
                'volatility': 0.15,
                'sharpe': 0.53
            }
        ]
        
        comparison_df = compare_portfolios(portfolios_list)
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 2
        assert 'Portfolio' in comparison_df.columns
        assert 'Return' in comparison_df.columns
        assert 'Sharpe Ratio' in comparison_df.columns
    
    def test_create_portfolio_comparison_chart(self):
        """Test portfolio comparison chart."""
        portfolios_list = [
            {'name': 'P1', 'return': 0.12, 'volatility': 0.18, 'sharpe': 0.56, 'weights': [0.5, 0.5]},
            {'name': 'P2', 'return': 0.10, 'volatility': 0.15, 'sharpe': 0.53, 'weights': [0.3, 0.7]}
        ]
        
        fig = create_portfolio_comparison_chart(portfolios_list)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_compare_factor_models(self):
        """Test factor model comparison."""
        models_list = [
            {
                'ticker': 'AAPL',
                'model': 'FF3',
                'alpha': 0.02,
                'r_squared': 0.65,
                'betas': {'Mkt-RF': 1.2, 'SMB': 0.3, 'HML': -0.2}
            },
            {
                'ticker': 'MSFT',
                'model': 'FF3',
                'alpha': 0.015,
                'r_squared': 0.70,
                'betas': {'Mkt-RF': 1.1, 'SMB': 0.2, 'HML': -0.1}
            }
        ]
        
        comparison_df = compare_factor_models(models_list)
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 2
        assert 'Stock' in comparison_df.columns
        assert 'Alpha' in comparison_df.columns
        assert 'Market Beta' in comparison_df.columns
    
    def test_create_beta_comparison_chart(self):
        """Test beta comparison chart."""
        models_list = [
            {'ticker': 'AAPL', 'betas': {'Mkt-RF': 1.2, 'SMB': 0.3}},
            {'ticker': 'MSFT', 'betas': {'Mkt-RF': 1.1, 'SMB': 0.2}}
        ]
        
        fig = create_beta_comparison_chart(models_list)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestAdvancedCharts:
    """Test advanced chart creation."""
    
    def test_create_volatility_surface_3d(self):
        """Test 3D volatility surface creation."""
        strikes = np.linspace(80, 120, 10)
        maturities = np.linspace(0.25, 2.0, 10)
        
        # Create sample price surface
        prices = np.outer(maturities, strikes - 100) + 10
        
        fig = create_volatility_surface_3d(strikes, maturities, prices)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == 'surface'
    
    def test_create_correlation_heatmap_enhanced(self):
        """Test enhanced correlation heatmap."""
        corr_matrix = np.array([
            [1.0, 0.3, 0.5],
            [0.3, 1.0, 0.4],
            [0.5, 0.4, 1.0]
        ])
        labels = ['Asset A', 'Asset B', 'Asset C']
        
        fig = create_correlation_heatmap_enhanced(corr_matrix, labels)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == 'heatmap'
    
    def test_create_risk_decomposition_chart(self):
        """Test risk decomposition chart."""
        weights = np.array([0.4, 0.3, 0.3])
        risk_contributions = np.array([0.35, 0.30, 0.35])
        labels = ['Asset A', 'Asset B', 'Asset C']
        
        fig = create_risk_decomposition_chart(weights, risk_contributions, labels)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_create_efficient_frontier_enhanced(self):
        """Test enhanced efficient frontier."""
        frontier_returns = np.linspace(0.08, 0.15, 20)
        frontier_vols = np.linspace(0.12, 0.25, 20)
        frontier_sharpes = (frontier_returns - 0.02) / frontier_vols
        
        optimal_return = 0.12
        optimal_vol = 0.18
        
        asset_returns = np.array([0.10, 0.12, 0.08])
        asset_vols = np.array([0.20, 0.25, 0.15])
        asset_names = ['A', 'B', 'C']
        
        fig = create_efficient_frontier_enhanced(
            frontier_returns, frontier_vols, frontier_sharpes,
            optimal_return, optimal_vol,
            asset_returns, asset_vols, asset_names
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
    
    def test_create_factor_exposure_radar(self):
        """Test factor exposure radar chart."""
        betas = {'Mkt-RF': 1.2, 'SMB': 0.3, 'HML': -0.2}
        factor_names = list(betas.keys())
        
        fig = create_factor_exposure_radar(betas, factor_names)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == 'scatterpolar'


class TestEdgeCases:
    """Test edge cases for components."""
    
    def test_scenario_analysis_with_errors(self):
        """Test scenario analysis handles pricing errors gracefully."""
        def failing_pricing_func(S, K, r, sigma, T):
            if S > 110:
                raise ValueError("Price too high")
            return max(S - K, 0)
        
        # Should not raise, just skip failed scenarios
        scenario_df = options_scenario_analysis(
            S0=100, K=100, r=0.05, sigma=0.2, T=1.0,
            option_type='Call', pricing_func=failing_pricing_func
        )
        
        assert isinstance(scenario_df, pd.DataFrame)
        # Some scenarios should succeed
        assert len(scenario_df) > 0
    
    def test_comparison_with_empty_list(self):
        """Test comparison with empty list."""
        comparison_df = compare_options([])
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 0
    
    def test_comparison_with_single_item(self):
        """Test comparison with single item."""
        options_list = [
            {'params': {'option_type': 'Call'}, 'results': {'price': 10}}
        ]
        
        comparison_df = compare_options(options_list)
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
