# Acquired dependencies
from flask import Flask, jsonify, request
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync, ScalarType
from ariadne.explorer import ExplorerPlayground # Updated import
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
from AutoScout24Scraper import AutoScout24Scraper
from datetime import datetime
from pymongo.errors import BulkWriteError
from pymongo import MongoClient

# Initialize Flask app and scheduler
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Global variables to track scrapers and saved documents
scrapers = []
saved_documents_count = 0

# Load the GraphQL schema from the schema.graphql file
with open("schema.graphql", "r") as schema_file:
    type_defs = schema_file.read()

# Define resolvers
query = QueryType()
mutation = MutationType()

@query.field("status")
def resolve_status(*_):
    global scrapers

    # Update the status of each scraper
    for scraper_entry in scrapers:
        scraper = scraper_entry["scraper"]
        job = scheduler.get_job(scraper.scraper_id)
        scraper_entry.update({
            "make": scraper.make,
            "model": scraper.model,
            "interval": job.trigger.interval.total_seconds() if job else None,
            "running": job is not None,  # Check if the job is scheduled
            "documentsSaved": scraper_entry.get("documentsSaved", 0),
            "documentsFetched": scraper_entry.get("documentsFetched", 0),
            "job_id": scraper.scraper_id,
            "start_time": scraper_entry.get("start_time", datetime.now().isoformat()),
            "launch_count": scraper_entry.get("launch_count", 1),
            "next_run_time": job.next_run_time.isoformat() if job and job.next_run_time else None
        })

    return scrapers

@mutation.field("startScraper")
def resolve_start_scraper(_, info, make, model, interval, version, yearFrom, yearTo, powerFrom, powerTo, powerType, zip, zipRadius, priceTo):
    global scrapers

    # Check if a scraper with identical parameters already exists
    for scraper_entry in scrapers:
        scraper = scraper_entry["scraper"]
        if (scraper.make == make and scraper.model == model and scraper.version == version and
            scraper.year_from == yearFrom and scraper.year_to == yearTo and
            scraper.power_from == powerFrom and scraper.power_to == powerTo and
            scraper.powertype == powerType and scraper.zip == zip and
            scraper.zipr == zipRadius and scraper.price_to == priceTo):
            print("A scraper with identical parameters already exists.")
            return True

    # Generate a unique scraper ID
    scraper_id = f"scraper_{int(time.time())}"

    # Create a new scraper instance with the scraper ID
    scraper = AutoScout24Scraper(
        make=make,
        model=model,
        version=version,
        year_from=yearFrom,
        year_to=yearTo,
        power_from=powerFrom,
        power_to=powerTo,
        powertype=powerType,
        zip=zip,
        zipr=zipRadius,
        price_to=priceTo,
        scraper_id=scraper_id
    )

    scrapers.append({"scraper": scraper, "scraper_id": scraper_id, "documentsSaved": 0, "documentsFetched": 0})

    # Define the function to run the scraper
    def run_scraper():
        print(f"Job {scraper_id} is starting.")
        scraper.scrape(num_pages=1, verbose=True)
        fetched_count = len(scraper.listing_frame)
        now = datetime.now()
        for doc in scraper.listing_frame:
            if "createdAt" not in doc:
                doc["createdAt"] = now
        saved_count = scraper.save_to_mongo()
        for scraper_entry in scrapers:
            if scraper_entry["scraper_id"] == scraper_id:
                scraper_entry["documentsFetched"] += fetched_count
                scraper_entry["documentsSaved"] += saved_count
                break

    scheduler.add_job(
        func=run_scraper,
        trigger="interval",
        seconds=interval,
        id=scraper_id,
        replace_existing=True
    )
    print(f"Job {scraper_id} has been scheduled to run every {interval} seconds.")

    return True

@query.field("fetchSavedDocuments")
def resolve_fetch_saved_documents(_, info, page=1, pageSize=10, model=None, mileageMin=None, mileageMax=None, yearMin=None, yearMax=None, priceMin=None, priceMax=None, createdAfter=None, db_name="autoscout24"):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db.saved_documents

    # Build the query with filters
    query_filter = {}
    if model:
        query_filter["model"] = model
    if mileageMin is not None:
        query_filter["mileage"] = {"$gte": mileageMin}
    if mileageMax is not None:
        query_filter.setdefault("mileage", {}).update({"$lte": mileageMax})
    if yearMin is not None:
        query_filter["year"] = {"$gte": yearMin}
    if yearMax is not None:
        query_filter.setdefault("year", {}).update({"$lte": yearMax})
    if priceMin is not None:
        query_filter["price"] = {"$gte": priceMin}
    if priceMax is not None:
        query_filter.setdefault("price", {}).update({"$lte": priceMax})
    if createdAfter:
        query_filter["createdAt"] = {"$gte": createdAfter}

    # Calculate skip and limit for pagination
    skip = (page - 1) * pageSize
    limit = pageSize

    # Fetch documents with pagination
    query = collection.find(query_filter).skip(skip).limit(limit)
    documents = [
        {
            "id": str(doc.get("_id")),
            "make": doc.get("make"),
            "model": doc.get("model"),
            "year": doc.get("year"),
            "price": doc.get("price"),
            "mileage": doc.get("mileage"),
            "location": doc.get("location"),
            "createdAt": doc.get("createdAt")
        }
        for doc in query
    ]

    # Debug: Log the documents being returned
    print("Documents Returned:", documents)

    return documents

# Custom scalar for ZonedDateTime
zoned_datetime_scalar = ScalarType("ZonedDateTime")

@zoned_datetime_scalar.serializer
def serialize_zoned_datetime(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise ValueError("Value is not a valid datetime object")

@zoned_datetime_scalar.value_parser
def parse_zoned_datetime(value):
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("Invalid ISO 8601 datetime format")

# Create executable schema
schema = make_executable_schema(type_defs, query, mutation, zoned_datetime_scalar)

# Retrieve HTML for the GraphiQL.
explorer_html = ExplorerPlayground().html(None)

@app.route("/playground", methods=["GET", "POST"])
def graphql_playground():
    if request.method == "POST":
        return graphql_server()
    return explorer_html, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Extract parameters from the request
        params = request.json
        make = params.get('make', 'volkswagen')
        model = params.get('model', 'golf')
        year_from = params.get('year_from', 2015)
        year_to = params.get('year_to', 2020)
        power_from = params.get('power_from', 50)
        power_to = params.get('power_to', 200)
        powertype = params.get('powertype', 'kw')
        zip_code = params.get('zip', '38442-wolfsburg')
        zipr = params.get('zipr', 200)
        price_to = params.get('price_to', 6000)
        num_pages = params.get('num_pages', 1)

        # Initialize the scraper
        scraper = AutoScout24Scraper(
            make=make,
            model=model,
            version='',
            year_from=year_from,
            year_to=year_to,
            power_from=power_from,
            power_to=power_to,
            powertype=powertype,
            zip=zip_code,
            zipr=zipr,
            price_to=price_to
        )

        # Run the scraper
        scraper.scrape(num_pages=num_pages, verbose=True)

        # Save results to MongoDB
        scraper.save_to_mongo()

        # Quit the browser
        scraper.quit_browser()

        return jsonify({"message": "Scraping completed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")