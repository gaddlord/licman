# Expense Tracker

A Flask application for tracking expenses with MySQL database integration.

## Features

- Plan expenses for budget years
- Track actual spend for expenses
- See overrun for expenses
- Filter expenses by year, organization, category using a dropdown
- Responsive UI built with Bootstrap, Flask
- Backend built with SQLAlchemy, pymysql, python-dotenv

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
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
```python
python3 app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
expense_tracker/
├── app.py                  # Main Flask application
├── init_db.py              # Initialize the database for the first time
├── models/
│   └── ddl.sql             # Database DDL created with DBeaver
│   └── models.py           # SQLAlchemy models
├── static/
│   └── css/
│       └── style.css       # Custom CSS styles
│   └── ico/
│       └── favicon.ico     # Custom Favorites Browser icon
│   └── svg/
│       └── logo.svg        # AppFire logo
├── templates/
│   └── index.html          # Main page listing expenses with filters
│   └── expense_detail.html # Expense detail read-only page with Edit, Delete buttons
│   └── expense_new.html    # Create new expense page
│   └── expense_edit.html   # Edit existing expense
│   └── help.html           # Help page
├── .env                    # Environment variables (this file is gitignored)
├── README.md               # This very file
└── requirements.txt        # Python dependencies
```

## Database Schema

The application uses the following main tables:
- `Accounts`: Contains general ledger accounts (e.g. 6504 - Cloud Services)
- `Category`: Contains available categories for filtering (e.g. SW - Software, HW - Hardware)
- `Expense`: Contains the planned expenses and actual spend. This is the master table to which all other link
- `Groups`: Contains general ledger groups (e.g. COS, G&A)
- `LicenseModel`: Defined possible ways to charge for licenses (e.g. Fixed Fee, Subscription, etc.)
- `Licenses`: Contains the licenses given to employees
- `Organization`: Defines the organizations to which the expenses are assigned (e.g. DevOps, ITOps)
- `Years`: Contains available fiscal years (e.g. FY25, FY24, FY23)

To re-init the database run

```bash
cd /Users/<user>>/repos/licman/expense_tracker && python3 -c "from init_db import init_db; init_db()"
```

## Environment Variables

Configure the .env file the following way:

```
LICMAN_PORT=5000
MYSQL_HOST=<database_host>.us-east-1.rds.amazonaws.com
MYSQL_USER=<database_user>
MYSQL_PASSWORD=<database_password>
MYSQL_DB=<database_name>
MYSQL_PORT=3306
```