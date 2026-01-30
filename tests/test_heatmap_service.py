"""
Heatmap service testing

"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.black_scholes import OptionInputs
from src.services.heatmap_service import HeatmapService, HeatmapParameters

def test_heatmap_generation():

    print("\n === Testing Heatmap Generation === ")

    # base input creation
    base_inputs = OptionInputs(stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.02  # Explicitly set to 0 for clarity
    )

    #heatmap parameter creation
    heatmap_parameters = HeatmapParameters( min_spot= 80.0,
                                           max_spot= 120.0,
                                           min_vol=0.2,
                                           max_vol=0.3,
                                           spot_steps=5, vol_steps=5)
    
    service = HeatmapService()
    heatmap_data = service.generate_heatmap(base_inputs, heatmap_parameters)

    print("Grenerated Heatmap with: ")
    print(f"  - {len(heatmap_data.spot_prices)} spot price poiunts")
    print(f"  - {len(heatmap_data.vols)} vol poiunts")
    print(f"  - Total calculations: {heatmap_data.call_prices.size}")

    # display some sample data
    print(f"\n Spot prices: {heatmap_data.spot_prices}")
    print(f"Volatilities: {heatmap_data.vols}")

    print(f"\n Call prices grid (first 3x3): {heatmap_data.call_prices[:3,:3]}")


    print(f"\n Put prices grid (first 3x3): {heatmap_data.put_prices[:3,:3]}")

    #verify dim
    assert heatmap_data.call_prices.shape == (5,5), "Call prices should be 5x5"
    assert heatmap_data.put_prices.shape == (5,5), "Put prices should be 5x5"

    #verify positive prices
    assert (heatmap_data.call_prices > 0).all() , "All call prices positive"
    assert (heatmap_data.put_prices > 0).all() , "All put prices positive"

    print("\n Heatmap data validated")


def test_database_output_format():
    """Test generating data in database format"""
    
    print("\n=== Testing Database Output Format ===\n")
    
    base_inputs = OptionInputs(
        stock_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        volatility=0.25,
        risk_free_rate=0.05,
        dividend_yield=0.0
    )
    
    heatmap_params = HeatmapParameters(
        min_spot=95.0,
        max_spot=105.0,
        min_vol=0.20,
        max_vol=0.30,
        spot_steps=3,
        vol_steps=3
    )
    
    service = HeatmapService()
    call_outputs, put_outputs = service.generate_outputs_for_database(
        base_inputs,
        heatmap_params
    )

    
    # Show a sample output
    sample_call = call_outputs[0]
    print(f"\nSample call output:")
    print(f"  Vol shock: {sample_call.volatility_shock:+.4f}")
    print(f"  Spot shock: {sample_call.stock_price_shock:+.2f}")
    print(f"  Option price: ${sample_call.option_price:.4f}")
    print(f"  Is call: {sample_call.is_call}")
    
    # Verify we have the right number of outputs
    expected_count = 3 * 3  # 3x3 grid
    assert len(call_outputs) == expected_count, f"Should have {expected_count} call outputs"
    assert len(put_outputs) == expected_count, f"Should have {expected_count} put outputs"
    
    # Verify shock values make sense
    # The center point should have ~0 shock (might not be exactly 0 due to rounding)
    shocks = [abs(o.volatility_shock) + abs(o.stock_price_shock) for o in call_outputs]
    min_shock_idx = shocks.index(min(shocks))
    center_output = call_outputs[min_shock_idx]
    
    print(f"\nCenter point (closest to base):")
    print(f"  Vol shock: {center_output.volatility_shock:+.6f}")
    print(f"  Spot shock: {center_output.stock_price_shock:+.6f}")
    
    print("\n✅ Database output format test passed!")



if __name__ == "__main__":
    test_heatmap_generation()
    test_database_output_format()



