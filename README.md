# Steeleye

Steeleye is a Python project designed to extract, parse, and transform ISO 20022 financial data from XML files. It provides tools for processing regulatory reporting files and converting them into structured, analyzable data formats.

## Overview

Steeleye handles the extraction and transformation of ISO 20022 XML documents, particularly focused on financial instrument data. The project is organized into modular components:

- **Extract Module**: Retrieves and downloads financial data files
- **Transform Module**: Processes XML files and converts them to pandas DataFrames
- **Load Module**: NOT IMPLEMENTED

## Features

- Extract ISO 20022 XML data from ZIP archives
- Parse complex nested XML structures with proper namespace handling
- Convert XML data to pandas DataFrames for data analysis
- Comprehensive logging and error handling
- Full test coverage with unit and integration tests
- Support for ISO 20022 auth.036.001.02 schema

## Project Structure

```
steeleye/
├── src/
│   └── steeleye/
│       ├── extract/          # Data extraction module
│       └── transform/        # Data transformation module
├── tests/
│   ├── extract/              # Extract module tests
│   │   ├── __init__.py
│   │   ├── test_unit.py
│   │   └── test_int.py
│   └── transform/            # Transform module tests
│       ├── __init__.py
│       ├── test_unit.py
│       └── test_int.py
└── .gitignore
```

## Installation

### Prerequisites
- Python 3.13 or higher
- make (Standard in Linux and MacOS)
### Setup

1. Clone the repository:
```bash
git clone https://github.com/mArcio-Lmano/steeleye.git
cd steeleye
```

2. Install Poetry on a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install poetry
```

3. Install dependencies:
```bash
poetry install
```

## Usage
### Extract Module

The Extract module extracts a zip file from the URL

```python

from steeleye.extract.main import Extract
url = (
    "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?"
    "q=*&fq=publication_date:[2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z]"
    "&wt=xml&indent=true&start=0&rows=100"
)
extract = Extract(url)
extract.run()
```
### Transform Module

The Transform module extracts and processes ISO 20022 XML files:

```python
from steeleye.transform.main import Transform
transformer = Transform()
df = transformer.run()
print(df.head())
```

## Testing

### Run All Tests

```bash
make test
```

## Logging

Steeleye includes comprehensive logging at the INFO level:

```
2026-04-09 12:34:56,789 - Transform - INFO - Processing file 1: data.xml
```

Logs include:
- File processing progress
- Critical parsing errors
- Data transformation steps

## Error Handling

The module provides robust error handling:

- `FileNotFoundError`: Raised when ZIP files cannot be located
- `RuntimeError`: Raised when XML parsing fails
- Proper exception logging and reporting

## Dependencies

- `pandas`: Data manipulation and analysis
- `requests`: HTTP library for data retrieval

## License

This project is provided as-is without a specific license.

## Author

Created by [mArcio-Lmano](https://github.com/mArcio-Lmano)

