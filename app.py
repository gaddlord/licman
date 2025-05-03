from flask import Flask, render_template, request, redirect, url_for
from models.models import db, Expense, Years, Organization, Category, Groups, LicenseModel, Accounts
from dotenv import load_dotenv
import os
import datetime
import pymysql
import re

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Custom Jinja2 filter for formatting numbers with apostrophe as thousand separator
@app.template_filter('format_number')
def format_number(value):
    return f"{value:,}".replace(",", "'")

@app.route('/')
def index():
    # Get all available filter options
    years = Years.query.all()
    organizations = Organization.query.all()
    categories = Category.query.all()
    
    # Get current year
    current_year = datetime.datetime.now().year
    
    # Extract numeric part from year IDs (e.g., 'FY25' -> 2025)
    def extract_year_number(year_id):
        # Extract digits from the year ID
        digits = re.findall(r'\d+', year_id)
        if not digits:
            return 0
        
        # Get the last set of digits (e.g., 'FY2025Q1' would return '2025')
        year_digits = digits[-1]
        
        # Handle 2-digit years (e.g., 'FY25' -> 2025)
        if len(year_digits) == 2:
            return 2000 + int(year_digits)
        
        # Handle 4-digit years or other formats
        return int(year_digits)
    
    # Find default year (current year or closest available)
    default_year = 'all'
    available_years = [year.YearId for year in years]
    
    if available_years:
        # Find the year closest to the current year
        closest_year = min(available_years, 
                          key=lambda x: abs(extract_year_number(x) - current_year))
        default_year = closest_year
    
    # Get selected filters (default year to current/closest, others to 'all' if not specified)
    selected_year = request.args.get('year', default_year)
    selected_organization = request.args.get('organization', 'all')
    selected_category = request.args.get('category', 'all')
    
    # Start with base query
    query = Expense.query
    
    # Apply filters if selected
    if selected_year and selected_year != 'all':
        query = query.filter_by(YearId=selected_year)
    
    if selected_organization and selected_organization != 'all':
        query = query.filter_by(OrganizationId=selected_organization)
    
    if selected_category and selected_category != 'all':
        query = query.filter_by(CategoryId=selected_category)
    
    # Execute query
    expenses = query.all()
    
    return render_template('index.html', 
                          expenses=expenses, 
                          years=years, 
                          organizations=organizations,
                          categories=categories,
                          selected_year=selected_year,
                          selected_organization=selected_organization,
                          selected_category=selected_category,
                          current_year=current_year)

@app.route('/expense/<int:expense_id>')
def expense_detail(expense_id):
    # Get the expense record
    expense = Expense.query.get_or_404(expense_id)
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    return render_template('expense_detail.html',
                          expense=expense,
                          current_year=current_year)

@app.route('/expense/new', methods=['GET', 'POST'])
def new_expense():
    # Get reference data for dropdowns
    years = Years.query.all()
    organizations = Organization.query.all()
    categories = Category.query.all()
    groups = Groups.query.all()
    license_models = LicenseModel.query.all()
    accounts = Accounts.query.all()
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    # Create a new expense object with default values
    expense = Expense(
        YearId='',
        AccountId=0,
        OrganizationId='',
        GroupId='',
        CategoryId='',
        Vendor='',
        Product='',
        LicenseModelId='',
        CostPerUnit=0.0,
        NumberOfUnits=0,
        ApprovedValue=0.0,
        ContractedValue=0.0,
        Sunset=False,
        SunsetPlan='',
        Notes='',
        ProcurementUrl='',
        EmployeeName='',
        EmployeeAnnualSalary=0.0,
        EmployeeAnnualBonus=0.0,
        EmployeeAnnualBenefits=0.0,
        TripName='',
        TripNumberOfPassengers=0,
        TrainingName='',
        TrainingNumberOfTrainees=0
    )
    
    # Handle form submission
    if request.method == 'POST':
        # Update expense with form data
        expense.YearId = request.form.get('year')
        expense.AccountId = int(request.form.get('account'))
        expense.OrganizationId = request.form.get('organization')
        expense.GroupId = request.form.get('group')
        expense.CategoryId = request.form.get('category')
        expense.Vendor = request.form.get('vendor')
        expense.Product = request.form.get('product')
        expense.LicenseModelId = request.form.get('license_model')
        expense.CostPerUnit = float(request.form.get('cost_per_unit') or 0)
        expense.NumberOfUnits = int(request.form.get('number_of_units') or 0)
        expense.ApprovedValue = float(request.form.get('approved_value') or 0)
        expense.ContractedValue = float(request.form.get('contracted_value') or 0)
        expense.Sunset = 'sunset' in request.form
        expense.SunsetPlan = request.form.get('sunset_plan')
        expense.Notes = request.form.get('notes')
        expense.ProcurementUrl = request.form.get('procurement_url')
        expense.EmployeeName = request.form.get('employee_name')
        
        # Handle optional numeric fields
        if request.form.get('employee_annual_salary'):
            expense.EmployeeAnnualSalary = float(request.form.get('employee_annual_salary'))
        if request.form.get('employee_annual_bonus'):
            expense.EmployeeAnnualBonus = float(request.form.get('employee_annual_bonus'))
        if request.form.get('employee_annual_benefits'):
            expense.EmployeeAnnualBenefits = float(request.form.get('employee_annual_benefits'))
        
        # Handle date field
        if request.form.get('employee_target_start_date'):
            try:
                expense.EmployeeTargetStartDate = datetime.datetime.strptime(
                    request.form.get('employee_target_start_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Handle other optional fields
        if request.form.get('trip_name'):
            expense.TripName = request.form.get('trip_name')
        if request.form.get('trip_number_of_passengers'):
            expense.TripNumberOfPassengers = int(request.form.get('trip_number_of_passengers') or 0)
        if request.form.get('training_name'):
            expense.TrainingName = request.form.get('training_name')
        if request.form.get('training_number_of_trainees'):
            expense.TrainingNumberOfTrainees = int(request.form.get('training_number_of_trainees') or 0)
        
        # Add to database
        db.session.add(expense)
        db.session.commit()
        
        # Redirect to detail page
        return redirect(url_for('expense_detail', expense_id=expense.ExpenseId))
    
    # Render new expense form
    return render_template('expense_new.html',
                          expense=expense,
                          years=years,
                          organizations=organizations,
                          categories=categories,
                          groups=groups,
                          license_models=license_models,
                          accounts=accounts,
                          current_year=current_year)

@app.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(expense_id):
    # Get the expense record
    expense = Expense.query.get_or_404(expense_id)
    
    # Get reference data for dropdowns
    years = Years.query.all()
    organizations = Organization.query.all()
    categories = Category.query.all()
    groups = Groups.query.all()
    license_models = LicenseModel.query.all()
    accounts = Accounts.query.all()
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    # Handle form submission
    if request.method == 'POST':
        # Update expense with form data
        expense.YearId = request.form.get('year')
        expense.AccountId = int(request.form.get('account'))
        expense.OrganizationId = request.form.get('organization')
        expense.GroupId = request.form.get('group')
        expense.CategoryId = request.form.get('category')
        expense.Vendor = request.form.get('vendor')
        expense.Product = request.form.get('product')
        expense.LicenseModelId = request.form.get('license_model')
        expense.CostPerUnit = float(request.form.get('cost_per_unit') or 0)
        expense.NumberOfUnits = int(request.form.get('number_of_units') or 0)
        expense.ApprovedValue = float(request.form.get('approved_value') or 0)
        expense.ContractedValue = float(request.form.get('contracted_value') or 0)
        expense.Sunset = 'sunset' in request.form
        expense.SunsetPlan = request.form.get('sunset_plan')
        expense.Notes = request.form.get('notes')
        expense.ProcurementUrl = request.form.get('procurement_url')
        expense.EmployeeName = request.form.get('employee_name')
        
        # Handle optional numeric fields
        if request.form.get('employee_annual_salary'):
            expense.EmployeeAnnualSalary = float(request.form.get('employee_annual_salary'))
        if request.form.get('employee_annual_bonus'):
            expense.EmployeeAnnualBonus = float(request.form.get('employee_annual_bonus'))
        if request.form.get('employee_annual_benefits'):
            expense.EmployeeAnnualBenefits = float(request.form.get('employee_annual_benefits'))
        
        # Handle date field
        if request.form.get('employee_target_start_date'):
            try:
                expense.EmployeeTargetStartDate = datetime.datetime.strptime(
                    request.form.get('employee_target_start_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Handle other optional fields
        if request.form.get('trip_name'):
            expense.TripName = request.form.get('trip_name')
        if request.form.get('trip_number_of_passengers'):
            expense.TripNumberOfPassengers = int(request.form.get('trip_number_of_passengers') or 0)
        if request.form.get('training_name'):
            expense.TrainingName = request.form.get('training_name')
        if request.form.get('training_number_of_trainees'):
            expense.TrainingNumberOfTrainees = int(request.form.get('training_number_of_trainees') or 0)
        
        # Save changes
        db.session.commit()
        
        # Redirect to detail page
        return redirect(url_for('expense_detail', expense_id=expense.ExpenseId))
    
    # Render edit form
    return render_template('expense_edit.html',
                          expense=expense,
                          years=years,
                          organizations=organizations,
                          categories=categories,
                          groups=groups,
                          license_models=license_models,
                          accounts=accounts,
                          current_year=current_year)

@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id):
    # Get the expense record
    expense = Expense.query.get_or_404(expense_id)
    
    # Delete the expense
    db.session.delete(expense)
    db.session.commit()
    
    # Redirect to the index page
    return redirect(url_for('index'))

@app.route('/help')
def help_page():
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    return render_template('help.html', current_year=current_year)

if __name__ == '__main__':
    app.run(debug=True, port=5004)
