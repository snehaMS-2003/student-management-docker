# Student Management System – CRUD Web Dashboard

A simple, beginner-friendly, and modern Student Management System built using Python (Flask), MySQL, Bootstrap 5, and Docker. This project demonstrates basic CRUD operations (Create, Read, Update, Delete) and Docker multi-container orchestration.

---

## 1. Features

- **Modern Admin Dashboard:**
  - Metric stat cards displaying total students and academic departments.
  - Recent students overview table.
  - Sidebar navigation and light, responsive UI.
- **Student Management (CRUD):**
  - **Create:** Add new students with auto-generated ID, name, email, phone, department, gender, and date of birth.
  - **Read:** View student list with dynamic search (name, email, department).
  - **Update:** Pre-fill existing record and update details in MySQL.
  - **Delete:** Interactive confirmation modal before permanent deletion.
- **RESTful API Backend:**
  - Modular Flask architecture using blueprints.
  - Parameterized queries to prevent SQL injection.
  - Standard HTTP response codes (`200`, `201`, `400`, `404`, `409`, `422`, `500`).
- **Containerization:**
  - Multi-container setup with Docker and Docker Compose.
  - Health checks ensuring Flask starts only after MySQL is ready.
  - Persistent MySQL data volume.

---

## 2. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5, Bootstrap Icons
- **Backend:** Python 3.11, Flask
- **Database:** MySQL 8.0
- **Containerization:** Docker, Docker Compose

---

## 3. Project Structure

```text
student-management/
│
├── app/
│   ├── __init__.py          # Flask app initialization and factory
│   ├── routes.py            # Page routes & REST API endpoints
│   ├── database.py          # MySQL database connection & setup
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Main layout with sidebar and header
│   │   ├── dashboard.html   # Admin dashboard statistics
│   │   ├── students.html    # Student directory and table
│   │   └── student_form.html# Add & Edit student form
│   └── static/
│       ├── css/
│       │   └── style.css    # Custom styles
│       └── js/
│           └── app.js       # Asynchronous CRUD frontend logic
│
├── Dockerfile               # Web container specification
├── docker-compose.yml       # Multi-container orchestration (web + db)
├── requirements.txt         # Python dependencies
├── .dockerignore            # Files ignored during Docker build
├── .env.example             # Example environment variables
├── .env                     # Local environment settings
├── init.sql                 # Database initialization & sample data
├── run.py                   # Application entry point
└── README.md                # Project documentation
```

---

## 4. Prerequisites

Make sure you have installed on your machine:
- [Docker](https://www.docker.com/) & Docker Compose
- Or Python 3.10+ and a local MySQL server (if running without Docker)

---

## 5. Quick Start with Docker (Recommended)

### Step 1: Clone or navigate to the directory
```bash
cd "c:\Users\sneha\Downloads\containers micro project"
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` (already done by default):
```bash
cp .env.example .env
```

### Step 3: Build and Run Containers
Build and start the web application and MySQL database in one command:
```bash
docker compose up --build
```
> Add `-d` to run in detached (background) mode: `docker compose up --build -d`

### Step 4: Access the Application
Open your browser and navigate to:
**[http://localhost:5000](http://localhost:5000)**

---

## 6. REST API Documentation

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/dashboard` | Dashboard metrics & recent students | 200, 500 |
| `GET` | `/api/students` | List all students (supports `?search=term`) | 200, 500 |
| `GET` | `/api/students/<id>` | Retrieve a single student by ID | 200, 404, 500 |
| `POST` | `/api/students` | Create a new student record | 201, 400, 409, 422, 500 |
| `PUT` | `/api/students/<id>` | Update an existing student | 200, 400, 404, 409, 422, 500 |
| `DELETE` | `/api/students/<id>` | Delete a student record | 200, 404, 500 |

### Sample JSON Payload for `POST` / `PUT`:
```json
{
  "name": "Alex Morgan",
  "email": "alex.morgan@university.edu",
  "phone": "+1-555-0188",
  "department": "Computer Science",
  "gender": "Female",
  "date_of_birth": "2001-07-24"
}
```

---

## 7. Stopping and Managing Containers

### Stop containers:
```bash
docker compose down
```

### Stop containers and remove volumes (clean database reset):
```bash
docker compose down -v
```

### View container logs:
```bash
docker compose logs -f web
docker compose logs -f db
```

---

## 8. Running Locally without Docker (Optional)

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your local database credentials in `.env` (`DB_HOST=localhost`).
4. Start the application:
   ```bash
   python run.py
   ```

