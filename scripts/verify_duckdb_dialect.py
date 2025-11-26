import duckdb_engine
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry

try:
    # Attempt to explicitly register the DuckDB dialect
    # This is the same logic added to core/database/duckdb_auth.py
    registry.register('duckdb', 'duckdb_engine.dialect', 'DuckDBDialect')
    print('DuckDB dialect explicitly registered.')

    # Attempt to create an engine
    engine = create_engine('duckdb:///:memory:')
    print('DuckDB engine created successfully.')

except Exception as e:
    print(f'Error during DuckDB dialect verification: {e}')
    import sys
    sys.exit(1) # Exit with an error code if verification fails
