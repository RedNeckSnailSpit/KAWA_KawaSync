import mysql.connector
from mysql.connector import Error
from tqdm import tqdm

class Database:
    def __init__(self, db_config):
        # Extract database settings
        self.host = db_config.get("host", "localhost")
        self.port = int(db_config.get("port", 3306))
        self.name = db_config.get("name", "")
        self.user = db_config.get("user", "")
        self.password = db_config.get("password", "")
        self.connection = None

        # Initialize connection and setup tables
        self.connect()
        self.setup_tables()

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.name,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print(f"Connected to the database '{self.name}' at {self.host}:{self.port}")
        except Error as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def setup_tables(self):
        """Create necessary tables if they do not exist."""
        if not self.connection or not self.connection.is_connected():
            print("No active database connection. Reconnecting...")
            self.connect()

        queries = [
            """
            CREATE TABLE IF NOT EXISTS materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                weight FLOAT NOT NULL,
                volume FLOAT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS planets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                natural_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                resource_richness JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prun_username VARCHAR(255) NOT NULL,
                fio_api_key TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_planets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prun_username VARCHAR(255) NOT NULL,
                planet_id VARCHAR(255) NOT NULL,
                planet_natural_id VARCHAR(255) NOT NULL,
                planet_name VARCHAR(255) NOT NULL,
                weight_capacity FLOAT NOT NULL DEFAULT 0,
                volume_capacity FLOAT NOT NULL DEFAULT 0,
                weight_load FLOAT NOT NULL DEFAULT 0,
                volume_load FLOAT NOT NULL DEFAULT 0,
                UNIQUE KEY (prun_username, planet_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS storage_materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_planet_id INT NOT NULL,
                material_ticker VARCHAR(255) NOT NULL,
                material_amount FLOAT NOT NULL DEFAULT 0,
                FOREIGN KEY (user_planet_id) REFERENCES user_planets(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_warehouses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prun_username VARCHAR(255) NOT NULL,
                store_id VARCHAR(255) NOT NULL,
                location_name VARCHAR(255) NOT NULL,
                location_natural_id VARCHAR(255) NOT NULL,
                weight_load FLOAT NOT NULL DEFAULT 0,
                weight_capacity FLOAT NOT NULL DEFAULT 0,
                volume_load FLOAT NOT NULL DEFAULT 0,
                volume_capacity FLOAT NOT NULL DEFAULT 0,
                UNIQUE KEY (prun_username, store_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS warehouse_materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_warehouse_id INT NOT NULL,
                material_ticker VARCHAR(255) NOT NULL,
                material_amount FLOAT NOT NULL DEFAULT 0,
                FOREIGN KEY (user_warehouse_id) REFERENCES user_warehouses(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pricing (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mat VARCHAR(50) NOT NULL,
                location VARCHAR(255) NOT NULL,
                price FLOAT NOT NULL,
                UNIQUE KEY (mat, location)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS shipping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                from_location VARCHAR(255) NOT NULL,
                to_location VARCHAR(255) NOT NULL,
                price FLOAT NOT NULL,
                UNIQUE KEY (from_location, to_location)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS production_lines (
                production_line_id VARCHAR(255) PRIMARY KEY,
                prun_username VARCHAR(255) NOT NULL,
                planet_name VARCHAR(255) NOT NULL,
                type VARCHAR(255) NOT NULL,
                capacity FLOAT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS production_orders (
                order_id VARCHAR(255) PRIMARY KEY,
                production_line_id VARCHAR(255) NOT NULL,
                duration_ms BIGINT NOT NULL,
                recurring BOOLEAN NOT NULL DEFAULT FALSE,
                recipe_name VARCHAR(255) NOT NULL,
                FOREIGN KEY (production_line_id) REFERENCES production_lines(production_line_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_inputs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                production_order_id VARCHAR(255) NOT NULL,
                material_name VARCHAR(255) NOT NULL,
                material_ticker VARCHAR(255) NOT NULL,
                material_amount FLOAT NOT NULL DEFAULT 0,
                FOREIGN KEY (production_order_id) REFERENCES production_orders(order_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_outputs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                production_order_id VARCHAR(255) NOT NULL,
                material_name VARCHAR(255) NOT NULL,
                material_ticker VARCHAR(255) NOT NULL,
                material_amount FLOAT NOT NULL DEFAULT 0,
                FOREIGN KEY (production_order_id) REFERENCES production_orders(order_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS burn_rate (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prun_username VARCHAR(255) NOT NULL,
                planet_natural_id VARCHAR(255) NOT NULL,
                planet_name VARCHAR(255) NOT NULL,
                material_ticker VARCHAR(255) NOT NULL,
                daily_consumption FLOAT NOT NULL,
                essential BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        ]

        cursor = None
        try:
            cursor = self.connection.cursor()
            for query in queries:
                cursor.execute(query)
            self.connection.commit()
            print("Tables set up successfully.")
        except Error as e:
            print(f"Error setting up tables: {e}")
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query, params=None):
        """
        Execute a query and return the result.
        :param query: The SQL query to execute.
        :param params: Optional parameters for the query.
        :return: Query result or None.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active database connection. Reconnecting...")
            self.connect()

        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or {})
            self.connection.commit()
            print("Query executed successfully.")
            return cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def execute_update(self, query, params=None):
        """
        Execute an update/insert/delete query.
        :param query: The SQL query to execute.
        :param params: Optional parameters for the query.
        """
        if not self.connection or not self.connection.is_connected():
            print("No active database connection. Reconnecting...")
            self.connect()

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            self.connection.commit()
            print("Update executed successfully.")
        except Error as e:
            print(f"Error executing update: {e}")
        finally:
            if cursor:
                cursor.close()

    def parse_and_update_pricing_data(self, sheet_data):
        """
        Parse and update pricing data in the database.
        Only updates rows where the price has changed or new rows are detected.
        :param sheet_data: 2D list of pricing data fetched from Google Sheets.
        """
        print("Parsing and updating Pricing Data...")
        cursor = self.connection.cursor(dictionary=True)

        ticker = None
        blank_row_count = 0

        # Use tqdm to display progress
        for i, row in enumerate(tqdm(sheet_data[2:], desc="Processing Pricing Data", unit="rows"),
                                start=3):  # Start at the 3rd row
            if not row[1].strip():  # Skip rows without a ticker in column B
                blank_row_count += 1
                if blank_row_count == 2:
                    print("Two consecutive blank rows detected. Ending parsing.")
                    break
                continue
            blank_row_count = 0

            ticker = row[1].strip()  # Get the ticker from column B
            if not ticker:
                continue

            locations = row[3:]  # Starting from column D
            prices = sheet_data[i][3:]  # Prices are in the same row, starting at column D

            for location, price in zip(locations, prices):
                location = location.strip()
                price = price.strip()

                if not location or not price:  # Skip empty locations or prices
                    continue

                try:
                    price = float(price)  # Convert price to float
                except ValueError:
                    print(f"Invalid price format at row {i}: {price}")
                    continue

                # Check if the row exists and fetch its current value
                cursor.execute(
                    "SELECT price FROM pricing WHERE mat = %s AND location = %s",
                    (ticker, location)
                )
                existing_row = cursor.fetchone()

                if existing_row:
                    # Update only if the price has changed
                    if existing_row["price"] != price:
                        cursor.execute(
                            "UPDATE pricing SET price = %s WHERE mat = %s AND location = %s",
                            (price, ticker, location)
                        )
                else:
                    # Insert new row
                    cursor.execute(
                        "INSERT INTO pricing (mat, location, price) VALUES (%s, %s, %s)",
                        (ticker, location, price)
                    )

        self.connection.commit()
        cursor.close()
        print("Pricing data update complete.")

    def parse_and_update_shipping_data(self, sheet_data):
        """
        Parse and update shipping data in the database.
        Only updates rows where the price has changed or new rows are detected.
        :param sheet_data: 2D list of shipping data fetched from Google Sheets.
        """
        print("Parsing and updating Shipping Data...")
        cursor = self.connection.cursor(dictionary=True)

        headers = sheet_data[0][1:]  # Get the "To" locations from the first row, skipping column A

        # Use tqdm to display progress
        for row in tqdm(sheet_data[1:], desc="Processing Shipping Data", unit="rows"):  # Skip the header row
            from_location = row[0].strip() if len(row) > 0 else None  # Ensure the row is not empty
            if not from_location:  # Stop if the "From" location is empty
                print("Empty 'From' location detected. Ending parsing.")
                break

            for to_location, price in zip(headers, row[1:]):  # Process "To" locations and prices
                to_location = to_location.strip()
                price = price.strip()

                if not to_location or not price:  # Skip empty locations or prices
                    continue

                try:
                    price = float(price)  # Convert price to float
                except ValueError:
                    print(f"Invalid price format for {from_location} to {to_location}: {price}")
                    continue

                # Check if the row exists and fetch its current value
                cursor.execute(
                    "SELECT price FROM shipping WHERE from_location = %s AND to_location = %s",
                    (from_location, to_location)
                )
                existing_row = cursor.fetchone()

                if existing_row:
                    # Update only if the price has changed
                    if existing_row["price"] != price:
                        cursor.execute(
                            "UPDATE shipping SET price = %s WHERE from_location = %s AND to_location = %s",
                            (price, from_location, to_location)
                        )
                else:
                    # Insert new row
                    cursor.execute(
                        "INSERT INTO shipping (from_location, to_location, price) VALUES (%s, %s, %s)",
                        (from_location, to_location, price)
                    )

        self.connection.commit()
        cursor.close()
        print("Shipping data update complete.")