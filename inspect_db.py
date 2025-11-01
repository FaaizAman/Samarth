# inspect_db.py
import pandas as pd
from sqlalchemy import create_engine, inspect

DB_PATH = 'sqlite:///samarth.db'
ENGINE = create_engine(DB_PATH)


def inspect_database():
    """Inspect the database structure to see actual table schemas."""
    inspector = inspect(ENGINE)

    print("=== Database Inspection ===")
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

    for table in tables:
        print(f"\n--- Table: {table} ---")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  {column['name']} ({column['type']})")

        # Show sample data
        try:
            sample = pd.read_sql(f"SELECT * FROM {table} LIMIT 2", ENGINE)
            print(f"Sample data:")
            print(sample)
        except Exception as e:
            print(f"Could not read sample data: {e}")


if __name__ == "__main__":
    inspect_database()