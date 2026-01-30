"""
    heatmap generation service 

    this service generates a heatmap of option prices with varying the volatility 
    and stock price around base values

    creates the necessary data needed for the visualisation of the heatmap


"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass

from src.models.black_scholes import BlackScholesCalculator, OptionInputs, OptionPrices
from src.database.models import CalculationOutput

@dataclass
class HeatmapParameters:
    """
    heatmap configuration

    The parameters define the range of values and the steps of the heatmap

        min_spot : Minimum stock price for the grid
        max_spot: maximum stock price
        min_vol : Minimum volatility 
        max_vol: maximum volatility
        spot_steps: number  of steps between min and max price
        vol_steps: number of steps for volatility
    """

    min_spot: float
    max_spot: float
    min_vol: float
    max_vol: float
    spot_steps: int = 10 #default 10x10 grid
    vol_steps: int = 10 

@dataclass
class HeatMapData:
    """
    heatmap calculation results class

    all data needed to show the heatmap

        spot_prices: array of stocj prices
        vols: array of volatilities used in grid
        call_prices: 2D array of call prices [vol_index, spot_index]
        put_prices: 2D array of put prices
    
    """

    spot_prices: np.ndarray
    vols: np.ndarray
    call_prices: np.ndarray
    put_prices: np.ndarray


class HeatmapService:
    """
    Service for generating the heatmaps

    calculates option pricess across a grid of stock prices and 
    volatilities creatinng the data needed for heatmap visualizations
    
    """

    def __init__(self, calculator: BlackScholesCalculator = None):

        self.calculator = calculator if calculator is not None else BlackScholesCalculator()

    def generate_heatmap(self, base_input: OptionInputs, 
                         heatmap_params: HeatmapParameters) -> HeatMapData:
        
        spot_prices = np.linspace(heatmap_params.min_spot,
                                  heatmap_params.max_spot, heatmap_params.spot_steps)
        
        vols = np.linspace(heatmap_params.min_vol, heatmap_params.max_vol,
                           heatmap_params.vol_steps)
        
        # initialise 2d arrays to store results
        # number of vols x number of prices
        call_prices = np.zeros((len(vols), len(spot_prices)))      
        put_prices = np.zeros((len(vols), len(spot_prices)))

        for i, vol in enumerate(vols):
            for j, spot in enumerate(spot_prices):
                # new opption inputs everytime
                # keeping rf, dividend, time, and K fixed from base inputs
                shocked_inputs = OptionInputs(stock_price=spot, 
                                              strike_price=base_input.strike_price,
                                              time_to_expiry=base_input.time_to_expiry,
                                              volatility=vol,
                                              risk_free_rate=base_input.risk_free_rate,
                                              dividend_yield=base_input.dividend_yield)
                
                prices = self.calculator.calculate(shocked_inputs)

                call_prices[i , j] = prices.call_price
                put_prices[i , j] = prices.put_price

        return HeatMapData(spot_prices=spot_prices,
                               vols=vols,
                               call_prices=call_prices,
                               put_prices=put_prices)
        

    def generate_outputs_for_database(self,
                                      base_inputs: OptionInputs,
                                      heatmap_params: HeatmapParameters
                                      ) -> Tuple[List[CalculationOutput], List[CalculationOutput]]:
        
        """
        same as generate_heatmap(), but formats data for saving in database
        
        """

        #first get resulting heatmap data
        heatmap_data = self.generate_heatmap(base_inputs, heatmap_params)

        calls = []
        puts = []

        for i, vol in enumerate(heatmap_data.vols):
            for j, spot in enumerate(heatmap_data.spot_prices):

                vol_shock = vol - base_inputs.volatility
                spot_shock = spot - base_inputs.stock_price

                call_price = heatmap_data.call_prices[i,j]
                put_price = heatmap_data.put_prices[i,j]

                call_output = CalculationOutput(volatility_shock=vol_shock,option_price= call_price,
                                                stock_price_shock=spot_shock,
                                                is_call = True
                                                )

                put_output = CalculationOutput(volatility_shock=vol_shock,option_price= call_price,
                                                stock_price_shock=spot_shock,
                                                is_call = True
                                                )
                
                calls.append(call_output)
                puts.append(put_output)

        
        return calls, puts
    
    def create_heatmap_params_from_inputs(self, base_inputs: OptionInputs,
                                          spot_range_pct: float  = 0.2, vol_range_pct: float = 0.2,
                                          steps: int = 10) -> HeatmapParameters:
        
        """
            automatically create heatmap parameters (volatility min and max and steps as well as spot price
            min and max and steps), based on the input price and volatility. we just define the range percentage 
            for these two factors and the number of steps and the absllute value of the shocks will be computed by this method

        """

        min_spot = base_inputs.stock_price * (1 - spot_range_pct)
        max_spot = base_inputs.stock_price * (1+ spot_range_pct)

        min_vol = base_inputs.volatility * (1 - vol_range_pct)
        max_vol = base_inputs.volatility * (1+ vol_range_pct)

        #to ensure vol is positive, otherwise black scholes wont work
        min_vol = max(min_vol, 0.005)

        return HeatmapParameters(
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol= min_vol,
            max_vol = max_vol,
            spot_steps=steps,
            vol_steps=steps
        )
    

    



        