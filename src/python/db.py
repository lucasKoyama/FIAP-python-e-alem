import cx_Oracle
from datetime import datetime
from typing import List, Dict, Optional


DB_CONFIG = {
    "host": "oracle.fiap.com.br",
    "port": 1521,
    "sid": "ORCL",
    "username": "rm566925",
    "password": "DtNasc#030700",
}


def get_connection():
    """Get database connection"""
    try:
        dsn = cx_Oracle.makedsn(
            DB_CONFIG["host"], DB_CONFIG["port"], sid=DB_CONFIG["sid"]
        )
        connection = cx_Oracle.connect(
            user=DB_CONFIG["username"], password=DB_CONFIG["password"], dsn=dsn
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def create_agricultural_production(
    product_name: str,
    quantity: float,
    sale_price: float = 0,
    cost_price: float = 0,
    planting_date: str = None,
    harvest_date: str = None,
    production_status: str = "PLANTED",
) -> bool:
    """
    Create a new agricultural production record

    Args:
        product_name: Name of the product
        quantity: Quantity produced
        sale_price: Sale price (optional, default 0)
        cost_price: Cost price (optional, default 0)
        planting_date: Planting date in 'YYYY-MM-DD' format (optional)
        harvest_date: Harvest date in 'YYYY-MM-DD' format (optional)
        production_status: Status ('PLANTED', 'HARVESTED', 'SOLD')

    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        sql = """
        INSERT INTO agricultural_production 
        (product_name, quantity, sale_price, cost_price, planting_date, harvest_date, production_status)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
        """

        # Convert date strings to datetime objects if provided
        planting_dt = (
            datetime.strptime(planting_date, "%Y-%m-%d") if planting_date else None
        )
        harvest_dt = (
            datetime.strptime(harvest_date, "%Y-%m-%d") if harvest_date else None
        )

        cursor.execute(
            sql,
            (
                product_name,
                quantity,
                sale_price,
                cost_price,
                planting_dt,
                harvest_dt,
                production_status,
            ),
        )
        connection.commit()

        print(f"Successfully created record for {product_name}")
        return True

    except Exception as e:
        print(f"Error creating record: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def read_all_agricultural_production() -> List[Dict]:
    """
    Read all agricultural production records

    Returns:
        List[Dict]: List of all records as dictionaries
    """
    connection = get_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()

        sql = """
        SELECT id, product_name, quantity, sale_price, cost_price, 
               planting_date, harvest_date, production_status, 
               created_at, updated_at
        FROM agricultural_production
        ORDER BY created_at DESC
        """

        cursor.execute(sql)
        columns = [col[0].lower() for col in cursor.description]
        records = []

        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            records.append(record)

        return records

    except Exception as e:
        print(f"Error reading records: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def read_agricultural_production_by_id(record_id: int) -> Optional[Dict]:
    """
    Read a specific agricultural production record by ID

    Args:
        record_id: ID of the record to retrieve

    Returns:
        Optional[Dict]: Record as dictionary if found, None otherwise
    """
    connection = get_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()

        sql = """
        SELECT id, product_name, quantity, sale_price, cost_price, 
               planting_date, harvest_date, production_status, 
               created_at, updated_at
        FROM agricultural_production
        WHERE id = :1
        """

        cursor.execute(sql, (record_id,))
        columns = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()

        if row:
            return dict(zip(columns, row))
        else:
            print(f"No record found with ID {record_id}")
            return None

    except Exception as e:
        print(f"Error reading record: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def update_agricultural_production(record_id: int, **kwargs) -> bool:
    """
    Update an agricultural production record

    Args:
        record_id: ID of the record to update
        **kwargs: Fields to update (product_name, quantity, sale_price,
                 cost_price, planting_date, harvest_date, production_status)

    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        # Build dynamic update query based on provided fields
        valid_fields = [
            "product_name",
            "quantity",
            "sale_price",
            "cost_price",
            "planting_date",
            "harvest_date",
            "production_status",
        ]

        update_fields = []
        values = []

        for field, value in kwargs.items():
            if field in valid_fields:
                update_fields.append(f"{field} = :{len(values) + 1}")

                # Handle date conversion
                if field in ["planting_date", "harvest_date"] and isinstance(
                    value, str
                ):
                    value = datetime.strptime(value, "%Y-%m-%d")

                values.append(value)

        if not update_fields:
            print("No valid fields provided for update")
            return False

        # Add updated_at field
        update_fields.append(f"updated_at = :{len(values) + 1}")
        values.append(datetime.now())

        # Add record_id for WHERE clause
        values.append(record_id)

        sql = f"""
        UPDATE agricultural_production 
        SET {', '.join(update_fields)}
        WHERE id = :{len(values)}
        """

        cursor.execute(sql, values)

        if cursor.rowcount > 0:
            connection.commit()
            print(f"Successfully updated record with ID {record_id}")
            return True
        else:
            print(f"No record found with ID {record_id}")
            return False

    except Exception as e:
        print(f"Error updating record: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_agricultural_production(record_id: int) -> bool:
    """
    Delete an agricultural production record

    Args:
        record_id: ID of the record to delete

    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        sql = "DELETE FROM agricultural_production WHERE id = :1"
        cursor.execute(sql, (record_id,))

        if cursor.rowcount > 0:
            connection.commit()
            print(f"Successfully deleted record with ID {record_id}")
            return True
        else:
            print(f"No record found with ID {record_id}")
            return False

    except Exception as e:
        print(f"Error deleting record: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def search_agricultural_production(
    product_name: str = None, production_status: str = None
) -> List[Dict]:
    """
    Search agricultural production records by criteria

    Args:
        product_name: Product name to search for (partial match)
        production_status: Status to filter by

    Returns:
        List[Dict]: List of matching records
    """
    connection = get_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()

        sql = """
        SELECT id, product_name, quantity, sale_price, cost_price, 
               planting_date, harvest_date, production_status, 
               created_at, updated_at
        FROM agricultural_production
        WHERE 1=1
        """

        params = []

        if product_name:
            sql += " AND UPPER(product_name) LIKE UPPER(:1)"
            params.append(f"%{product_name}%")

        if production_status:
            param_num = len(params) + 1
            sql += f" AND production_status = :{param_num}"
            params.append(production_status)

        sql += " ORDER BY created_at DESC"

        cursor.execute(sql, params)
        columns = [col[0].lower() for col in cursor.description]
        records = []

        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            records.append(record)

        return records

    except Exception as e:
        print(f"Error searching records: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# Example usage functions for testing
def example_usage():
    """Example usage of the CRUD functions"""
    print("=== Agricultural Production CRUD Operations ===")

    # Create
    print("\n1. Creating new records...")
    create_agricultural_production(
        "Tomatoes", 1500.50, 25.00, 15.00, "2024-03-01", "2024-06-01", "HARVESTED"
    )
    create_agricultural_production(
        "Corn", 2000.00, 30.00, 20.00, "2024-04-15", production_status="PLANTED"
    )

    # Read all
    print("\n2. Reading all records...")
    all_records = read_all_agricultural_production()
    for record in all_records:
        print(
            f"ID: {record['id']}, Product: {record['product_name']}, "
            f"Quantity: {record['quantity']}, Status: {record['production_status']}"
        )

    # Read by ID
    if all_records:
        record_id = all_records[0]["id"]
        print(f"\n3. Reading record by ID {record_id}...")
        record = read_agricultural_production_by_id(record_id)
        if record:
            print(f"Found: {record['product_name']} - {record['quantity']} units")

    # Update
    if all_records:
        record_id = all_records[0]["id"]
        print(f"\n4. Updating record {record_id}...")
        update_agricultural_production(
            record_id, quantity=1600.00, production_status="SOLD"
        )

    # Search
    print("\n5. Searching for 'Tom' in product names...")
    search_results = search_agricultural_production(product_name="Tom")
    for record in search_results:
        print(f"Found: {record['product_name']} - {record['quantity']} units")

    ## Delete (commented out to avoid accidental deletion)
    # if all_records and len(all_records) > 1:
    #     record_id = all_records[-1]['id']
    #     print(f"\n6. Deleting record {record_id}...")
    #     delete_agricultural_production(record_id)


if __name__ == "__main__":
    example_usage()
