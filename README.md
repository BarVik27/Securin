


## CVE Information API 
A Flask-based API that retrieves, stores, and serves Common Vulnerabilities and Exposures (CVE) data from the NVD API. It allows users to filter CVEs based on different parameters, view the data in a UI, and provides Swagger documentation for easy API testing.  

---

##  Features
- Fetch and store CVEs from the **NVD API** in a MySQL database  
- Filter CVEs by CVE ID, Year, CVSS Score, Last Modified Date**  
- Periodic data synchronization (batch update)  
- RESTful API endpoints with **Flask**  
- Swagger UI for API documentation  
- Simple UI with HTML, CSS, JavaScript  
- Docker support for containerized deployment  

---

##  Technologies Used
- Backend: Flask (Python)  
- Database: MySQL  
- Frontend: HTML, CSS, JavaScript  
- API Documentation: Flasgger (Swagger for Flask)  
- Containerization: Docker  

---

##  Getting Started
Follow these steps to set up the project locally.

### 1️. Clone the Repository
```bash
git clone https://github.com/yourusername/cve-api-flask.git
cd cve-api-flask
```

### 2. Install Dependencies
Make sure Python 3.8+ is installed. Then, install the required packages:  
```bash
pip install -r requirements.txt
```
OR manually install the required dependencies:  
```bash
pip install flask flasgger flask-cors mysql-connector-python
```

### 3️. Setup MySQL Database
1. Open MySQL Workbenchor use a terminal and create a database:
   ```sql
   CREATE DATABASE cve_data;
   ```
2. Create a table for storing CVEs:
   ```sql
   CREATE TABLE cve_details (
       id INT AUTO_INCREMENT PRIMARY KEY,
       cve_id VARCHAR(50) UNIQUE NOT NULL,
       published_date DATETIME,
       last_modified_date DATETIME,
       base_score FLOAT,
       description TEXT
   );
   ```
3. Update app.py`with your MySQL credentials inside `get_db_connection()`:
   ```python
   def get_db_connection():
       return mysql.connector.connect(
           host="localhost",
           user="root",       # Change if needed
           password="root",   # Your MySQL password
           database="cve_data"
       )
   ```

---

## Running the Project
### Start the Flask Server
```bash
python app.py
```
- The API will be available at: http://127.0.0.1:5000/  

### Open Swagger UI for API Docs
- Visit http://127.0.0.1:5000/api/docs  
- You can test API endpoints directly from Swagger UI  

---

🔗 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cve/<cve_id>` | `GET` | Get CVE details by ID |
| `/cve/year/<year>` | `GET` | Get CVEs from a specific year |
| `/cve/score?min=0.0&max=10.0` | `GET` | Get CVEs by CVSS score range |
| `/cve/recent/<days>` | `GET` | Get CVEs modified in the last N days |

---

  UI Integration
### 1️. Open `index.html` in your Browser
- The UI will display CVE records in a table  
- Click on a row to view detailed CVE information 
- Supports pagination and sorting by date

### 2️. Start a Simple HTTP Server for Testing
```bash
python -m http.server 8000
```
- Open http://127.0.0.1:8000/index.html in your browser  

---

##  Running with Docker (Optional)
### 1. Build the Docker Image
```bash
docker build -t cve-api .
```
### 2️. Run the Container
```bash
docker run -p 5000:5000 cve-api
```
- The API will now be accessible at http://localhost:5000/  

------------------------------------------------------
