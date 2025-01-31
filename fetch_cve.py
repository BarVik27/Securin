import requests
import mysql.connector
import datetime
import time

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'cve_data',
    'port': 3307  # Since we mapped port 3307 in Docker
}

# NVD API URL
BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Function to connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to create the table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cve_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cve_id VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            published_date DATETIME,
            last_modified_date DATETIME,
            base_score FLOAT,
            severity VARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()

# Function to fetch CVE data from API
def fetch_cve_data(start_index=0, results_per_page=10, last_modified_days=None):
    params = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page
    }

    # If last_modified_days is provided, fetch only recently modified records
    if last_modified_days:
        last_modified_filter = (datetime.datetime.now() - datetime.timedelta(days=last_modified_days)).strftime('%Y-%m-%dT%H:%M:%S')
        params["lastModStartDate"] = last_modified_filter

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("vulnerabilities", [])
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

# Function to insert data into MySQL
def insert_cve_data(cve_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    insert_count = 0
    for cve_entry in cve_data:
        cve_id = cve_entry.get("cve", {}).get("id")
        description = cve_entry.get("cve", {}).get("descriptions", [{}])[0].get("value", "No description available")
        published_date = cve_entry.get("cve", {}).get("published", "1970-01-01T00:00:00")[:19]
        last_modified_date = cve_entry.get("cve", {}).get("lastModified", "1970-01-01T00:00:00")[:19]
        base_score = cve_entry.get("cve", {}).get("metrics", {}).get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseScore", None)
        severity = cve_entry.get("cve", {}).get("metrics", {}).get("cvssMetricV2", [{}])[0].get("baseSeverity", "Unknown")

        # Check if CVE already exists
        cursor.execute("SELECT COUNT(*) FROM cve_details WHERE cve_id = %s", (cve_id,))
        exists = cursor.fetchone()[0]

        if exists == 0:
            cursor.execute("""
                INSERT INTO cve_details (cve_id, description, published_date, last_modified_date, base_score, severity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cve_id, description, published_date, last_modified_date, base_score, severity))
            insert_count += 1
        else:
            print(f"Skipping duplicate CVE: {cve_id}")

    conn.commit()
    conn.close()
    print(f"{insert_count} new records inserted successfully.")

# Function to periodically sync data (incremental updates)
def periodic_sync(interval_minutes=60, last_modified_days=1):
    while True:
        print("\nFetching updated CVE data...")
        cve_data = fetch_cve_data(last_modified_days=last_modified_days)
        if cve_data:
            insert_cve_data(cve_data)
        else:
            print("No new CVE data found.")
        
        print(f"Sleeping for {interval_minutes} minutes before the next sync...")
        time.sleep(interval_minutes * 60)

# Main execution
if __name__ == "__main__":
    create_table()  # Ensure table exists before inserting data
    
    # Fetch initial data (set results_per_page to a higher value to get more data)
    print("Fetching initial CVE data...")
    cve_data = fetch_cve_data(results_per_page=50)
    insert_cve_data(cve_data)

    # Start periodic sync (fetch updates every 60 minutes, checking for last 1-day changes)
    periodic_sync(interval_minutes=60, last_modified_days=1)
