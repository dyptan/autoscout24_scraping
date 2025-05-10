# AutoScout24 Scraper

## Overview
The AutoScout24 Scraper is a Python-based project designed to scrape car listings from the AutoScout24 website. It collects data such as make, model, mileage, fuel type, first registration date, price, and location (zip code) of vehicles. The scraped data is stored in a MongoDB database for further analysis and use.

## Features
- **Web Scraping**: Uses Selenium to scrape car listings from AutoScout24.
- **Data Storage**: Saves scraped data into a MongoDB database, ensuring unique entries using a unique index on the `ad-link` field.
- **GraphQL API**: Provides a GraphQL API for querying and managing scraping jobs.
- **Scheduler**: Uses APScheduler to schedule periodic scraping jobs.
- **Error Handling**: Handles duplicate entries and bulk write errors gracefully.

## Project Structure
- `AutoScout24Scraper.py`: Contains the main scraper class and logic for scraping and saving data.
- `http_server.py`: Implements a Flask server with GraphQL endpoints for managing scraping jobs.
- `schema.graphql`: Defines the GraphQL schema for the API.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `scrape_results.csv`: Example CSV file containing scraped data.
- `test_mongo_insertion.py`: Unit tests for MongoDB insertion logic.
- `test_bulk_write_error.py`: Unit tests for handling bulk write errors.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd autoscout24_scraping
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure you have MongoDB installed and running locally.
4. Download and set up the Chrome WebDriver compatible with your version of Google Chrome.

## Usage
### Running the Scraper
1. Edit the parameters in `AutoScout24Scraper.py` or use the GraphQL API to start a scraper.
2. Run the scraper:
   ```bash
   python AutoScout24Scraper.py
   ```

### Starting the HTTP Server
1. Start the Flask server:
   ```bash
   python http_server.py
   ```
2. Access the GraphQL Playground at `http://localhost:5000/graphql` to interact with the API.

### Example GraphQL Queries
#### Start a Scraper
```graphql
mutation {
  startScraper(
    make: "volkswagen",
    model: "golf",
    interval: 3600,
    version: "",
    yearFrom: 2015,
    yearTo: 2020,
    powerFrom: 50,
    powerTo: 200,
    powerType: "kw",
    zip: "38442-wolfsburg",
    zipRadius: 200,
    priceTo: 6000
  )
}
```

#### Query Scraper Status
```graphql
query {
  status {
    make
    model
    running
    documentsSaved
    documentsFetched
  }
}
```

## Testing
Run the unit tests to ensure everything is working correctly:
```bash
python -m unittest discover
```

## Dependencies
- Python 3.10
- Selenium
- Flask
- Ariadne
- APScheduler
- MongoDB
- Pandas
- Graphene

## License
This project is licensed under the MIT License.