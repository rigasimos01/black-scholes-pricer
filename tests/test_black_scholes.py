"""
Tests for Black-Scholes calculator

This file contains test functions to verify our calculator works correctly.
Running tests helps us catch bugs early and ensures our code does what we expect.
"""

# Import the classes we want to test
from src.models.black_scholes import BlackScholesCalculator, OptionInputs


def test_basic_calculation():
    """
    Test basic Black-Scholes calculation
    
    This function tests our calculator with a simple example:
    - At-the-money option (stock price = strike price = $100)
    - 1 year to expiration
    - 25% volatility
    - 5% risk-free rate
    """
    
    # Create an OptionInputs object with our test parameters
    # This demonstrates how users of our code will interact with it
    inputs = OptionInputs(
        stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,  # 1 year
        volatility=0.25,  # 25% annual volatility
        risk_free_rate=0.05  # 5% annual risk-free rate
    )
    
    # Call our calculator to get the option prices
    result = BlackScholesCalculator.calculate(inputs)
    
    # Print the results so we can see them when we run the test
    print(f"Call Price: ${result.call_price}")
    print(f"Put Price: ${result.put_price}")
    
    # Assert statements check if conditions are true
    # If they're false, the program stops and shows an error
    # This is how we verify our calculator is working correctly
    
    # Sanity check: both prices should be positive numbers
    assert result.call_price > 0, "Call price should be positive"
    assert result.put_price > 0, "Put price should be positive"
    
    # For an at-the-money option with positive interest rates,
    # the call is typically worth more than the put (due to cost of carry)
    assert result.call_price > result.put_price, "Call should be worth more (ATM with positive rate)"
    
    # If we got here, all assertions passed!
    print("✓ All tests passed!")


# This is a special Python pattern that checks if this file is being run directly
# (as opposed to being imported by another file)
if __name__ == "__main__":
    """
    The __name__ variable is automatically set by Python:
    - If you run this file directly: python test_black_scholes.py
      then __name__ == "__main__"
    - If another file imports this: from tests import test_black_scholes
      then __name__ == "tests.test_black_scholes"
    
    This pattern lets us write code that only runs when the file is executed directly.
    It's useful for including test code or examples in a module without them running
    every time the module is imported.
    """
    # Run our test function
    test_basic_calculation()