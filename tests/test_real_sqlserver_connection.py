import pytest
import os
from core.database.database import get_db_manager
from core.config.config import Config

# Load environment variables for the test
# This ensures that the test picks up the .env file
# In a real application, Config() would handle this.
# For testing, we explicitly load it if not already loaded.
if not os.environ.get("DB_SERVER"):
    from dotenv import load_dotenv
    load_dotenv()

@pytest.fixture(scope="module")
def db_manager():
    """Provides a DatabaseConnectionManager instance for real connection tests."""
    # Ensure Config is initialized to load .env variables
    Config() 
    manager = get_db_manager()
    yield manager
    # Clean up resources after tests in the module are done
    manager.close()

def test_sqlserver_connection(db_manager):
    """
    Tests if the application can establish a connection to the SQL Server
    using the credentials provided in the .env file.
    """
    print("\nAttempting to connect to SQL Server...")
    success, message = db_manager.test_connection()
    print(f"Connection Test Result: Success={success}, Message={message}")
    assert success, f"Failed to connect to SQL Server: {message}"

# You could add more tests here to verify basic queries or authentication
# once the connection is established.
# For example:
# def test_sqlserver_auth_initialize_db(db_manager):
#     """Tests the initialize_db function of sqlserver_auth."""
#     from core.database import sqlserver_auth
#     try:
#         sqlserver_auth.initialize_db()
#         assert True
#     except ConnectionError as e:
#         pytest.fail(f"sqlserver_auth.initialize_db failed: {e}")

# def test_sqlserver_auth_verify_user(db_manager):
#     """
#     Tests user verification with a known user in the actual SQL Server.
#     This requires a pre-existing user in the database.
#     """
#     from core.database import sqlserver_auth
#     # IMPORTANT: Replace with actual username and password from your SQL Server
#     # And ensure the password_hash in DB matches the bcrypt hash of 'real_password'
#     test_username = "your_test_user"
#     test_password = "your_test_password" # This should be the plaintext password
#     
#     # This test will only pass if 'your_test_user' exists in your SQL Server
#     # with a bcrypt hashed password matching 'your_test_password'
#     user_data = sqlserver_auth.verify_user(test_username, test_password)
#     assert user_data is not None, f"Authentication failed for user {test_username}"
#     assert user_data["username"] == test_username
#     # You might want to check the role as well
#     # assert user_data["role"] == "expected_role"

