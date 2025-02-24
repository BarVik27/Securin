from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  
Swagger(app)  


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


@app.route('/api/cves', methods=['GET'])
def get_cves():
    
   
    page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=10)
    cve_id = request.args.get('cveId', type=str, default="")
    cvss = request.args.get('cvss', type=float, default=None)
    date = request.args.get('date', type=str, default="")

   
    offset = (page - 1) * limit

    
    query = "SELECT * FROM cve_details WHERE 1=1"
    params = []

    if cve_id:
        query += " AND cve_id LIKE %s"
        params.append(f"%{cve_id}%")
    if cvss is not None:
        query += " AND base_score = %s"
        params.append(cvss)
    if date:
        query += " AND published_date >= %s"
        params.append(date)

    
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    results = cursor.fetchall()

    
    count_query = "SELECT COUNT(*) as total FROM cve_details WHERE 1=1"
    count_params = []

    if cve_id:
        count_query += " AND cve_id LIKE %s"
        count_params.append(f"%{cve_id}%")
    if cvss is not None:
        count_query += " AND base_score = %s"
        count_params.append(cvss)
    if date:
        count_query += " AND published_date >= %s"
        count_params.append(date)

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return jsonify({
        "results": results,
        "total": total,
        "page": page,
        "limit": limit
    })


@app.route('/cve/<cve_id>', methods=['GET'])
def get_cve_by_id(cve_id):
    
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


if __name__ == '__main__':
    app.run(debug=True)
