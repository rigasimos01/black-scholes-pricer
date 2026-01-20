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


if __name__ == "__main__":
    test_heatmap_generation()



