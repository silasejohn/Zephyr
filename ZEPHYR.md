# Zephyr

Zephyr is a comprehensive project designed to interact with multiple APIs, including Riot API, scrape data from various websites, and manage data efficiently. The project is modular, scalable, and organized for easy navigation and maintenance. Below is an overview of all components, their features, and a graphical representation of the project structure.

## Features

### API Clients
- **Riot API Client**: Modular interaction with Riot's different categorial apis (e.g., `MATCH_V5`, `ACCOUNT_V1`).
  - **Craft Functions**: Construct API requests with required parameters.
  - **Process Functions**: Handle API responses, retry logic, and error handling.
  - **Queue System**: An API queue that processes requests asynchronously, with retry logic and logging.

- **Google API Client**: Integration for reading and editing Google Spreadsheets, supporting data handling and updates.

### Scrapers
- **Website Scrapers**: Dedicated scripts for scraping data from various websites.
  - Includes utility functions to handle common scraping tasks and manage data outputs.

### Data Handling
- **Raw Data Storage**: Unprocessed data collected from API responses and scrapers.
- **Synthesized Data**: Processed and refined data ready for analysis or further use.
- **Data Models**: Structured DTOs (Data Transfer Objects) and common data structures for consistent data manipulation.

### Utilities
- Utility scripts to support various functions across API clients and scrapers.
- Functions for file handling, data saving/loading, and common tasks.

### Example Scripts
- Practical examples demonstrating the use of different classes and functions.
- Guides on integrating various features into larger projects.

## Project Structure

```markdown
Zephyr
├── config               # env vars, setup, credentials
├── constants            # json game constants, global references
├── data                 # data storagee
│   ├── raw
│   ├── processed
│   ├── synthesized
│   └── test
├── models               # Data Transfer Objects (DTOs) and data structures
├── modules              # Core functional modules
│   ├── api_clients      # API client modules
│   │   ├── google_client       # api client for google (spec. gspreadsheet view/edit)
│   │   └── riot_client         # api client for riot (data access & processing)
│   │       └── services # service classes for each API endpoint category (api call crafting & processing)
│   ├── scrapers         # web scraping scripts for target websites
│   └── utils            # utility scripts for repetitive tasks (data save & load, api utilities)
├── samples              # example scripts & usage guides
```

## How to Use
1. Set up configurations: Place environment variables and credentials in the configurations folder.
2. Run Example Scripts: Navigate to the samples folder for guided usage of various classes and functions.
3. Modify Data Models: Extend or update data models in the models folder to fit new data requirements.
4. Use API Clients: Utilize the riot_client and google_client modules to interact with respective APIs.
5. Run Scrapers: Execute scraper scripts in the scrapers folder to collect data from websites.
6. Extend Utilities: Add or modify utility scripts in the utils folder to support new features.

## Local DB Folder Structure
```markdown
Zephyr
├── databases
│   ├── local_db               # Local database interactions (SQLite, MySQL, etc.)
│   │   ├── __init__.py
│   │   ├── models.py          # ORM models or raw SQL queries
│   │   ├── connections.py     # DB connection and setup
│   │   ├── queries.py         # Query functions (CRUD)
│   │   └── migrations.py      # Schema migrations, if needed

Zephyr
├── databases
│   ├── remote_db              # Remote database interactions
│   │   ├── __init__.py
│   │   ├── models.py          # ORM models or raw SQL queries
│   │   ├── connections.py     # Remote DB connection (RDS, etc.)
│   │   ├── queries.py         # Query functions (CRUD)
│   │   └── migrations.py      # Schema migrations

Zephyr
├── config                    # Configuration files (env variables, setup, credentials)
├── constants                 # Game constants, key:value references
├── data                      # Data storage (raw, synthesized, test)
│   ├── raw
│   ├── processed
│   ├── synthesized
│   └── test
├── models                    # Data Transfer Objects (DTOs) and data structures
├── samples                   # Example scripts and usage guides
├── modules                   # Core functional modules
│   ├── api_clients           # API client modules (Google, Riot, etc.)
│   │   ├── google_client
│   │   └── riot_client
│   │       └── services
│   ├── scrapers              # Web scraping scripts for multiple websites
│   ├── utils                 # Utility scripts for common tasks
│   ├── databases             # Database integration (local, remote)
│   │   ├── local_db          # Local database interactions
│   │   ├── remote_db         # Remote database interactions
│   │   └── migrations.py     # Schema migrations and versioning
```

Key Points:
connections.py: This file would handle the database connection logic and configurations, like database credentials, database selection, etc.
models.py: If you're using an ORM like SQLAlchemy, this file will define the database schema and structure. If using raw SQL, you might just store the schema here.
queries.py: Contains functions that handle actual CRUD operations.
migrations.py: If you're using a database migration tool (e.g., Alembic for SQLAlchemy), this would store migration scripts.

Key Points for Remote Databases:
connections.py: In this file, you'd store the credentials and configurations for connecting to the remote database (host, user, password, database name, etc.). You might also want to handle connection pooling here.
models.py & queries.py: Same as with the local database but configured to interact with the remote DB.
migrations.py: If using migration tools for versioning your database schema, this file will store migration steps.

## Avoid Redudant Data Purchase via API Calls
If your goal is to avoid making redundant API calls and instead store data locally for future use, a database can be a solution, but it may not always be the most efficient approach depending on your use case. Instead, the problem can often be solved by using caching strategies or persistent storage systems that allow you to check whether data has already been retrieved before making another API call.

Solution 1: DB for Persistent Storage
... treat db as a cache that holds prev fetched data, query it b4 making a new api call
... local db like SQLite (or lightweight json store) 
... design db sceme (either store api call metadata OR actual returned data from API)

Solution 2: In-Memory Caching (Faster) 
... avoid redudant api calls w/in single runtime of application (no persistence btwn sessions)
... options: redis, memory_cache, TTL, cachetools
... (1) Create Key based off of API endpoints and params and cache value = api call response
... (2) if the data exists in the cache, return it ... else make the api call + cache result + return

Solution 3: Hybrid
... (1) Check In-Mmeory Cache for Data
... (2) if not in the cache, query the DB
... (3) if not found... fetch it from teh API + update both cache AND DB

Solution 4: Efficient Data Expiration
... used for both DB (cleanup mechanism on stale data) && Cacheing (TTL)

