"""
Black-Scholes Options Pricer App

main file to run the application
run with: streamlit run app.py
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Import our modules
from src.models.black_scholes import BlackScholesCalculator, OptionInputs
from src.services.heatmap_service import HeatmapService, HeatmapParameters
from src.database.db_manager import DatabaseManager
from src.database.models import CalculationInput, CalculationOutput
from src.ui.history_page import show_history_page

# Page configuration
st.set_page_config(
    page_title="Black-Scholes Options Pricer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar starts expanded
)

# Initialize services
@st.cache_resource
def get_services():
    #caching service instances for performance
    calculator = BlackScholesCalculator()
    heatmap_service = HeatmapService(calculator)
    db_manager = DatabaseManager()
    return calculator, heatmap_service, db_manager


calculator, heatmap_service, db_manager = get_services()


def main():    
    # sidebar for navigation
    with st.sidebar:
        st.title("Options Pricer")
        
        # Radio buttons for page selection
        page = st.radio(
            "Navigation", ["Calculator", "History"],
            label_visibility= "collapsed"  # Hide the "Navigation" label
        )
        
        st.markdown("---")
        st.markdown("""
        ### About
        This application implements the Black-Scholes model for pricing European options.
        
        **Features:**
        - Real-time option pricing
        - Greeks calculations
        - Sensitivity analysis heatmaps
        - Calculation history
        """)
    
    if page == "Calculator":
        show_calculator_page()
    elif page == "History":
        show_history_page(db_manager)


def show_calculator_page():
    """Display the main calculator page"""
    
    st.title("📈 Black-Scholes Options Pricer")
    st.markdown("""
    Calculate European call and put option prices using the Black-Scholes model.
    Explore how option prices change with different parameters.
    """)
    
    # Create layout
    col1, col2 = st.columns([1, 2])
    
    # left columns shows configurable input parameters
    with col1:
        st.header("Input Parameters")
        
        stock_price = st.number_input(
            "Current Stock Price ($)",
            value=100.0,
            min_value=0.01,
            step=1.0,
            format="%.2f",
            help="Current market price of the underlying stock"
        )
        
        strike_price = st.number_input(
            "Strike Price ($)",
            value=100.0,
            min_value=0.01,
            step=1.0,
            format="%.2f",
            help="The price at which the option can be exercised"
        )
        
        time_to_expiry = st.number_input(
            "Time to Expiry (Years)",
            value=1.0,
            min_value=0.01,
            max_value=10.0,
            step=0.1,
            format="%.2f",
            help="Time remaining until option expiration"
        )
        
        volatility = st.number_input(
            "Volatility (σ)",
            value=0.25,
            min_value=0.01,
            max_value=2.0,
            step=0.01,
            format="%.4f",
            help="Annualized volatility (e.g., 0.25 = 25%)"
        )
        
        risk_free_rate = st.number_input(
            "Risk-Free Rate (r)",
            value=0.05,
            min_value=-0.1,
            max_value=0.5,
            step=0.01,
            format="%.4f",
            help="Annualized risk-free interest rate (e.g., 0.05 = 5%)"
        )
        
        dividend_yield = st.number_input(
            "Dividend Yield (q)",
            value=0.0,
            min_value=0.0,
            max_value=0.5,
            step=0.01,
            format="%.4f",
            help="Continuous dividend yield (e.g., 0.02 = 2%)"
        )
        
        st.markdown("---")
        
        st.subheader("Heatmap Configuration")
        
        spot_range = st.slider(
            "Stock Price Range (%)",
            min_value=10,
            max_value=50,
            value=20,
            step=5,
            help="Range around current stock price (±%)"
        )
        
        vol_range = st.slider(
            "Volatility Range (%)",
            min_value=10,
            max_value=50,
            value=20,
            step=5,
            help="Range around current volatility (±%)"
        )
        
        grid_size = st.slider(
            "Grid Size",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            help="Number of points in each dimension (N x N grid)"
        )
        
        st.markdown("---")
        
        calculate_button = st.button(
            "Calculate",
            type="primary",
            width='stretch'
        )
    
    # right column shows results of calculation
    with col2:
        if calculate_button:
            try:
                # Create inputs
                inputs = OptionInputs(
                    stock_price=stock_price,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    volatility=volatility,
                    risk_free_rate=risk_free_rate,
                    dividend_yield=dividend_yield
                )
                
                # Calculate prices
                prices = calculator.calculate(inputs)
                
                # Calculate Greeks
                greeks = calculator.calculate_greeks(inputs)
                
                # Display option prices
                st.header("Option Prices")
                
                metric_col1, metric_col2 = st.columns(2)
                
                with metric_col1:
                    st.metric(
                        label="Call Option Price",
                        value=f"${prices.call_price:.4f}"
                    )
                
                with metric_col2:
                    st.metric(
                        label="Put Option Price",
                        value=f"${prices.put_price:.4f}"
                    )
                
                # Display Greeks
                st.header("Greeks (Sensitivities)")
                
                # Create tabs for call and put Greeks
                greek_tab1, greek_tab2 = st.tabs(["📞 Call Greeks", "📉 Put Greeks"])
                
                with greek_tab1:
                    show_greeks(greeks['call'])
                
                with greek_tab2:
                    show_greeks(greeks['put'])
                
                # Generate and display heatmaps
                st.header("Sensitivity Analysis")
                
                with st.spinner("Generating heatmap..."):
                    heatmap_params = heatmap_service.create_heatmap_params_from_inputs(
                        inputs,
                        spot_range_pct=spot_range / 100.0,
                        vol_range_pct=vol_range / 100.0,
                        steps=grid_size
                    )
                    
                    heatmap_data = heatmap_service.generate_heatmap(inputs, heatmap_params)
                
                tab1, tab2 = st.tabs(["📞 Call Price Heatmap", "📉 Put Price Heatmap"])
                
                with tab1:
                    fig_call = create_heatmap(
                        heatmap_data.spot_prices,
                        heatmap_data.vols,
                        heatmap_data.call_prices,
                        "Call Option Price",
                        stock_price,
                        volatility
                    )
                    st.plotly_chart(fig_call, width='stretch')
                
                with tab2:
                    fig_put = create_heatmap(
                        heatmap_data.spot_prices,
                        heatmap_data.vols,
                        heatmap_data.put_prices,
                        "Put Option Price",
                        stock_price,
                        volatility
                    )
                    st.plotly_chart(fig_put, width='stretch')
                
                # Save to database
                st.markdown("---")

                def save_callback():
                    save_to_database(inputs, heatmap_params, heatmap_data)
                
                with st.expander("💾 Save Calculation to Database"):
                    st.button(
                                "Save to Database",
                                    type="secondary",
                                key="save_calc_btn",
                                on_click=save_callback
                            )
            
            except ValueError as e:
                st.error(f"Input Error: {str(e)}")
            except Exception as e:
                st.error(f"Calculation Error: {str(e)}")
        
        else:
            st.info("👈 Enter parameters and click **Calculate** to see results")




def show_greeks(greeks_dict):
    """
    Display Greeks in a nice format
    
    Args:
        greeks_dict: Dictionary containing Greek values
    """
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Delta (Δ)",
            f"{greeks_dict['delta']:.4f}",
            help="Change in option price per $1 change in stock price"
        )
    
    with col2:
        st.metric(
            "Gamma (Γ)",
            f"{greeks_dict['gamma']:.4f}",
            help="Rate of change of delta"
        )
    
    with col3:
        st.metric(
            "Theta (Θ)",
            f"{greeks_dict['theta']:.4f}",
            help="Change in option price per day (time decay)"
        )
    
    with col4:
        st.metric(
            "Vega (ν)",
            f"{greeks_dict['vega']:.4f}",
            help="Change in option price per 1% change in volatility"
        )
    
    with col5:
        st.metric(
            "Rho (ρ)",
            f"{greeks_dict['rho']:.4f}",
            help="Change in option price per 1% change in interest rate"
        )


def create_heatmap(spot_prices, volatilities, prices, title, base_spot, base_vol):
    """Create a Plotly heatmap figure"""
    fig = go.Figure(data=go.Heatmap(
        x=spot_prices,
        y=volatilities,
        z=prices,
        colorscale='RdYlGn',
        text=np.round(prices, 2),
        hovertemplate='Stock: $%{x:.2f}<br>Vol: %{y:.4f}<br>Price: $%{z:.4f}<extra></extra>',
        colorbar=dict(title="Option<br>Price ($)")
    ))
    
    fig.add_trace(go.Scatter(
        x=[base_spot],
        y=[base_vol],
        mode='markers',
        marker=dict(
            size=15,
            color='blue',
            symbol='x',
            line=dict(width=2, color='white')
        ),
        name='Base Case',
        hovertemplate=f'Base Case<br>Stock: ${base_spot:.2f}<br>Vol: {base_vol:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Stock Price ($)",
        yaxis_title="Volatility (σ)",
        height=500,
        hovermode='closest'
    )
    
    return fig


def save_to_database(inputs, heatmap_params, heatmap_data):
    """Save calculation to database"""
    try:
        calc_input = CalculationInput(
            stock_price=inputs.stock_price,
            strike_price=inputs.strike_price,
            interest_rate=inputs.risk_free_rate,
            volatility=inputs.volatility,
            time_to_expiry=inputs.time_to_expiry,
            dividend_yield=inputs.dividend_yield
        )
        
        call_outputs, put_outputs = heatmap_service.generate_outputs_for_database(
            inputs,
            heatmap_params
        )
        
        all_outputs = call_outputs + put_outputs
        
        calc_id = db_manager.save_calculation(calc_input, all_outputs)
        
        st.success(f"✅ Calculation saved successfully! (ID: {calc_id})")
        
    except Exception as e:
        st.error(f"❌ Error saving to database: {str(e)}")


if __name__ == "__main__":
    main()