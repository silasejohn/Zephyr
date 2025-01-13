# Zephyr

*True to its name, Zephyr delivers subtle yet powerful insights that can shape the outcome of your scouting & tournament draft. While it won’t guarantee victory, its meticulous analysis of opponents provides the strategic advantage needed to tip the balance in your favor, setting the stage for success before your match even starts*

## Project Structure
```
project_root/
│
├── data/                       # data storage
│   ├── raw/                    # (raw) data
│   └── synthesized/            # (processed) data
│
├── scripts/                    # python scripts
│   ├── __init__.py
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── opgg_profile_scraper.py     # Contains scraping logic with Selenium
│   │   └── api_client.py               # For API interactions
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── data_processor.py   # Handles data processing and transformations
│   │   └── output_formatter.py # Formats data for output (e.g., CSV, JSON)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_manager.py     # Manages reading/writing CSV and JSON
│       └── helpers.py          # Miscellaneous utility functions
│
├── notebooks/                  # Jupyter notebooks for exploratory analysis
│
├── config/                     # Configuration files
│   └── settings.py             # Configuration for scraping, APIs, paths
│
├── tests/                      # Test cases for your modules
│
├── .gitignore
├── README.md
└── requirements.txt            # Dependencies for the project

```

https://developers.google.com/sheets/api/quickstart/python

[Activate Virtual Environment] `source hw2-env/bin/activate`
[Changing Scope Locally] Delete `config/token.json`
[Configure Run Button to Virtual Env] CMD + SHIFT + P ~> Select Appropriate Interpreter (auto configures run button)