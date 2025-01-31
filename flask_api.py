from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

app = Flask(_name_)
CORS(app)  # Enable CORS for frontend communication
Swagger(app)  # Enable Swagger UI for API documentation


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  
            database="cve_data"
        )
        return conn
    except mysql.connector.Error as e:
        return None


@app.route('/cve/<cve_id>', methods=['GET'])
def get_cve_by_id(cve_id):
    """
    Get CVE details by CVE ID
    ---
    parameters:
      - name: cve_id
        in: path
        type: string
        required: true
        description: CVE ID (e.g., CVE-2023-1234)
    responses:
      200:
        description: CVE details
      404:
        description: CVE not found
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM cve_details WHERE cve_id = %s", (cve_id,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "CVE not found"}), 404

#  2. API to get CVEs by year
@app.route('/cve/year/<int:year>', methods=['GET'])
def get_cve_by_year(year):
    """
    Get CVEs from a specific year
    ---
    parameters:
      - name: year
        in: path
        type: integer
        required: true
        description: Year of the CVE (e.g., 2022)
    responses:
      200:
        description: List of CVEs
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM cve_details WHERE YEAR(published_date) = %s", (year,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

# 3. API to get CVEs by CVSS Score
@app.route('/cve/score', methods=['GET'])
def get_cve_by_score():
    """
    Get CVEs filtered by CVSS Score range
    ---
    parameters:
      - name: min
        in: query
        type: float
        required: false
        default: 0.0
        description: Minimum CVSS Score
      - name: max
        in: query
        type: float
        required: false
        default: 10.0
        description: Maximum CVSS Score
    responses:
      200:
        description: List of CVEs within the score range
    """
    min_score = request.args.get('min', type=float, default=0.0)
    max_score = request.args.get('max', type=float, default=10.0)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM cve_details 
        WHERE base_score BETWEEN %s AND %s
    """, (min_score, max_score))
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

#  4. API to get CVEs modified in the last N days
@app.route('/cve/recent/<int:days>', methods=['GET'])
def get_recent_cves(days):
    """
    Get CVEs modified in the last N days
    ---
    parameters:
      - name: days
        in: path
        type: integer
        required: true
        description: Number of days (e.g., 30 for last month)
    responses:
      200:
        description: List of CVEs modified in the last N days
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    cursor.execute("""
        SELECT * FROM cve_details 
        WHERE last_modified_date >= %s
    """, (cutoff_date,))
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

if _name_ == '_main_':
    app.run(debug=True)