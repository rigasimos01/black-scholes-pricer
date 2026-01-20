"""
Class to manage database for black scholes calculator

handles all interactions with the SQLite database.
It creates tables, inserts data, and retrieves calculation history.

SQLite is a file-based database - no server needed! The database is just a .db file.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
# Import our data models
from src.database.models import CalculationInput, CalculationOutput


class DatabaseManager:
    """
    Manages all database operations for the Black-Scholes calculator
      
    follows dependency injection, database path is passed as a parameter
    """
    
    def __init__(self, db_path: str = "data/black_scholes.db"):
        """
        Initialize the database manager
        
        Args:
            db_path: Path to the SQLite database file (will be created if it doesn't exist)
        """
        # Store the database path
        self.db_path = db_path
        
        # Ensure the directory exists
        # Path(db_path).parent gets the directory containing the file (e.g., "data/")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # parents=True creates parent directories if they don't exist
        # exist_ok=True doesn't error if the directory already exists
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create a connection to the SQLite database
        """
        # sqlite3.connect() creates or opens a database file
        conn = sqlite3.connect(self.db_path)
        
        # makes rows behave like dictionaries, access columns by name
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def _create_tables(self):
        """
        Create the database tables if they don't exist
        
        This method runs automatically when DatabaseManager is initialized.
        NOT EXISTS clause means it won't crash if tables already exist.
        """
        # Get a database connection
        conn = self._get_connection()
        
        # cursor() creates a cursor object used to execute SQL commands
        # Think of it like a pointer that moves through the database
        cursor = conn.cursor()
        
        # Create the inputs table
        # This table stores the base parameters for each calculation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BlackScholesInputs (
                CalculationId INTEGER PRIMARY KEY AUTOINCREMENT,
                StockPrice DECIMAL(18,9) NOT NULL,
                StrikePrice DECIMAL(18,9) NOT NULL,
                InterestRate DECIMAL(18,9) NOT NULL,
                Volatility DECIMAL(18,9) NOT NULL,
                TimeToExpiry DECIMAL(18,9) NOT NULL,
                DividendYield DECIMAL(18,9) NOT NULL DEFAULT 0.0,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create the outputs table
        # This table stores calculation results with various parameter shocks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BlackScholesOutputs (
                CalculationOutputId INTEGER PRIMARY KEY AUTOINCREMENT,
                VolatilityShock DECIMAL(18,9) NOT NULL,
                StockPriceShock DECIMAL(18,9) NOT NULL,
                OptionPrice DECIMAL(18,9) NOT NULL,
                IsCall TINYINT(1) NOT NULL,
                CalculationId INTEGER NOT NULL,
                FOREIGN KEY (CalculationId) 
                    REFERENCES BlackScholesInputs(CalculationId)
                    ON DELETE NO ACTION
                    ON UPDATE NO ACTION
            )
        """)
        # tinyint to store boolean
        # ON UPDATE NO ACTION means if you change an input's ID, outputs aren't updated
        
        # Create an index on CalculationId for faster lookups
        # An index is like a book's index - makes finding data much faster
        # Without an index, SQLite has to scan every row to find matches
        # With an index, it can jump directly to the relevant rows
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_calculation_id 
            ON BlackScholesOutputs(CalculationId)
        """)
        
        # commit() saves all changes to the database
        # Without commit(), changes are temporary and lost when connection closes
        conn.commit()
        
        # close() closes the database connection
        # Always close connections when done to free up resources
        conn.close()
    
    def save_calculation(
        self,
        inputs: CalculationInput,
        outputs: List[CalculationOutput]
    ) -> int:
        """
        Save a calculation (inputs and outputs) to the database
        
        This method uses a transaction - either everything saves or nothing does.
        This prevents partial data if something goes wrong.
        
        Args:
            inputs: CalculationInput object with base parameters
            outputs: List of CalculationOutput objects with results
            
        Returns:
            The CalculationId of the saved calculation
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert the input row first
            cursor.execute("""
                INSERT INTO BlackScholesInputs 
                (StockPrice, StrikePrice, InterestRate, Volatility, TimeToExpiry, DividendYield)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                inputs.stock_price,
                inputs.strike_price,
                inputs.interest_rate,
                inputs.volatility,
                inputs.time_to_expiry,
                inputs.dividend_yield
            ))
            # The ? are placeholders that get replaced by the values in the tuple
            
            # lastrowid gives us the auto-generated CalculationId
            calculation_id = cursor.lastrowid
            
            # Insert all the output rows
            # Each output row gets the same calculation_id, linking them to the input
            for output in outputs:
                cursor.execute("""
                    INSERT INTO BlackScholesOutputs
                    (CalculationId, VolatilityShock, StockPriceShock, OptionPrice, IsCall)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    calculation_id,
                    output.volatility_shock,
                    output.stock_price_shock,
                    output.option_price,
                    1 if output.is_call else 0  # Convert boolean to integer (1 or 0)
                ))
            
            # Save all changes
            conn.commit()
            
            # Return the calculation_id so caller knows which ID was used
            return calculation_id
            
        except Exception as e:
            # If anything went wrong, rollback (undo) all changes
            #  prevents partial data - either everything saves or nothing does (atomicity)
            conn.rollback()
            # Re-raise the exception so the caller knows something went wrong
            raise e
            
        finally:
            # finally block ALWAYS runs, even if there was an error
            # This ensures we close the connection no matter what
            conn.close()
    
    def get_calculation_by_id(self, calculation_id: int) -> Optional[Tuple[CalculationInput, List[CalculationOutput]]]:
        """
        Retrieve a calculation by its ID
        
        Args:
            calculation_id: The ID of the calculation to retrieve
            
        Returns:
            A tuple of (CalculationInput, List[CalculationOutput]) or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Fetch the input row
        cursor.execute("""
            SELECT * FROM BlackScholesInputs WHERE CalculationId = ?
        """, (calculation_id,))
        # even for a single value, we pass a tuple: (calculation_id,)
        # The comma makes it a tuple, not just parentheses around a value
        
        # returns the first matching row, or None if no matches
        input_row = cursor.fetchone()
        
        if input_row is None:
            # no calculation found with this ID
            conn.close()
            return None
        
        # Convert the database row into a CalculationInput object
        calc_input = CalculationInput(
            calculation_id=input_row['CalculationId'],
            stock_price=input_row['StockPrice'],
            strike_price=input_row['StrikePrice'],
            interest_rate=input_row['InterestRate'],
            volatility=input_row['Volatility'],
            time_to_expiry=input_row['TimeToExpiry'],
            dividend_yield=input_row['DividendYield'],
            created_at=input_row['CreatedAt']
        )
        
        # Fetch all output rows for this calculation
        cursor.execute("""
            SELECT * FROM BlackScholesOutputs WHERE CalculationId = ?
        """, (calculation_id,))
        
        # fetchall() returns a list of all matching rows
        output_rows = cursor.fetchall()
        
        # Convert each database row into a CalculationOutput object
        calc_outputs = [
            CalculationOutput(
                output_id=row['CalculationOutputId'],
                calculation_id=row['CalculationId'],
                volatility_shock=row['VolatilityShock'],
                stock_price_shock=row['StockPriceShock'],
                option_price=row['OptionPrice'],
                is_call=bool(row['IsCall'])  # Convert 0/1 back to boolean
            )
            for row in output_rows
        ]
        # This is a "list comprehension" - a compact way to build lists in Python
        # Equivalent to:
        # calc_outputs = []
        # for row in output_rows:
        #     calc_outputs.append(CalculationOutput(...))
        
        conn.close()
        
        # Return both the input and outputs as a tuple
        return (calc_input, calc_outputs)
    
    def get_recent_calculations(self, limit: int = 10) -> List[CalculationInput]:
        """
        Get the most recent calculations (inputs only, not outputs)
        
        limit: Maximum number of calculations to return
            
        returns List of CalculationInput objects, ordered by most recent first
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # ORDER BY sorts the results
        # DESC means descending order (newest first)
        # LIMIT restricts how many rows are returned
        cursor.execute("""
            SELECT * FROM BlackScholesInputs 
            ORDER BY CreatedAt DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        # Convert each row to a CalculationInput object
        calculations = [
            CalculationInput(
                calculation_id=row['CalculationId'],
                stock_price=row['StockPrice'],
                strike_price=row['StrikePrice'],
                interest_rate=row['InterestRate'],
                volatility=row['Volatility'],
                time_to_expiry=row['TimeToExpiry'],
                dividend_yield=row['DividendYield'],
                created_at=row['CreatedAt']
            )
            for row in rows
        ]
        
        conn.close()
        return calculations