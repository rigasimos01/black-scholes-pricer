"""
Black-Scholes Options Pricing Model

This module implements the Black-Scholes formula for pricing European call and put options.
The Black-Scholes model is the foundational framework for options pricing in finance.
"""

# Import statements - bringing in code from other libraries we need
import numpy as np  # For mathematical operations like logarithms and exponentials
from scipy.stats import norm  # For the cumulative normal distribution function N(d)
from typing import Tuple  # For type hints (helps with code clarity and IDE autocomplete)
from dataclasses import dataclass  # A decorator that auto-generates boilerplate code for classes


# The @dataclass decorator automatically creates __init__, __repr__, and other methods
# This saves us from writing repetitive constructor code
@dataclass
class OptionInputs:
    """
    Container for option pricing inputs
    
    This is a data class that holds all the parameters needed to price an option.
    Using a dataclass makes our code cleaner - instead of passing 5 separate parameters,
    we pass one object that contains all of them.
    
    Attributes:
        stock_price: Current price of the underlying stock (S)
        strike_price: Strike/exercise price of the option (K)
        time_to_expiry: Time until option expires, in years (T)
        volatility: Annualized volatility of the stock (sigma/σ)
        risk_free_rate: Annualized risk-free interest rate (r)
    """
    # These are called "type annotations" - they tell Python (and us) what type each variable should be
    # float means a decimal number like 100.5
    stock_price: float
    strike_price: float
    time_to_expiry: float  # in years (e.g., 0.5 = 6 months, 1.0 = 1 year)
    volatility: float  # as a decimal (e.g., 0.25 = 25% volatility)
    risk_free_rate: float  # as a decimal (e.g., 0.05 = 5% interest rate)
    
    def __post_init__(self):
        """
        This special method runs automatically AFTER the dataclass __init__ creates the object.
        We use it to validate that the user didn't input nonsensical values.
        
        For example: a negative stock price doesn't make sense in finance.
        """
        if self.stock_price <= 0:
            raise ValueError("Stock price must be positive")
        if self.strike_price <= 0:
            raise ValueError("Strike price must be positive")
        if self.time_to_expiry <= 0:
            raise ValueError("Time to expiry must be positive")
        if self.volatility <= 0:
            raise ValueError("Volatility must be positive")
        # Note: risk_free_rate CAN be negative in some rare economic scenarios, so we don't check it


@dataclass
class OptionPrices:
    """
    Container for calculated option prices
    
    This holds the output of our Black-Scholes calculation.
    Again, using a dataclass makes it easy to return multiple related values.
    
    Attributes:
        call_price: The fair value of a call option
        put_price: The fair value of a put option
    """
    call_price: float
    put_price: float


class BlackScholesCalculator:
    """
    Black-Scholes option pricing calculator
    
    This is our main calculator class. It contains the methods that implement
    the Black-Scholes formula for pricing options.
    
    We use @staticmethod because these calculations don't need any instance-specific data.
    They just take inputs and return outputs - pure functions.
    """
    
    @staticmethod  # This means the method doesn't need 'self' - it doesn't access instance variables
    def calculate(inputs: OptionInputs) -> OptionPrices:
        """
        Calculate call and put option prices using Black-Scholes formula
        
        The Black-Scholes formula:
        Call Price = S*N(d1) - K*e^(-rT)*N(d2)
        Put Price = K*e^(-rT)*N(-d2) - S*N(-d1)
        
        Where:
        - S = current stock price
        - K = strike price
        - T = time to expiration
        - r = risk-free rate
        - σ (sigma) = volatility
        - N(x) = cumulative distribution function of standard normal distribution
        - d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        - d2 = d1 - σ√T
        
        Args:
            inputs: OptionInputs object containing all required parameters
            
        Returns:
            OptionPrices object with call_price and put_price
        """
        # Extract values from the inputs object to make the formula more readable
        # These variable names match standard finance notation
        S = inputs.stock_price  # Current stock price
        K = inputs.strike_price  # Strike price
        T = inputs.time_to_expiry  # Time to expiration (in years)
        sigma = inputs.volatility  # Volatility (sigma in Greek notation)
        r = inputs.risk_free_rate  # Risk-free interest rate
        
        # Calculate d1 - the first key component of the Black-Scholes formula
        # np.log() is the natural logarithm (ln)
        # np.sqrt() is the square root
        # The formula measures how far "in the money" the option is, adjusted for time and volatility
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        
        # Calculate d2 - the second key component
        # d2 is just d1 shifted by σ√T
        d2 = d1 - sigma * np.sqrt(T)
        
        # norm.cdf() is the cumulative distribution function (CDF) of the standard normal distribution
        # N(d1) represents the probability that the option will be exercised
        # np.exp() is the exponential function (e^x)
        
        # Call option price formula
        # S * norm.cdf(d1) = expected value of stock if option is exercised
        # K * np.exp(-r * T) * norm.cdf(d2) = present value of strike price, weighted by probability
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        
        # Put option price formula
        # This is derived from put-call parity but can also be calculated directly
        # norm.cdf(-d2) is the same as 1 - norm.cdf(d2), used for the opposite tail of distribution
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        # Return both prices in an OptionPrices object
        # round() to 4 decimal places for cleaner output (pennies + 2 more digits)
        return OptionPrices(
            call_price=round(call_price, 4),
            put_price=round(put_price, 4)
        )
    
    @staticmethod
    def calculate_greeks(inputs: OptionInputs) -> dict:
        """
        Calculate option Greeks (for future enhancement)
        
        Greeks measure the sensitivity of option prices to various factors:
        - Delta: sensitivity to stock price changes
        - Gamma: rate of change of delta
        - Theta: sensitivity to time decay
        - Vega: sensitivity to volatility changes
        - Rho: sensitivity to interest rate changes
        
        We'll implement this in a later step.
        
        Returns:
            Dictionary containing delta, gamma, theta, vega, rho
        """
        # NotImplementedError is a built-in exception type that signals
        # "this feature exists but isn't coded yet"
        raise NotImplementedError("Greeks calculation coming in future version")