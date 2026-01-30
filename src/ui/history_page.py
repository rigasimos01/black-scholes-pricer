"""
Calculation History page

page for viewing past calculations from the database
"""


import streamlit as st
import pandas as pd
from datetime import datetime

from src.database.db_manager import DatabaseManager

def show_history_page(db_manager: DatabaseManager):
    """
    Display calculation history page

    Arguments:
        db_manager: DatabaseManager instance to access saved calcs
    """

    st.header("Calculation History")

    st.markdown(""" View your previous calculations. Click on any calculation to see details""")

    recent_calcs = db_manager.get_recent_calculations(20)

    if not recent_calcs:
        st.info("No calculations were found. Create and Save a calculation to view it here!")

    df_data = []

    for calc in recent_calcs:
        df_data.append({
            'ID': calc.calculation_id,
            'Stock Price' : f"${calc.stock_price:.2f}",
            'Strike' : f"${calc.strike_price:.2f}",
            'Volatility' : f"${calc.volatility:.2f}",
            'Time (Years)' : f"${calc.time_to_expiry:.2f}",
            'Interest Rate' : f"${calc.interest_rate:.2f}",
            'Dividend' : f"${calc.dividend_yield:.2f}",
            'Created' : f"${calc.stock_price:.2f}"
        })

    df = pd.DataFrame(df_data)

    #display table
    #st.dataframe creates interactive table
    st.dataframe(df, use_container_width=True, hide_index=True)

    #allow user to select calculation and view details
    st.markdown("---")

    calc_ids = [calc.calculation_id for calc in recent_calcs]

    selected_id = st.selectbox("Select a calculation to view details: ",
                               options=calc_ids, 
                               format = lambda x: f"Calculation #{x}")
    
    if selected_id:
        show_calculation_details(db_manager,selected_id)


def show_calculation_details(db_manager: DatabaseManager, calc_id: int):
    """
    Show detailed info about a specific calculation

    Arguments:
        db_manager: DatabaseManager instance
        calc_id: ID of the calculation to display
    """

    result = db_manager.get_calculation_by_id(calc_id)

    if result is None:
        st.error("Calculation not found!")
        return
    
    calc_input, calc_outputs = result

    st.subheader(f"Calculation #{calc_id} Details")

    col1, col2, col3 = st.columns(3)

    with col1: 
        st.metric("Stock Price" f"${calc_input.stock_price:.2f}")
        st.metric("Strike Price" f"${calc_input.strike_price:.2f}")
    with col2:
        st.metric("Volatility" f"${calc_input.volatility:.2f}")
        st.metric("Time to expiry" f"${calc_input.time_to_expiry:.2f}")
    with col3:
        st.metric("Interest rate" f"${calc_input.interest_rate:.2f}")
        st.metric("Dividend yield" f"${calc_input.dividend_yield:.2f}")

    st.markdown("---")
    st.subheader("Outputs Summary")

    call_outputs = [o for o in calc_outputs if o.is_call]
    put_outputs = [o for o in calc_outputs if not o.is_call]

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Call Options:** {len(call_outputs)} calculations")
        if call_outputs:
            prices = [o.option_price for o in call_outputs]
            st.write(f"Price range: $ {min(prices):.4f} - $ {max(prices):.4f}")

    with col2:
        st.write(f"**Put Options:** {len(put_outputs)} calculations")
        if put_outputs:
            prices = [o.option_price for o in put_outputs]
            st.write(f"Price range: $ {min(prices):.4f} - $ {max(prices):.4f}")        

