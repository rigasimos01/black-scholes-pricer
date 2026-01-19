"""
Tests for database functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.db_manager import DatabaseManager
from src.database.models import CalculationInput, CalculationOutput


def test_database():
    """Test saving and retrieving calculations"""
    
    print("\n=== Testing Database Operations ===\n")
    
    # Create a test database (using a different file so we don't mess up real data)
    db = DatabaseManager("data/test_black_scholes.db")
    
    print("✓ Database initialized")
    
    # Create test input
    test_input = CalculationInput(
        stock_price=100.0,
        strike_price=95.0,
        interest_rate=0.05,
        volatility=0.25,
        time_to_expiry=1.0,
        dividend_yield=0.02
    )
    
    # Create test outputs (call and put at base case)
    test_outputs = [
        CalculationOutput(
            volatility_shock=0.0,
            stock_price_shock=0.0,
            option_price=12.34,
            is_call=True
        ),
        CalculationOutput(
            volatility_shock=0.0,
            stock_price_shock=0.0,
            option_price=5.67,
            is_call=False
        )
    ]
    
    # Save to database
    calc_id = db.save_calculation(test_input, test_outputs)
    print(f"✓ Saved calculation with ID: {calc_id}")
    
    # Retrieve from database
    retrieved = db.get_calculation_by_id(calc_id)
    
    if retrieved is None:
        print("✗ Failed to retrieve calculation")
        return
    
    retrieved_input, retrieved_outputs = retrieved
    
    print(f"✓ Retrieved calculation ID: {retrieved_input.calculation_id}")
    print(f"  Stock Price: ${retrieved_input.stock_price}")
    print(f"  Strike Price: ${retrieved_input.strike_price}")
    print(f"  Number of outputs:  {len(retrieved_outputs)}")
     
    # Verify data matches
    assert retrieved_input.stock_price == test_input.stock_price
    assert retrieved_input.strike_price == test_input.strike_price
    assert len(retrieved_outputs) == len(test_outputs)
    
    print("✓ Data integrity verified")
    
    # Test getting recent calculations
    recent = db.get_recent_calculations(limit=5)
    print(f"\n✓ Retrieved {len(recent)} recent calculations")
    
    print("\n✅ All database tests passed!")


if __name__ == "__main__":
    test_database()