"""
Input validation utilities for quant-fundamentals.
Provides comprehensive parameter validation with helpful error messages.
"""
# Version: 2026-01-11 11:15

import numpy as np
import pandas as pd
from typing import Union, Optional


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


def validate_positive(value: float, name: str) -> None:
    """
    Validate that a value is positive.
    
    Parameters:
    -----------
    value : float
        Value to validate
    name : str
        Parameter name for error message
    
    Raises:
    -------
    ValidationError : If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")


def validate_non_negative(value: float, name: str) -> None:
    """
    Validate that a value is non-negative.
    
    Parameters:
    -----------
    value : float
        Value to validate
    name : str
        Parameter name for error message
    
    Raises:
    -------
    ValidationError : If value is negative
    """
    if value < 0:
        raise ValidationError(f"{name} must be non-negative, got {value}")


def validate_probability(value: float, name: str) -> None:
    """
    Validate that a value is a valid probability [0, 1].
    
    Parameters:
    -----------
    value : float
        Value to validate
    name : str
        Parameter name for error message
    
    Raises:
    -------
    ValidationError : If value is not in [0, 1]
    """
    if not 0 <= value <= 1:
        raise ValidationError(f"{name} must be in [0, 1], got {value}")


def validate_option_params(
    S0: float,
    K: float,
    r: float,
    sigma: float,
    T: float
) -> None:
    """
    Validate option pricing parameters.
    
    Parameters:
    -----------
    S0 : float
        Current stock price
    K : float
        Strike price
    r : float
        Risk-free rate
    sigma : float
        Volatility
    T : float
        Time to maturity
    
    Raises:
    -------
    ValidationError : If any parameter is invalid
    """
    validate_positive(S0, "Stock price (S0)")
    validate_positive(K, "Strike price (K)")
    validate_non_negative(r, "Risk-free rate (r)")
    validate_positive(sigma, "Volatility (sigma)")
    validate_positive(T, "Time to maturity (T)")
    
    # Additional sanity checks
    if sigma > 5.0:
        raise ValidationError(f"Volatility {sigma} seems unreasonably high (>500%)")
    
    if r > 1.0:
        raise ValidationError(f"Risk-free rate {r} seems unreasonably high (>100%)")
    
    if T > 30.0:
        raise ValidationError(f"Time to maturity {T} years seems unreasonably long")


def validate_weights(weights: np.ndarray, allow_short: bool = False) -> None:
    """
    Validate portfolio weights.
    
    Parameters:
    -----------
    weights : np.ndarray
        Portfolio weights
    allow_short : bool
        Whether short positions are allowed
    
    Raises:
    -------
    ValidationError : If weights are invalid
    """
    # Robust check for Pandas-like objects (handle potential multiple pandas imports in memory)
    if hasattr(weights, 'values'):
        weights = weights.values
        if hasattr(weights, 'flatten'):
            weights = weights.flatten()
            
    if not isinstance(weights, np.ndarray):
        raise ValidationError(f"Weights must be a numpy array or pandas Series, got {type(weights).__name__}")
    
    if weights.ndim != 1:
        raise ValidationError(f"Weights must be 1-dimensional, got shape {weights.shape}")
    
    if len(weights) == 0:
        raise ValidationError("Weights array is empty")
    
    # Check sum to 1
    weight_sum = np.sum(weights)
    if not np.isclose(weight_sum, 1.0, atol=1e-4):
        raise ValidationError(f"Weights must sum to 1, got {weight_sum}")
    
    # Check for short positions if not allowed
    if not allow_short and np.any(weights < -1e-6):
        raise ValidationError(f"Negative weights not allowed: {weights[weights < 0]}")
    
    # Check for NaN or inf
    if np.any(~np.isfinite(weights)):
        raise ValidationError("Weights contain NaN or inf values")


def validate_covariance_matrix_v3(cov_matrix):
    """
    Validate covariance matrix and return as numpy array.
    """
    # Robust check for Pandas-like objects
    if hasattr(cov_matrix, 'values') and not isinstance(cov_matrix, np.ndarray):
        cov_matrix = cov_matrix.values
        
    if not isinstance(cov_matrix, np.ndarray):
        raise ValidationError(f"Covariance matrix must be a numpy array (v3), got {type(cov_matrix).__name__}")
    
    if cov_matrix.ndim != 2:
        raise ValidationError(f"Covariance matrix must be 2D, got shape {cov_matrix.shape}")
    
    n, m = cov_matrix.shape
    if n != m:
        raise ValidationError(f"Covariance matrix must be square, got {n}x{m}")
    
    # Check symmetry
    if not np.allclose(cov_matrix, cov_matrix.T, atol=1e-8):
        raise ValidationError("Covariance matrix must be symmetric")
    
    # Check positive semi-definite
    eigenvalues = np.linalg.eigvalsh(cov_matrix)
    if np.any(eigenvalues < -1e-8):
        raise ValidationError(f"Covariance matrix must be positive semi-definite, "
                            f"got negative eigenvalue: {eigenvalues.min()}")
    
    # Check for NaN or inf
    if np.any(~np.isfinite(cov_matrix)):
        raise ValidationError("Covariance matrix contains NaN or inf values")
    
    # Check diagonal (variances) are positive
    if np.any(np.diag(cov_matrix) <= 0):
        raise ValidationError("Covariance matrix diagonal (variances) must be positive")


def validate_returns(returns: Union[np.ndarray, pd.Series]) -> None:
    """
    Validate returns data.
    
    Parameters:
    -----------
    returns : np.ndarray or pd.Series
        Returns data
    
    Raises:
    -------
    ValidationError : If returns are invalid
    """
    if hasattr(returns, 'values'):
        returns_array = returns.values
    elif isinstance(returns, np.ndarray):
        returns_array = returns
    else:
        raise ValidationError(f"Returns must be numpy array or pandas Series, got {type(returns).__name__}")
    
    if len(returns_array) == 0:
        raise ValidationError("Returns array is empty")
    
    # Check for NaN or inf
    if np.any(~np.isfinite(returns_array)):
        nan_count = np.sum(np.isnan(returns_array))
        inf_count = np.sum(np.isinf(returns_array))
        raise ValidationError(f"Returns contain {nan_count} NaN and {inf_count} inf values")
    
    # Sanity check: returns shouldn't be too extreme
    if np.any(np.abs(returns_array) > 1.0):
        extreme_count = np.sum(np.abs(returns_array) > 1.0)
        raise ValidationError(f"Returns contain {extreme_count} values > 100% "
                            f"(max: {np.max(np.abs(returns_array))*100:.1f}%)")


def validate_monte_carlo_params(n_paths: int, n_steps: int) -> None:
    """
    Validate Monte Carlo simulation parameters.
    
    Parameters:
    -----------
    n_paths : int
        Number of simulation paths
    n_steps : int
        Number of time steps
    
    Raises:
    -------
    ValidationError : If parameters are invalid
    """
    if not isinstance(n_paths, int):
        raise ValidationError(f"n_paths must be an integer, got {type(n_paths)}")
    
    if not isinstance(n_steps, int):
        raise ValidationError(f"n_steps must be an integer, got {type(n_steps)}")
    
    if n_paths < 100:
        raise ValidationError(f"n_paths should be at least 100 for reasonable accuracy, got {n_paths}")
    
    if n_steps < 10:
        raise ValidationError(f"n_steps should be at least 10, got {n_steps}")
    
    if n_paths > 10_000_000:
        raise ValidationError(f"n_paths={n_paths} is too large, may cause memory issues")
    
    if n_steps > 10_000:
        raise ValidationError(f"n_steps={n_steps} is too large, may cause performance issues")


# Decorator for automatic validation
def validate_inputs(**validators):
    """
    Decorator for automatic input validation.
    
    Usage:
    ------
    @validate_inputs(S0=validate_positive, K=validate_positive)
    def my_function(S0, K):
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    try:
                        validator(value, param_name)
                    except ValidationError as e:
                        raise ValidationError(f"In {func.__name__}(): {e}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test validation functions
    print("Testing validation functions...")
    
    # Test positive validation
    try:
        validate_positive(-1, "test_value")
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test option params
    try:
        validate_option_params(100, 100, 0.05, 0.20, 1.0)
        print("✓ Valid option params passed")
    except ValidationError as e:
        print(f"ERROR: {e}")
    
    # Test invalid volatility
    try:
        validate_option_params(100, 100, 0.05, 10.0, 1.0)
        print("ERROR: Should have raised ValidationError for high volatility")
    except ValidationError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test weights
    try:
        weights = np.array([0.3, 0.3, 0.4])
        validate_weights(weights)
        print("✓ Valid weights passed")
    except ValidationError as e:
        print(f"ERROR: {e}")
    
    # Test invalid weights (don't sum to 1)
    try:
        weights = np.array([0.3, 0.3, 0.3])
        validate_weights(weights)
        print("ERROR: Should have raised ValidationError for weights not summing to 1")
    except ValidationError as e:
        print(f"✓ Caught expected error: {e}")
    
    print("\nAll validation tests passed!")
