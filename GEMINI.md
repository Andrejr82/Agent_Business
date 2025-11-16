## Project Overview

This project is a Business Intelligence (BI) assistant. It's built with Python and features a web interface created with Streamlit. The primary goal of the project is to provide data insights and analysis in an accessible way.

The system uses a combination of technologies to achieve its goals:
- **Backend:** Python, with Flask for the API (implied by `core/api` and common Python BI setups).
- **Frontend:** Streamlit for the interactive user interface.
- **Data Storage:** It can connect to a SQL Server database and also read data from Parquet and JSON files.
- **Natural Language Processing:** It uses the Google Gemini API and the LangChain library to process natural language queries from users.
- **Agent-based Architecture:** The core of the application is an agent-based system. A `SupervisorAgent` routes user queries to a `ToolAgent`, which in turn uses a set of tools to interact with the available data sources. A `DataSourceManager` abstracts the data access, allowing the tools to query different data sources with a unified interface. A `CodeGenAgent` is also mentioned for RAG processes.
- **Database Migrations:** Alembic is used to manage database schema changes (indicated by `alembic.ini` and `migrations/`).

## Building and Running

To set up and run the project locally, follow these steps:

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the environment variables:**
    Create a `.env` file in the root of the project, based on the `.env.example` file, and fill in your credentials and configurations. Example:
    ```
    MSSQL_SERVER=your_sql_server
    MSSQL_DATABASE=your_database
    MSSQL_USER=your_user
    MSSQL_PASSWORD=your_password
    DB_DRIVER={ODBC Driver 17 for SQL Server}
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```

## Development Conventions

- **Configuration:** The project uses a `.env` file for configuration. A `Config` class in `core/config/config.py` loads the environment variables (inferred from common patterns).
- **Data Access:** A `DataSourceManager` in `core/data_source_manager.py` provides a unified interface for accessing data from different sources.
- **Agent-based architecture:** The query processing is handled by a system of agents built with LangChain. Key agents include `SupervisorAgent` and `ToolAgent`.
- **Tooling:** The agent uses a set of tools defined in `core/tools/` to perform specific tasks.
- **Database Migrations:** Database schema changes are managed with Alembic. The migration scripts are located in the `migrations` directory.
- **Testing:** The project has a `tests` directory and `pytest.ini`, indicating that it uses `pytest` for its test suite.
- **Code Style:** The project seems to follow the standard Python code style (PEP 8), as no specific linter configuration (other than ruff cache) or style guide was explicitly found, but it's a common practice.
