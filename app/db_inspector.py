from sqlalchemy import inspect
from app.models import db

def get_database_tables():
    """Returns a list of table names available in the connected database."""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        return []

def get_table_columns(table_name):
    """Returns a list of dicts with column metadata for the given table."""
    try:
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):
            return []
        columns = inspector.get_columns(table_name)
        result = []
        for col in columns:
            result.append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col.get('nullable', True)
            })
        return result
    except Exception as e:
        return []
