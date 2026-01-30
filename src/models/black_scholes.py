"""
Black Scholes Options Pricing Model

This file implements the Black-Scholes formula for pricing European call and put options.
The Black-Scholes model is the foundational framework for options pricing in finance.
"""

import numpy as np  
from scipy.stats import norm 
from typing import Tuple
from dataclasses import dataclass


# The @dataclass decorator automatically creates __init__, __repr__, and other methods
# This saves us from writing repetitive constructor code
@dataclass
class OptionInputs:
    """
    Container for option pricing inputs
    
    This is a class that holds all the input parameters needed to price an option.
   

        stock_price: Current price of the underlying stock (S)
        strike_price: Strike/exercise price of the option (K)
        time_to_expiry: Time until option expires, in years (T)
        volatility: Annualized volatility of the stock (sigma)
        risk_free_rate: Annualized risk-free interest rate (r)
        dividend_yield: Continuous dividend yield (q) - defaults to 0.0 for non-dividend stocks
    """
    stock_price: float
    strike_price: float
    time_to_expiry: float  # unit: years
    volatility: float  # decimal value
    risk_free_rate: float  # decimal value
    dividend_yield: float = 0.0 # decimal value
                                  # dividend yield parameter is optional and defaults to 0
    
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
        if self.dividend_yield < 0: 
            raise ValueError("Dividend yield must not be negative")
        # nb: rf can be negative in some occasion


@dataclass
class OptionPrices:
    """
    Class to store resulting ootpion prices
    
    This holds the output of our Black-Scholes calculation.
    Again, using a dataclass makes it easy to return multiple related values.
    
        call_price: The fair value of a call option
        put_price: The fair value of a put option
    """
    call_price:  float
    put_price: float


class BlackScholesCalculator:
    """
     option pricing calculator
    
    This is the main calculator class. It contains the methods that implement
    the Black-Scholes formula for pricing options.
    """
    
    @staticmethod  # This means the method doesn't need 'self'
    def calculate(inputs: OptionInputs) -> OptionPrices:
        """
        Calculate call and put option prices using Black-Scholes formula
        
        The Black-Scholes formula:
        Call Price = S*e^(-qT)*N(d1) - K*e^(-rT)*N(d2)
        Put price = K*e^(-rT)*N(-d2) - S*e^(-qT)*N(-d1)
        
        Where:
        - S = current stock price
        - K = strike price
        - T = time to expiration
        - r = risk-free rate
        - sigma = volatility
        - q = continuous dividend yield
        - N(x) = cumulative distribution function of standard normal distribution
        - d1 = [ln(S/K) + (r + sigma^2/2)T] / (sigma*sqrt(T))
        - d2 = d1 - sigma* sqrt(T)
        
            inputs: OptionInputs object containing all required parameters
            
            OptionPrices object with call_price and put_price
        """
        S = inputs.stock_price  # curent stock price
        K = inputs.strike_price  # strike price
        T = inputs.time_to_expiry  # time to expiration (years)
        vol = inputs.volatility  # vol
        r = inputs.risk_free_rate  # rf
        q = inputs.dividend_yield
        
        # Calculate d1 - the first key component of the Black-Scholes formula
        # np.log() is the natural logarithm (ln)
        # np.sqrt() is the square root
        # The formula measures how far "in the money" the option is, adjusted for time and volatility
        d1 = (np.log(S / K) + (r - q + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
        
        # Calculate d2 - the second key component
        # d2 is just d1 shifted by sigma*sqrt(T)
        d2 = d1 - vol * np.sqrt(T)
        
        # S*norm.cdf(d1) = expected value of stock if option is exercised
        # K*np.exp(-r * T) * norm.cdf(d2) = present value of strike price, weighted by probability
        call_price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        
        # Put option price formula
        # derived from put-call parity but can also be calculated directly
        # norm.cdf(-d2) is the same as 1 - norm.cdf(d2), used for the opposite tail of distribution
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        
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
        
        Returns:
            Dict containing delta, gamma, theta, vega, rho
        """

        S = inputs.stock_price
        K = inputs.strike_price
        vol = inputs.volatility
        T = inputs.time_to_expiry
        r = inputs.risk_free_rate
        q = inputs.dividend_yield

        
        # The formula measures how far "in the money" the option is, adjusted for time and volatility
        d1 = (np.log(S / K) + (r - q + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
        
        # Calculate d2 - the second key component
        # d2 is just d1 shifted by sigma*sqrt(T)
        d2 = d1 - vol * np.sqrt(T)

        #Call delta: e^(qT) * N(d1)
        # Put delta = -e^(qT) * N(-d1)
        call_delta = np.exp(-q*T)  * norm.cdf(d1)
        put_delta = -np.exp(-q*T) * norm.cdf(-d1)

        # Gamma is just the derivative of delta in terms of S
        # since put_delta = call_delta - e^(-qT) their gammas are equivalent all else equal
        gamma = np.exp(-q*T) * (norm.pdf(d1)) / (S*vol*np.sqrt(T))

        # vega - sensitivity to volatility
        # measures change in option price in terms of change in volatility
        # we usually express it per 1% move, so i multiply by 0.01
        vega = S * np.exp(-q*T) * norm.pdf(d1) * np.sqrt(T) * 0.01

        # Theta - change in option price in terms of forward change in time 
        # usually expressed per day so divide by 365
        call_theta = (-(S* norm.pdf(d1) * vol * np.exp(-q*T) / (2* np.sqrt(T))) 
                      - r * K * np.exp(-r*T) + norm.cdf(d2)
                      + q*S* np.exp(-q*T) * norm.cdf(d1)) / 365
        
        put_theta = (-(S* norm.pdf(d1) * vol * np.exp(-q*T) / (2* np.sqrt(T))) 
                      + r * K * np.exp(-r*T) + norm.cdf(-d2)
                      - q*S* np.exp(-q*T) * norm.cdf(-d1)) / 365
        

        #rho - sensitivity to interest rates
        # chang ein option price following a 1% change in interest rate
        # we multiply by 0.01 to find that
        call_rho = K * T * np.exp(-r*T) * norm.cdf(d2) * 0.01
        put_rho = -K * T * np.exp(-r *T) * norm.cdf(-d2) * 0.01

        return {
            'call' : {
                'delta' : round(call_delta, 4),
                'gamma' : round(gamma, 4),
                'theta' : round(call_theta, 4),
                'vega' : round(vega, 4),
                'rho' : round(call_rho,4)
            } ,
            'put' : {
                'delta' : round(put_delta, 4),
                'gamma' : round(gamma, 4),
                'theta' : round(put_theta, 4),
                'vega' : round(vega, 4),
                'rho' : round(put_rho,4)
            } 
        }



        # NotImplementedError is a built-in exception type that signals
        # "this feature exists but isn't coded yet"
        raise NotImplementedError("Greeks calculation coming in future version")