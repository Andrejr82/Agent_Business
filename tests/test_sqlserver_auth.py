import pytest
from unittest.mock import MagicMock, patch
from core.database import sqlserver_auth
from core.database.database import DatabaseConnectionManager # Import the actual class

# Mock the bcrypt library
# We'll assume bcrypt is installed and functional for this test
# In a real scenario, you might mock bcrypt.checkpw directly
# For now, we'll simulate a successful check if password matches "test_password"
# and a stored hash that would correspond to "test_password"
MOCKED_BCRYPT_HASH = b"$2b$12$1azbZQ85FNNRbvqtVxRqGOHheHGvwLowTNJmG9M7iM/aXEEBHjDaq"

@pytest.fixture
def mock_db_manager():
    """Fixture to mock the DatabaseConnectionManager and its methods."""
    with patch('core.database.database.DatabaseConnectionManager', autospec=True) as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.test_connection.return_value = (True, "Conexão bem-sucedida")
        mock_instance.execute_query_one.return_value = None # Default to no user found
        yield mock_instance

@pytest.fixture
def mock_get_db_manager(mock_db_manager):
    """Fixture to mock the get_db_manager function."""
    with patch('core.database.sqlserver_auth.get_db_manager', return_value=mock_db_manager):
        yield mock_db_manager

def test_initialize_db_success(mock_get_db_manager):
    """Test initialize_db when connection is successful."""
    sqlserver_auth.initialize_db()
    mock_get_db_manager.test_connection.assert_called_once()

def test_initialize_db_failure(mock_get_db_manager):
    """Test initialize_db when connection fails."""
    mock_get_db_manager.test_connection.return_value = (False, "Erro de conexão")
    with pytest.raises(ConnectionError, match="Não foi possível conectar ao SQL Server"):
        sqlserver_auth.initialize_db()
    mock_get_db_manager.test_connection.assert_called_once()

def test_verify_user_success(mock_get_db_manager):
    """Test verify_user with correct credentials."""
    # Simulate a user found in the database
    mock_get_db_manager.execute_query_one.return_value = (
        "testuser", MOCKED_BCRYPT_HASH.decode('utf-8'), "admin"
    )
    
    # Temporarily, for testing without actual bcrypt check in the test file
    # The sqlserver_auth.py has a placeholder for "test_password"
    user_data = sqlserver_auth.verify_user("testuser", "test_password")
    
    assert user_data is not None
    assert user_data["username"] == "testuser"
    assert user_data["role"] == "admin"
    mock_get_db_manager.execute_query_one.assert_called_once_with(
        "SELECT username, password_hash, role FROM users WHERE username = :username",
        {"username": "testuser"}
    )

def test_verify_user_invalid_password(mock_get_db_manager):
    """Test verify_user with incorrect password."""
    mock_get_db_manager.execute_query_one.return_value = (
        "testuser", MOCKED_BCRYPT_HASH.decode('utf-8'), "admin"
    )
    
    # Temporarily, for testing without actual bcrypt check in the test file
    # The sqlserver_auth.py has a placeholder for "test_password"
    user_data = sqlserver_auth.verify_user("testuser", "wrong_password")
    
    assert user_data is None
    mock_get_db_manager.execute_query_one.assert_called_once()

def test_verify_user_not_found(mock_get_db_manager):
    """Test verify_user when user is not found."""
    mock_get_db_manager.execute_query_one.return_value = None # No user found
    user_data = sqlserver_auth.verify_user("nonexistent", "anypassword")
    assert user_data is None
    mock_get_db_manager.execute_query_one.assert_called_once()

def test_verify_user_exception(mock_get_db_manager):
    """Test verify_user when an exception occurs during query execution."""
    mock_get_db_manager.execute_query_one.side_effect = Exception("Database error")
    user_data = sqlserver_auth.verify_user("testuser", "test_password")
    assert user_data is None
    mock_get_db_manager.execute_query_one.assert_called_once()
