"""
Greeks calculation for European options using Black-Scholes formulas.
Delta, Gamma, Vega, Theta, Rho - the sensitivities of option prices.
"""

import numpy as np
from scipy.stats import norm


def d1(S, K, T, r, sigma):
    """Calculate d1 parameter for Black-Scholes."""
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def d2(S, K, T, r, sigma):
    """Calculate d2 parameter for Black-Scholes."""
    return d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


# =============================================================================
# First-order Greeks
# =============================================================================

def delta_call(S, K, T, r, sigma):
    """
    Delta: Rate of change of option price with respect to underlying price.
    For calls: always positive (0 to 1)
    """
    return norm.cdf(d1(S, K, T, r, sigma))


def delta_put(S, K, T, r, sigma):
    """
    Delta for put options.
    For puts: always negative (-1 to 0)
    """
    return delta_call(S, K, T, r, sigma) - 1


def vega(S, K, T, r, sigma):
    """
    Vega: Rate of change with respect to volatility.
    Same for calls and puts. Usually quoted per 1% vol change.
    """
    d1_val = d1(S, K, T, r, sigma)
    return S * norm.pdf(d1_val) * np.sqrt(T) / 100  # per 1% vol


def theta_call(S, K, T, r, sigma):
    """
    Theta: Rate of time decay (per day).
    Usually negative - options lose value as time passes.
    """
    d1_val = d1(S, K, T, r, sigma)
    d2_val = d2(S, K, T, r, sigma)
    
    term1 = -S * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
    term2 = -r * K * np.exp(-r * T) * norm.cdf(d2_val)
    
    return (term1 + term2) / 365  # per day


def theta_put(S, K, T, r, sigma):
    """Theta for put options (per day)."""
    d1_val = d1(S, K, T, r, sigma)
    d2_val = d2(S, K, T, r, sigma)
    
    term1 = -S * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
    term2 = r * K * np.exp(-r * T) * norm.cdf(-d2_val)
    
    return (term1 + term2) / 365  # per day


def rho_call(S, K, T, r, sigma):
    """
    Rho: Rate of change with respect to interest rate.
    Quoted per 1% rate change.
    """
    d2_val = d2(S, K, T, r, sigma)
    return K * T * np.exp(-r * T) * norm.cdf(d2_val) / 100


def rho_put(S, K, T, r, sigma):
    """Rho for put options (per 1% rate change)."""
    d2_val = d2(S, K, T, r, sigma)
    return -K * T * np.exp(-r * T) * norm.cdf(-d2_val) / 100


# =============================================================================
# Second-order Greeks
# =============================================================================

def gamma(S, K, T, r, sigma):
    """
    Gamma: Rate of change of delta with respect to underlying price.
    Same for calls and puts. Measures convexity.
    """
    d1_val = d1(S, K, T, r, sigma)
    return norm.pdf(d1_val) / (S * sigma * np.sqrt(T))


def vanna(S, K, T, r, sigma):
    """
    Vanna: Sensitivity of delta to volatility (or vega to spot).
    Cross-gamma between spot and vol.
    """
    d1_val = d1(S, K, T, r, sigma)
    d2_val = d2(S, K, T, r, sigma)
    return -norm.pdf(d1_val) * d2_val / sigma


def volga(S, K, T, r, sigma):
    """
    Volga (Vomma): Sensitivity of vega to volatility.
    Second derivative with respect to vol.
    """
    d1_val = d1(S, K, T, r, sigma)
    d2_val = d2(S, K, T, r, sigma)
    v = vega(S, K, T, r, sigma) * 100  # convert back
    return v * d1_val * d2_val / sigma


if __name__ == "__main__":
    # Example: ATM option
    S = 100      # Spot price
    K = 100      # Strike (ATM)
    T = 0.25     # 3 months
    r = 0.05     # 5% risk-free rate
    sigma = 0.20 # 20% volatility
    
    print("="*50)
    print("Greeks for European Call Option (ATM)")
    print("="*50)
    print(f"Spot: ${S}, Strike: ${K}, T: {T:.2f}y")
    print(f"Rate: {r*100:.1f}%, Vol: {sigma*100:.0f}%")
    print("-"*50)
    
    print(f"\nFirst-Order Greeks:")
    print(f"  Delta:  {delta_call(S, K, T, r, sigma):.4f}")
    print(f"  Vega:   ${vega(S, K, T, r, sigma):.4f} (per 1% vol)")
    print(f"  Theta:  ${theta_call(S, K, T, r, sigma):.4f} (per day)")
    print(f"  Rho:    ${rho_call(S, K, T, r, sigma):.4f} (per 1% rate)")
    
    print(f"\nSecond-Order Greeks:")
    print(f"  Gamma:  {gamma(S, K, T, r, sigma):.6f}")
    print(f"  Vanna:  {vanna(S, K, T, r, sigma):.6f}")
    print(f"  Volga:  {volga(S, K, T, r, sigma):.6f}")
    
    print("\n" + "="*50)
    print("Greeks for European Put Option (ATM)")
    print("="*50)
    print(f"\nFirst-Order Greeks:")
    print(f"  Delta:  {delta_put(S, K, T, r, sigma):.4f}")
    print(f"  Vega:   ${vega(S, K, T, r, sigma):.4f} (per 1% vol)")
    print(f"  Theta:  ${theta_put(S, K, T, r, sigma):.4f} (per day)")
    print(f"  Rho:    ${rho_put(S, K, T, r, sigma):.4f} (per 1% rate)")
    
    # Delta hedging example
    print("\n" + "="*50)
    print("Delta Hedging Example")
    print("="*50)
    position_size = 100  # 100 call options (1 contract = 100 shares)
    delta = delta_call(S, K, T, r, sigma)
    hedge_shares = -position_size * delta
    print(f"Long {position_size} calls → Short {hedge_shares:.1f} shares to delta-hedge")
