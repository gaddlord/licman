# Expense Tracker

A Flask application for tracking expenses with MySQL database integration.

## Features

- List all expenses with details
- Filter expenses by year using a dropdown
- Responsive UI built with Bootstrap

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd expense_tracker
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Configure the database:
   - Make sure MySQL is running
   - Create a database named `licman` if it doesn't exist
   - Import the database schema from the `DDL.sql` file:
   ```
   mysql -u root -p licman < ../DDL.sql
   ```
   - Update the `.env` file with your MySQL credentials if needed

## Running the Application

1. Start the Flask application:
```
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
expense_tracker/
├── app.py                 # Main Flask application
├── models/
│   └── models.py          # SQLAlchemy models
├── static/
│   └── css/
│       └── style.css      # Custom CSS styles
├── templates/
│   └── index.html         # HTML template for the expense listing
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## Database Schema

The application uses the following main tables:
- `Expense`: Contains expense records with foreign keys to related tables
- `Years`: Contains available years for filtering
- Other reference tables: `Accounts`, `Category`, `Groups`, etc.

To reinit the database run

`cd /Users/<user>>/repos/licman/expense_tracker && python3 -c "from init_db import init_db; init_db()"`