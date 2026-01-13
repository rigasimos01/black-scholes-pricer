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
    - No dividends (default)
    """
    
    # Create an OptionInputs object with our test parameters
    # This demonstrates how users of our code will interact with it
    inputs = OptionInputs(
        stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,  # 1 year
        volatility=0.25,  # 25% annual volatility
        risk_free_rate=0.05,  # 5% annual risk-free rate
        #dividend_yield=0.0
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
    

def test_with_dividends():
    """
    Test Black-Scholes calculation WITH dividends
    
    When a stock pays dividends, the call price should be LOWER and
    the put price should be HIGHER compared to a non-dividend stock.
    
    Why? Dividends reduce the stock's expected growth rate, making calls
    less valuable and puts more valuable.
    """
    
    print("\n=== Test 2: With 2% Dividend Yield ===")
    
    # Same parameters as before, but now with a 2% dividend yield
    inputs_with_div = OptionInputs(
        stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.02  # 2% annual dividend yield
    )
    
    result_with_div = BlackScholesCalculator.calculate(inputs_with_div)
    
    print(f"Call Price: ${result_with_div.call_price}")
    print(f"Put Price: ${result_with_div.put_price}")
    
    # Compare to no-dividend case
    inputs_no_div = OptionInputs(
        stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.0  # Explicitly set to 0 for clarity
    )
    
    result_no_div = BlackScholesCalculator.calculate(inputs_no_div)
    
    print(f"\nComparison:")
    print(f"Call price impact: ${result_no_div.call_price} → ${result_with_div.call_price} (dividend reduces call value)")
    print(f"Put price impact: ${result_no_div.put_price} → ${result_with_div.put_price} (dividend increases put value)")
    
    # Dividends should reduce call value and increase put value
    assert result_with_div.call_price < result_no_div.call_price, "Dividends should reduce call price"
    assert result_with_div.put_price > result_no_div.put_price, "Dividends should increase put price"
    
    print("Dividend test passed!")


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
    # Run our test functions
    test_basic_calculation()
    test_with_dividends()
    print("\n All tests passed successfully!")