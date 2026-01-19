"""
Relevant Database entities

 defines the structure of our SQLite database tables.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CalculationInput:
    """
    Repersents a row in the BlackScholesInputs table
    
    This table stores the base parameters used for each calculation.
    Each calculation gets a unique CalculationId that links to multiple outputs.

    """
    # Optional[int] means this can be an integer or None
    # None is used before the row is saved (no ID yet), then becomes an int after saving
    calculation_id: Optional[int] = None
    stock_price: float = .0
    strike_price: float =0.0
    interest_rate: float =0.0
    volatility: float =0.0
    time_to_expiry: float  =0.0
    dividend_yield: float= 0.0
    # datetime.now() would be called when creating the object, giving us the current time
    created_at: Optional[datetime]= None


@dataclass
class CalculationOutput:
    """
    Represents a row in the BlackScholesOutputs table
    
    This table stores the results of option price calculations with various shocks.
    Multiple output rows link to a single input row via calculation_id.
    
        output_id: Unique identifier for this output row (auto-generated)
        calculation_id: Foreign key linking to BlackScholesInputs table
        volatility_shock: Change in volatility from base (e.g., +0.05, -0.10)
        stock_price_shock: Change in stock price from base (e.g., +5.0, -10.0)
        option_price: The calculated option price (call or put)
        is_call: True if this is a call option, False if put option
    """
    output_id : Optional[int] = None
    calculation_id: Optional[int] = None
    volatility_shock: float = 0.0
    stock_price_shock: float = 0.0
    option_price: float = 0.0
    is_call: bool = True  # false = put