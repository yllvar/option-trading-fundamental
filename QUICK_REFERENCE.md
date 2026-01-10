# Quick Reference Guide - Enhanced Features

**Quick guide to using the new testing, validation, logging, and performance features**

---

## 🧪 Running Tests

### Basic Commands
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_options.py

# Run specific test class
pytest tests/test_options.py::TestBlackScholes

# Run specific test
pytest tests/test_options.py::TestBlackScholes::test_atm_call_price

# Run tests matching pattern
pytest -k "delta" -v
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=options --cov=portfolio --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Output
```
✅ 39 tests total
✅ 23 options tests
✅ 16 portfolio tests
✅ 100% pass rate
⚡ ~5 seconds execution time
```

---

## ✅ Input Validation

### Quick Usage
```python
from utils.validation import (
    validate_option_params,
    validate_weights,
    validate_covariance_matrix,
    ValidationError
)

# Validate option parameters
try:
    validate_option_params(S0=100, K=100, r=0.05, sigma=0.20, T=1.0)
    # Proceed with calculation
except ValidationError as e:
    print(f"Invalid input: {e}")
```

### Available Validators
```python
validate_positive(value, name)              # value > 0
validate_non_negative(value, name)          # value >= 0
validate_probability(value, name)           # 0 <= value <= 1
validate_option_params(S0, K, r, sigma, T)  # All option params
validate_weights(weights, allow_short)      # Portfolio weights
validate_covariance_matrix(cov_matrix)      # Covariance matrix
validate_returns(returns)                   # Returns data
validate_monte_carlo_params(n_paths, n_steps)  # MC params
```

### Error Messages
```
ValidationError: Stock price (S0) must be positive, got -100
ValidationError: Volatility 10.0 seems unreasonably high (>500%)
ValidationError: Weights must sum to 1, got 0.9
```

---

## 📝 Logging

### Quick Setup
```python
from utils.logging_config import get_default_logger, PerformanceLogger

# Get logger for your module
logger = get_default_logger(__name__)

# Log messages
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue")
```

### Performance Logging
```python
# Time an operation
with PerformanceLogger(logger, "Monte Carlo simulation"):
    price = price_european_call(...)
# Automatically logs: "Completed: Monte Carlo simulation in 0.5234s"
```

### Log Files
- Location: `logs/quant_fundamentals_YYYYMMDD.log`
- Format: `2026-01-10 20:30:15 - module.name - INFO - message`
- Auto-created daily

---

## ⚡ Parallel Monte Carlo

### Quick Usage
```python
from options.monte_carlo_parallel import (
    price_european_call_parallel,
    price_european_put_parallel
)

# Price with automatic parallelization
price, std_err = price_european_call_parallel(
    S0=100, K=100, r=0.05, sigma=0.20, T=1.0,
    n_paths=1_000_000  # 1 million paths
)

print(f"Price: ${price:.4f} ± ${std_err:.4f}")
```

### Performance Comparison
```python
from options.monte_carlo_parallel import compare_performance

# Compare serial vs parallel
compare_performance()
```

### Expected Speedup
```
2 cores:  ~1.8x faster
4 cores:  ~3.0x faster
8 cores:  ~5.5x faster
```

---

## 🔄 Complete Example

### Validated, Logged, Parallel Pricing
```python
from options.monte_carlo_parallel import price_european_call_parallel
from utils.logging_config import get_default_logger
from utils.validation import ValidationError

# Setup
logger = get_default_logger(__name__)

try:
    # All-in-one: validation + logging + parallel execution
    price, std_err = price_european_call_parallel(
        S0=100, K=100, r=0.05, sigma=0.20, T=1.0,
        n_paths=1_000_000
    )
    
    logger.info(f"Success: ${price:.4f} ± ${std_err:.4f}")
    
except ValidationError as e:
    logger.error(f"Invalid parameters: {e}")
except Exception as e:
    logger.error(f"Calculation failed: {e}")
```

### Portfolio Optimization with All Features
```python
from portfolio.markowitz import optimize_sharpe
from utils.validation import validate_covariance_matrix, ValidationError
from utils.logging_config import get_default_logger, PerformanceLogger

logger = get_default_logger(__name__)

try:
    # Validate inputs
    validate_covariance_matrix(cov_matrix)
    
    # Optimize with performance logging
    with PerformanceLogger(logger, "Portfolio optimization"):
        result = optimize_sharpe(mean_returns, cov_matrix)
    
    logger.info(f"Sharpe ratio: {result['sharpe']:.3f}")
    
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
```

---

## 📊 Test Examples

### Test Your Own Code
```python
# tests/test_my_module.py
import pytest
import numpy as np

class TestMyFunction:
    def test_basic_case(self):
        """Test basic functionality."""
        result = my_function(100, 100)
        assert result > 0, "Result should be positive"
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValidationError):
            my_function(-100, 100)  # Should raise error
```

### Run Your Tests
```bash
pytest tests/test_my_module.py -v
```

---

## 🎯 Common Patterns

### Pattern 1: Safe Calculation
```python
from utils.validation import validate_option_params, ValidationError

def safe_price_option(S0, K, r, sigma, T):
    """Price option with validation."""
    try:
        validate_option_params(S0, K, r, sigma, T)
        return black_scholes_call(S0, K, r, sigma, T)
    except ValidationError as e:
        print(f"Error: {e}")
        return None
```

### Pattern 2: Logged Operation
```python
from utils.logging_config import get_default_logger, PerformanceLogger

logger = get_default_logger(__name__)

def logged_optimization(mean_returns, cov_matrix):
    """Optimize portfolio with logging."""
    logger.info("Starting optimization")
    
    with PerformanceLogger(logger, "Optimization"):
        result = optimize_sharpe(mean_returns, cov_matrix)
    
    logger.info(f"Completed: Sharpe={result['sharpe']:.3f}")
    return result
```

### Pattern 3: Fast Monte Carlo
```python
from options.monte_carlo_parallel import price_european_call_parallel

def fast_option_price(S0, K, r, sigma, T, n_paths=1_000_000):
    """Price option with parallel MC."""
    price, std_err = price_european_call_parallel(
        S0, K, r, sigma, T, n_paths=n_paths
    )
    
    confidence_95 = 1.96 * std_err
    return {
        'price': price,
        'lower_bound': price - confidence_95,
        'upper_bound': price + confidence_95
    }
```

---

## 🐛 Debugging

### Enable Debug Logging
```python
from utils.logging_config import setup_logger
import logging

logger = setup_logger(__name__, level=logging.DEBUG, console=True)
```

### Run Tests with Debug Output
```bash
pytest -v --log-cli-level=DEBUG
```

### Check Log Files
```bash
# View today's log
tail -f logs/quant_fundamentals_$(date +%Y%m%d).log

# Search for errors
grep ERROR logs/*.log
```

---

## 📈 Performance Tips

### Monte Carlo
```python
# Use parallel for large simulations
if n_paths > 100_000:
    price, err = price_european_call_parallel(...)  # Faster
else:
    price = price_european_call(...)  # Less overhead
```

### Validation
```python
# Validate once, use many times
validate_option_params(S0, K, r, sigma, T)

for strike in strikes:
    price = black_scholes_call(S0, strike, r, sigma, T)
    # No need to re-validate S0, r, sigma, T
```

### Logging
```python
# Use appropriate log levels
logger.debug("Detailed info")    # Development only
logger.info("Normal operation")  # Production
logger.warning("Unusual but OK") # Attention needed
logger.error("Failed operation") # Requires action
```

---

## 🔍 Troubleshooting

### Tests Failing
```bash
# Run with full traceback
pytest -v --tb=long

# Run specific failing test
pytest tests/test_options.py::TestBlackScholes::test_atm_call_price -v
```

### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify conftest.py exists
ls conftest.py
```

### Validation Errors
```python
# Catch and inspect
try:
    validate_option_params(S0, K, r, sigma, T)
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Parameters: S0={S0}, K={K}, r={r}, sigma={sigma}, T={T}")
```

---

## 📚 Further Reading

- **Full Documentation:** `COMPREHENSIVE_DOCUMENTATION.md`
- **Implementation Details:** `IMPLEMENTATION_COMPLETE.md`
- **Test Details:** `tests/test_options.py`, `tests/test_portfolio.py`
- **Validation API:** `utils/validation.py`
- **Logging API:** `utils/logging_config.py`
- **Parallel MC:** `options/monte_carlo_parallel.py`

---

## ✨ Quick Wins

### 1. Add Tests to Your Code
```bash
# Copy test template
cp tests/test_options.py tests/test_my_module.py
# Edit and run
pytest tests/test_my_module.py -v
```

### 2. Add Validation
```python
from utils.validation import validate_option_params

# Add to your function
def my_pricing_function(S0, K, r, sigma, T):
    validate_option_params(S0, K, r, sigma, T)  # Add this line
    # ... rest of function
```

### 3. Add Logging
```python
from utils.logging_config import get_default_logger

logger = get_default_logger(__name__)  # Add this line

def my_function():
    logger.info("Starting calculation")  # Add logging
    # ... rest of function
```

### 4. Use Parallel MC
```python
# Replace this:
from options.european_options import price_european_call
price = price_european_call(S0, K, r, sigma, T, n_paths=1_000_000)

# With this:
from options.monte_carlo_parallel import price_european_call_parallel
price, err = price_european_call_parallel(S0, K, r, sigma, T, n_paths=1_000_000)
```

---

**Quick Reference Complete** ✅  
**For detailed information, see:** `IMPLEMENTATION_COMPLETE.md`
