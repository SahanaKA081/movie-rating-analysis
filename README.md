# Movie Rating Analysis and Genre Popularity Using MongoDB

A full-stack, beginner-friendly college project built with **Python (Flask)**, **PyMongo**, **MongoDB**, **Bootstrap 5**, and **Chart.js** for analyzing movie rating distributions, genre popularity, and audience trends.

Developed for college **IA-2 Activity / Practical-Based Learning** evaluation.

---

## 🌟 Key Features

* **Dataset Seeding Script (`seed_data.py`)**: Automatically generates and inserts 500+ realistic rating documents spanning 8 distinct genres, multiple users, and duplicate-prevention indexes.
* **Executive Dashboard**: Live KPI metric cards, Top Rated Movies bar chart, Genre Popularity doughnut chart, Rating frequency histogram, and real-time automated insights.
* **Data Management (CRUD)**: Search by movie title, filter by genre, sort by multiple criteria, paginate results, add new ratings, edit existing records, and delete with confirmation dialogs.
* **Deep Aggregation Analytics**: Custom MongoDB aggregation pipelines calculating vote-threshold top movies, review volume rankings, genre performance comparisons, and release year trends.
* **Viva Code Reference**: Includes live MongoDB pipeline code snippets on the analysis page for practical viva questions.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3 (Custom Dark Navy Cinema Theme), Bootstrap 5.3, Chart.js 4.4, FontAwesome 6.4
* **Backend**: Python 3.9+, Flask 3.0+
* **Database**: MongoDB (Local or MongoDB Atlas)
* **Database Driver**: PyMongo 4.6+
* **Environment Config**: `python-dotenv`

---

## 📂 Project Structure

```
movie-rating-analysis/
├── app.py                 # Main Flask application with Web & REST API routes
├── seed_data.py           # MongoDB dataset seeding script (500+ documents)
├── test_app.py            # Automated unit tests for API & database operations
├── requirements.txt       # Python dependencies list
├── .env.example           # Environment configuration template
├── .env                   # Local configuration file
├── README.md              # Project documentation & setup guide
├── templates/
│   ├── base.html          # Base Bootstrap layout template
│   ├── index.html         # Dashboard template
│   ├── ratings.html       # Ratings Data Table & CRUD modals template
│   └── analysis.html      # Deep Aggregation Analysis template
├── static/
│   ├── css/
│   │   └── style.css      # Dark-mode cinema visual styling
│   └── js/
│       ├── dashboard.js   # Dashboard charts & KPI logic
│       ├── ratings.js     # CRUD operations & pagination logic
│       └── analysis.js    # Deep analysis charts logic
└── docs/
    └── project_report.md  # Complete academic report with 25 Viva Q&As
```

---

## 🚀 Quick Setup and Execution Guide

### 1. Prerequisites
Ensure you have installed:
* **Python 3.9+**
* **MongoDB Community Server** (running locally on port 27017) or a **MongoDB Atlas Connection URI**.

### 2. Install Python Dependencies
Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` (already created by default):

```ini
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=movieDB
COLLECTION_NAME=ratings
FLASK_PORT=5000
FLASK_DEBUG=True
```

*Note: If using MongoDB Atlas, update `MONGO_URI` with your connection string.*

### 4. Seed the MongoDB Database
Run the seed script to create the database `movieDB`, set up unique indexes, and insert 500+ rating documents:

```bash
python seed_data.py
```

Expected Output:
```text
Connecting to MongoDB at mongodb://localhost:27017/...
Connected to MongoDB successfully!
Clearing existing collection 'ratings' in database 'movieDB'...
Creating MongoDB indexes...
Generating synthetic movie rating dataset...
Inserting 550 rating records into MongoDB...

==================================================
SEEDING COMPLETED SUCCESSFULLY!
==================================================
Database Name       : movieDB
Collection Name     : ratings
Inserted Documents  : 550
Distinct Movies     : 40
Distinct Users      : 90
Distinct Genres     : 8
==================================================
```

### 5. Start the Flask Server
Run the Flask server:

```bash
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Automated Testing

To verify all REST API endpoints and CRUD operations, run the unit test suite:

```bash
python test_app.py
```

---

## 📚 Viva Questions & Project Documentation

Refer to **`docs/project_report.md`** for a comprehensive academic report, including:
* System Architecture Diagram
* Complete Aggregation Pipeline Explanations (`$match`, `$group`, `$sort`, `$limit`, `$avg`, `$sum`, `$addToSet`)
* **25 Faculty Viva Questions & Answers**
* Instructions for taking screenshots for practical submission.

---

## 🔧 Troubleshooting

| Error | Cause | Solution |
| :--- | :--- | :--- |
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB service is not running locally. | Start your MongoDB service (`net start MongoDB` on Windows) or check `MONGO_URI` in `.env`. |
| `DuplicateKeyError: E11000` | User has already rated the specified movie. | A user cannot rate the same movie twice. Use a different `user_id` or movie title. |
| `ModuleNotFoundError` | Missing Python package. | Run `pip install -r requirements.txt`. |
