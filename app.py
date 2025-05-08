from flask import Flask, render_template, request, redirect, url_for, make_response, g, session
from models.models import db, Expense, Years, Organization, Category, Groups, LicenseModel, Accounts, AuditLog
from utils.audit_logger import log_changes, log_create, log_delete
# Use flexible authentication that can be bypassed with SKIP_AUTH env variable
from flexible_auth import init_flexible_auth, flexible_login_required as login_required
from dotenv import load_dotenv
import os
import datetime
import pymysql
import re
import io
import csv
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase.pdfdoc import PDFCatalog, PDFInfo, PDFDictionary, PDFString

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

# Initialize flexible authentication
app = init_flexible_auth(app)

# Custom Jinja2 filter for formatting numbers with apostrophe as thousand separator
@app.template_filter('format_number')
def format_number(value):
    return f"{value:,}".replace(",", "'")

@app.route('/')
@login_required
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
    search_term = request.args.get('search', '')
    
    # Start with base query
    query = Expense.query
    
    # Apply filters if selected
    if selected_year and selected_year != 'all':
        query = query.filter_by(YearId=selected_year)
    
    if selected_organization and selected_organization != 'all':
        query = query.filter_by(OrganizationId=selected_organization)
    
    if selected_category and selected_category != 'all':
        query = query.filter_by(CategoryId=selected_category)
    
    # Apply search filter if provided
    if search_term:
        # Filter by Product, Vendor, or Organization containing the search term
        query = query.join(Organization).filter(
            db.or_(
                Expense.Product.ilike(f'%{search_term}%'),
                Expense.Vendor.ilike(f'%{search_term}%'),
                Organization.Name.ilike(f'%{search_term}%')
            )
        )
    
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
                          search_term=search_term,
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
        LicensedUsersUrl='',
        EmployeeName='',
        EmployeeAnnualSalary=0.0,
        EmployeeAnnualBonus=0.0,
        EmployeeAnnualBenefits=0.0,
        TripName='',
        TripNumberOfPassengers=0,
        TrainingName='',
        TrainingNumberOfTrainees=0,
        WithBreakdown=False,
        ApprovedJan=0.0,
        ApprovedFeb=0.0,
        ApprovedMar=0.0,
        ApprovedApr=0.0,
        ApprovedMay=0.0,
        ApprovedJun=0.0,
        ApprovedJul=0.0,
        ApprovedAug=0.0,
        ApprovedSep=0.0,
        ApprovedOct=0.0,
        ApprovedNov=0.0,
        ApprovedDec=0.0,
        ActualJan=0.0,
        ActualFeb=0.0,
        ActualMar=0.0,
        ActualApr=0.0,
        ActualMay=0.0,
        ActualJun=0.0,
        ActualJul=0.0,
        ActualAug=0.0,
        ActualSep=0.0,
        ActualOct=0.0,
        ActualNov=0.0,
        ActualDec=0.0
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
        
        # Basic fields
        expense.Sunset = 'sunset' in request.form
        expense.SunsetPlan = request.form.get('sunset_plan')
        expense.Notes = request.form.get('notes')
        expense.ProcurementUrl = request.form.get('procurement_url')
        expense.LicensedUsersUrl = request.form.get('licensed_users_url')
        expense.EmployeeName = request.form.get('employee_name')
        
        # Handle Renewal date field
        if request.form.get('renewal'):
            try:
                expense.Renewal = datetime.datetime.strptime(
                    request.form.get('renewal'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Handle WithBreakdown field and monthly values
        expense.WithBreakdown = True if request.form.get('with_breakdown') else False
        
        if expense.WithBreakdown:
            # Handle monthly approved values
            expense.ApprovedJan = float(request.form.get('approved_jan') or 0)
            expense.ApprovedFeb = float(request.form.get('approved_feb') or 0)
            expense.ApprovedMar = float(request.form.get('approved_mar') or 0)
            expense.ApprovedApr = float(request.form.get('approved_apr') or 0)
            expense.ApprovedMay = float(request.form.get('approved_may') or 0)
            expense.ApprovedJun = float(request.form.get('approved_jun') or 0)
            expense.ApprovedJul = float(request.form.get('approved_jul') or 0)
            expense.ApprovedAug = float(request.form.get('approved_aug') or 0)
            expense.ApprovedSep = float(request.form.get('approved_sep') or 0)
            expense.ApprovedOct = float(request.form.get('approved_oct') or 0)
            expense.ApprovedNov = float(request.form.get('approved_nov') or 0)
            expense.ApprovedDec = float(request.form.get('approved_dec') or 0)
            
            # Handle monthly actual values
            expense.ActualJan = float(request.form.get('actual_jan') or 0)
            expense.ActualFeb = float(request.form.get('actual_feb') or 0)
            expense.ActualMar = float(request.form.get('actual_mar') or 0)
            expense.ActualApr = float(request.form.get('actual_apr') or 0)
            expense.ActualMay = float(request.form.get('actual_may') or 0)
            expense.ActualJun = float(request.form.get('actual_jun') or 0)
            expense.ActualJul = float(request.form.get('actual_jul') or 0)
            expense.ActualAug = float(request.form.get('actual_aug') or 0)
            expense.ActualSep = float(request.form.get('actual_sep') or 0)
            expense.ActualOct = float(request.form.get('actual_oct') or 0)
            expense.ActualNov = float(request.form.get('actual_nov') or 0)
            expense.ActualDec = float(request.form.get('actual_dec') or 0)
            
            # Calculate total approved value from monthly values
            expense.ApprovedValue = (
                expense.ApprovedJan + expense.ApprovedFeb + expense.ApprovedMar + 
                expense.ApprovedApr + expense.ApprovedMay + expense.ApprovedJun + 
                expense.ApprovedJul + expense.ApprovedAug + expense.ApprovedSep + 
                expense.ApprovedOct + expense.ApprovedNov + expense.ApprovedDec
            )
            
            # Calculate total contracted value from monthly actual values
            expense.ContractedValue = (
                expense.ActualJan + expense.ActualFeb + expense.ActualMar + 
                expense.ActualApr + expense.ActualMay + expense.ActualJun + 
                expense.ActualJul + expense.ActualAug + expense.ActualSep + 
                expense.ActualOct + expense.ActualNov + expense.ActualDec
            )
        else:
            # If not using monthly breakdown, get values directly from form
            expense.ApprovedValue = float(request.form.get('approved_value') or 0)
            expense.ContractedValue = float(request.form.get('contracted_value') or 0)
            
            # Clear monthly values
            expense.ApprovedJan = 0
            expense.ApprovedFeb = 0
            expense.ApprovedMar = 0
            expense.ApprovedApr = 0
            expense.ApprovedMay = 0
            expense.ApprovedJun = 0
            expense.ApprovedJul = 0
            expense.ApprovedAug = 0
            expense.ApprovedSep = 0
            expense.ApprovedOct = 0
            expense.ApprovedNov = 0
            expense.ApprovedDec = 0
            
            expense.ActualJan = 0
            expense.ActualFeb = 0
            expense.ActualMar = 0
            expense.ActualApr = 0
            expense.ActualMay = 0
            expense.ActualJun = 0
            expense.ActualJul = 0
            expense.ActualAug = 0
            expense.ActualSep = 0
            expense.ActualOct = 0
            expense.ActualNov = 0
            expense.ActualDec = 0
        
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
        
        # Log the creation of the expense
        log_create(expense)
        
        # Commit the transaction to save the expense and audit logs
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
        # Capture old values BEFORE making any changes
        old_values = {}
        for column in expense.__table__.columns.keys():
            old_values[column] = getattr(expense, column)
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
        
        # Basic fields
        expense.Sunset = 'sunset' in request.form
        expense.SunsetPlan = request.form.get('sunset_plan')
        expense.Notes = request.form.get('notes')
        expense.ProcurementUrl = request.form.get('procurement_url')
        expense.LicensedUsersUrl = request.form.get('licensed_users_url')
        expense.EmployeeName = request.form.get('employee_name')
        
        # Handle Renewal date field
        if request.form.get('renewal'):
            try:
                expense.Renewal = datetime.datetime.strptime(
                    request.form.get('renewal'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Handle WithBreakdown field and monthly values
        expense.WithBreakdown = True if request.form.get('with_breakdown') else False
        
        if expense.WithBreakdown:
            # Handle monthly approved values
            expense.ApprovedJan = float(request.form.get('approved_jan') or 0)
            expense.ApprovedFeb = float(request.form.get('approved_feb') or 0)
            expense.ApprovedMar = float(request.form.get('approved_mar') or 0)
            expense.ApprovedApr = float(request.form.get('approved_apr') or 0)
            expense.ApprovedMay = float(request.form.get('approved_may') or 0)
            expense.ApprovedJun = float(request.form.get('approved_jun') or 0)
            expense.ApprovedJul = float(request.form.get('approved_jul') or 0)
            expense.ApprovedAug = float(request.form.get('approved_aug') or 0)
            expense.ApprovedSep = float(request.form.get('approved_sep') or 0)
            expense.ApprovedOct = float(request.form.get('approved_oct') or 0)
            expense.ApprovedNov = float(request.form.get('approved_nov') or 0)
            expense.ApprovedDec = float(request.form.get('approved_dec') or 0)
            
            # Handle monthly actual values
            expense.ActualJan = float(request.form.get('actual_jan') or 0)
            expense.ActualFeb = float(request.form.get('actual_feb') or 0)
            expense.ActualMar = float(request.form.get('actual_mar') or 0)
            expense.ActualApr = float(request.form.get('actual_apr') or 0)
            expense.ActualMay = float(request.form.get('actual_may') or 0)
            expense.ActualJun = float(request.form.get('actual_jun') or 0)
            expense.ActualJul = float(request.form.get('actual_jul') or 0)
            expense.ActualAug = float(request.form.get('actual_aug') or 0)
            expense.ActualSep = float(request.form.get('actual_sep') or 0)
            expense.ActualOct = float(request.form.get('actual_oct') or 0)
            expense.ActualNov = float(request.form.get('actual_nov') or 0)
            expense.ActualDec = float(request.form.get('actual_dec') or 0)
            
            # Calculate total approved value from monthly values
            expense.ApprovedValue = (
                expense.ApprovedJan + expense.ApprovedFeb + expense.ApprovedMar + 
                expense.ApprovedApr + expense.ApprovedMay + expense.ApprovedJun + 
                expense.ApprovedJul + expense.ApprovedAug + expense.ApprovedSep + 
                expense.ApprovedOct + expense.ApprovedNov + expense.ApprovedDec
            )
            
            # Calculate total contracted value from monthly actual values
            expense.ContractedValue = (
                expense.ActualJan + expense.ActualFeb + expense.ActualMar + 
                expense.ActualApr + expense.ActualMay + expense.ActualJun + 
                expense.ActualJul + expense.ActualAug + expense.ActualSep + 
                expense.ActualOct + expense.ActualNov + expense.ActualDec
            )
        else:
            # If not using monthly breakdown, get values directly from form
            expense.ApprovedValue = float(request.form.get('approved_value') or 0)
            expense.ContractedValue = float(request.form.get('contracted_value') or 0)
            
            # Clear monthly values
            expense.ApprovedJan = 0
            expense.ApprovedFeb = 0
            expense.ApprovedMar = 0
            expense.ApprovedApr = 0
            expense.ApprovedMay = 0
            expense.ApprovedJun = 0
            expense.ApprovedJul = 0
            expense.ApprovedAug = 0
            expense.ApprovedSep = 0
            expense.ApprovedOct = 0
            expense.ApprovedNov = 0
            expense.ApprovedDec = 0
            
            expense.ActualJan = 0
            expense.ActualFeb = 0
            expense.ActualMar = 0
            expense.ActualApr = 0
            expense.ActualMay = 0
            expense.ActualJun = 0
            expense.ActualJul = 0
            expense.ActualAug = 0
            expense.ActualSep = 0
            expense.ActualOct = 0
            expense.ActualNov = 0
            expense.ActualDec = 0
        
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
        
        # Get the new values after all changes have been made
        new_values = {}
        for column in expense.__table__.columns.keys():
            new_values[column] = getattr(expense, column)
            
        log_changes('Expense', expense.ExpenseId, old_values, new_values)
        
        # Commit the transaction to save the expense changes and audit logs
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
    
    # Log the deletion before deleting the expense
    log_delete(expense)
    
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

@app.route('/audit-logs')
def audit_logs():
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    # Get filter parameters
    selected_table = request.args.get('table', 'all')
    selected_record_id = request.args.get('record_id', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Start with base query
    query = AuditLog.query
    
    # Apply filters if selected
    if selected_table and selected_table != 'all':
        query = query.filter_by(TableName=selected_table)
    
    if selected_record_id:
        query = query.filter_by(RecordId=int(selected_record_id))
    
    if date_from:
        try:
            from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.Timestamp >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire day
            to_date = to_date + datetime.timedelta(days=1)
            query = query.filter(AuditLog.Timestamp < to_date)
        except ValueError:
            pass
    
    # Order by timestamp descending (newest first)
    query = query.order_by(AuditLog.Timestamp.desc())
    
    # Execute query
    audit_logs = query.all()
    
    # Get list of unique table names for the filter dropdown
    tables = db.session.query(AuditLog.TableName).distinct().all()
    tables = [table[0] for table in tables]  # Extract table names from result tuples
    
    return render_template('audit_logs.html',
                          audit_logs=audit_logs,
                          tables=tables,
                          selected_table=selected_table,
                          selected_record_id=selected_record_id,
                          date_from=date_from,
                          date_to=date_to,
                          current_year=current_year)

@app.route('/renewals')
def renewals():
    # Get all expenses with Renewal date assigned, sorted by Renewal date
    expenses = Expense.query.filter(Expense.Renewal.isnot(None)).order_by(Expense.Renewal).all()
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    return render_template('renewals.html', 
                          expenses=expenses,
                          current_year=current_year)

@app.route('/budget_treemap')
def budget_treemap():
    # Get the selected organization from the query parameters
    selected_organization = request.args.get('organization', 'all')
    
    # Get all organizations for the filter dropdown
    organizations = Organization.query.all()
    
    # Get all expenses
    if selected_organization == 'all':
        expenses = Expense.query.all()
    else:
        expenses = Expense.query.filter_by(OrganizationId=selected_organization).all()
    
    # Get all categories and groups for the 2D treemap
    categories = Category.query.all()
    groups = Groups.query.all()
    
    # Prepare data for the treemap
    treemap_data = []
    expense_ids = set()  # Track expense IDs to ensure uniqueness
    
    for expense in expenses:
        # Make sure all required fields have values
        if not expense.Product or not expense.category or not expense.group:
            print(f"Skipping expense with missing data: {expense.ExpenseId}")
            continue
            
        # Skip duplicates
        if expense.ExpenseId in expense_ids:
            print(f"Skipping duplicate expense: {expense.ExpenseId}")
            continue
            
        expense_ids.add(expense.ExpenseId)
        
        treemap_data.append({
            'id': expense.ExpenseId,  # Add ID for uniqueness
            'product': expense.Product,
            'vendor': expense.Vendor,
            'organization': expense.organization.Name,
            'group': expense.group.Name,
            'category': expense.category.Name,
            'group_id': expense.GroupId,
            'category_id': expense.CategoryId,
            'approved_value': int(expense.ApprovedValue) if expense.ApprovedValue else 0,
            'approved_value_formatted': format_number(int(expense.ApprovedValue) if expense.ApprovedValue else 0)
        })
    
    # Debug: Print the number of expenses and data points
    print(f"Number of expenses: {len(expenses)}")
    print(f"Number of treemap data points: {len(treemap_data)}")
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    return render_template('treemap.html',
                          treemap_data=treemap_data,
                          organizations=organizations,
                          categories=categories,
                          groups=groups,
                          selected_organization=selected_organization,
                          current_year=current_year)

@app.route('/org_breakdown')
def org_breakdown():
    # Get the selected year from the query parameters
    selected_year = request.args.get('year', datetime.datetime.now().year)
    
    # Get all years for the filter dropdown
    years = Years.query.all()
    
    # Get all organizations
    organizations = Organization.query.all()
    
    # Prepare data for the organization breakdown
    org_data = []
    total_planned = 0
    total_actual = 0
    
    for org in organizations:
        # Get all expenses for this organization and selected year
        expenses = Expense.query.filter_by(OrganizationId=org.OrganizationId, YearId=selected_year).all()
        
        # Calculate planned budget (ApprovedValue) and actual expenses
        planned_budget = sum(expense.ApprovedValue for expense in expenses if expense.ApprovedValue)
        
        # Calculate actual expenses (sum of monthly actuals)
        actual_expenses = 0
        for expense in expenses:
            monthly_actuals = [
                expense.ActualJan or 0, expense.ActualFeb or 0, expense.ActualMar or 0,
                expense.ActualApr or 0, expense.ActualMay or 0, expense.ActualJun or 0,
                expense.ActualJul or 0, expense.ActualAug or 0, expense.ActualSep or 0,
                expense.ActualOct or 0, expense.ActualNov or 0, expense.ActualDec or 0
            ]
            actual_expenses += sum(monthly_actuals)
        
        # Add to totals
        total_planned += planned_budget
        total_actual += actual_expenses
        
        # Add organization data
        org_data.append({
            'name': org.Name,
            'planned': planned_budget,
            'actual': actual_expenses,
            'difference': planned_budget - actual_expenses,
            'planned_formatted': format_number(int(planned_budget)),
            'actual_formatted': format_number(int(actual_expenses)),
            'difference_formatted': format_number(int(planned_budget - actual_expenses))
        })
    
    # Calculate percentages of total budget
    for org in org_data:
        if total_planned > 0:
            org['percentage'] = round((org['planned'] / total_planned) * 100, 1)
        else:
            org['percentage'] = 0
    
    # Format totals
    total_planned_formatted = format_number(int(total_planned))
    total_actual_formatted = format_number(int(total_actual))
    total_difference_formatted = format_number(int(total_planned - total_actual))
    
    # Get current year for footer
    current_year = datetime.datetime.now().year
    
    return render_template('org_breakdown.html',
                          org_data=org_data,
                          years=years,
                          selected_year=selected_year,
                          total_planned=total_planned,
                          total_actual=total_actual,
                          total_difference=total_planned - total_actual,
                          total_planned_formatted=total_planned_formatted,
                          total_actual_formatted=total_actual_formatted,
                          total_difference_formatted=total_difference_formatted,
                          current_year=current_year)

@app.route('/export_csv')
def export_csv():
    # Get filter parameters
    selected_year = request.args.get('year', 'all')
    selected_organization = request.args.get('organization', 'all')
    selected_category = request.args.get('category', 'all')
    search_term = request.args.get('search', '')
    
    # Start with base query
    query = Expense.query
    
    # Apply filters if selected
    if selected_year and selected_year != 'all':
        query = query.filter_by(YearId=selected_year)
    
    if selected_organization and selected_organization != 'all':
        query = query.filter_by(OrganizationId=selected_organization)
    
    if selected_category and selected_category != 'all':
        query = query.filter_by(CategoryId=selected_category)
    
    # Apply search filter if provided
    if search_term:
        # Filter by Product, Vendor, or Organization containing the search term
        query = query.join(Organization).filter(
            db.or_(
                Expense.Product.ilike(f'%{search_term}%'),
                Expense.Vendor.ilike(f'%{search_term}%'),
                Organization.Name.ilike(f'%{search_term}%')
            )
        )
    else:
        # Join Organization to avoid errors
        query = query.join(Organization)
    
    # Execute query
    expenses = query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    
    # Determine which columns to include based on filters
    headers = []
    if selected_year == 'all':
        headers.append("Year")
    headers.extend(["Vendor", "Product"])
    if selected_category == 'all':
        headers.append("Category")
    if selected_organization == 'all':
        headers.append("Organization")
    headers.extend(["Group", "Cost Per Unit", "Units", "Approved Budget", "Contracted Value", "Sunset"])
    
    # Write headers
    writer.writerow(headers)
    
    # Format currency function
    def format_currency(value):
        if value is None or value == 0:
            return "$0"
        return f"${int(value):,}".replace(",", "'")
    
    # Write data rows
    for expense in expenses:
        row = []
        if selected_year == 'all':
            row.append(expense.year.Name)
        row.append(expense.Vendor)
        row.append(expense.Product)
        if selected_category == 'all':
            row.append(expense.category.Name)
        if selected_organization == 'all':
            row.append(expense.organization.Name)
        row.append(expense.group.Name)
        row.append(format_currency(expense.CostPerUnit))
        row.append(str(expense.NumberOfUnits))
        row.append(format_currency(expense.ApprovedValue))
        row.append(format_currency(expense.ContractedValue))
        row.append("Yes" if expense.Sunset else "No")
        writer.writerow(row)
    
    # Add totals row
    totals_row = [""] * len(headers)
    # Calculate position for "Totals:" label
    offset = 0
    if selected_year == 'all':
        offset += 1
    if selected_category == 'all':
        offset += 1
    if selected_organization == 'all':
        offset += 1
    offset += 3  # Skip Vendor, Product, Group
    totals_row[offset] = "Totals:"
    
    # Calculate totals
    total_approved = sum(expense.ApprovedValue or 0 for expense in expenses)
    total_contracted = sum(expense.ContractedValue or 0 for expense in expenses)
    
    # Set totals in the row
    totals_row[-3] = format_currency(total_approved)  # Approved Budget
    totals_row[-2] = format_currency(total_contracted)  # Contracted Value
    writer.writerow(totals_row)
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=licman_expenses.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@app.route('/export_pdf')
def export_pdf():
    # Get filter parameters
    selected_year = request.args.get('year', 'all')
    selected_organization = request.args.get('organization', 'all')
    selected_category = request.args.get('category', 'all')
    search_term = request.args.get('search', '')
    
    # Start with base query
    query = Expense.query
    
    # Apply filters if selected
    if selected_year and selected_year != 'all':
        query = query.filter_by(YearId=selected_year)
    
    if selected_organization and selected_organization != 'all':
        query = query.filter_by(OrganizationId=selected_organization)
    
    if selected_category and selected_category != 'all':
        query = query.filter_by(CategoryId=selected_category)
    
    # Apply search filter if provided
    if search_term:
        # Filter by Product, Vendor, or Organization containing the search term
        query = query.join(Organization).filter(
            db.or_(
                Expense.Product.ilike(f'%{search_term}%'),
                Expense.Vendor.ilike(f'%{search_term}%'),
                Organization.Name.ilike(f'%{search_term}%')
            )
        )
    else:
        # If no search term, still join Organization to avoid errors
        query = query.join(Organization)
    
    # Execute query
    expenses = query.all()
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Set up the PDF document with PDF/A compatibility and landscape orientation
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        title="LicMan Expenses Report",
        author="AppFire LLC",
        subject="Expenses Report",
        creator="LicMan Application",
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Get the current year for copyright
    current_year = datetime.datetime.now().year
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = TA_CENTER
    
    # Create a custom style for the footer
    footer_style = ParagraphStyle(
        'footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER
    )
    
    # Create document elements
    elements = []
    
    # Add title
    title = Paragraph("LicMan Expenses Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.5*inch))
    
    # Prepare filter information
    filter_text = f"Filters: "
    if selected_year != 'all':
        year_obj = Years.query.filter_by(YearId=selected_year).first()
        filter_text += f"Year: {year_obj.Name if year_obj else selected_year}, "
    if selected_organization != 'all':
        org_obj = Organization.query.filter_by(OrganizationId=selected_organization).first()
        filter_text += f"Organization: {org_obj.Name if org_obj else selected_organization}, "
    if selected_category != 'all':
        cat_obj = Category.query.filter_by(CategoryId=selected_category).first()
        filter_text += f"Category: {cat_obj.Name if cat_obj else selected_category}, "
    if search_term:
        filter_text += f"Search: '{search_term}'"
    
    # Add filter information
    filter_paragraph = Paragraph(filter_text, styles['Normal'])
    elements.append(filter_paragraph)
    elements.append(Spacer(1, 0.3*inch))
    
    # Determine which columns to include based on filters (excluding Category and Group)
    headers = []
    if selected_year == 'all':
        headers.append("Year")
    headers.extend(["Vendor", "Product"])
    if selected_organization == 'all':
        headers.append("Organization")
    headers.extend(["Cost Per Unit", "Units", "Approved Budget", "Contracted Value", "Sunset"])
    
    # Prepare data for the table
    data = [headers]
    
    # Format currency function
    def format_currency(value):
        if value is None:
            return "$0"
        return f"${int(value):,}".replace(",", "'")
    
    # Add expense data
    for expense in expenses:
        row = []
        if selected_year == 'all':
            row.append(expense.year.Name)
        row.append(expense.Vendor)
        row.append(expense.Product)
        if selected_organization == 'all':
            row.append(expense.organization.Name)
        row.append(format_currency(expense.CostPerUnit))
        row.append(str(expense.NumberOfUnits))
        row.append(format_currency(expense.ApprovedValue))
        row.append(format_currency(expense.ContractedValue))
        row.append("Yes" if expense.Sunset else "No")
        data.append(row)
    
    # Calculate totals
    total_approved = sum(expense.ApprovedValue or 0 for expense in expenses)
    total_contracted = sum(expense.ContractedValue or 0 for expense in expenses)
    
    # Add totals row
    totals_row = ["" for _ in range(len(headers))]
    # Set the label for totals
    offset = 0
    if selected_year == 'all':
        offset += 1
    if selected_organization == 'all':
        offset += 1
    totals_row[offset + 2] = "Totals:"
    # Set the values for totals
    totals_row[-3] = format_currency(total_approved)  # Approved Budget
    totals_row[-2] = format_currency(total_contracted)  # Contracted Value
    data.append(totals_row)
    
    # Calculate appropriate column widths based on content and available space
    # Determine available width in landscape mode (A4 height becomes width in landscape)
    available_width = landscape(A4)[0] - inch  # Subtract margins
    
    # Define column widths proportionally
    col_widths = []
    
    # Assign widths based on content type
    for i, header in enumerate(headers):
        if header in ["Year", "Units", "Sunset"]:
            # Narrow columns
            col_widths.append(0.06 * available_width)
        elif header == "Vendor":
            # Wider column for Vendor with word wrap
            col_widths.append(0.18 * available_width)
        elif header == "Product":
            # Wider column for Product with word wrap
            col_widths.append(0.22 * available_width)
        elif header == "Organization":
            # Medium-wide column for Organization
            col_widths.append(0.16 * available_width)
        elif header in ["Cost Per Unit", "Approved Budget", "Contracted Value"]:
            # Medium columns for currency
            col_widths.append(0.10 * available_width)
    
    # Create the table with specified column widths
    table = Table(data, repeatRows=1, colWidths=col_widths)
    
    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Totals row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Totals row
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (-4, 1), (-2, -1), 'RIGHT'),  # Right align numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping for all cells
        ('FONTSIZE', (0, 1), (-1, -1), 9),  # Slightly smaller font for data rows
    ])
    
    # Find column indices for Vendor and Product
    vendor_col = headers.index("Vendor")
    product_col = headers.index("Product")
    
    # Add specific styling for Vendor and Product columns with enhanced word wrapping
    # Use explicit word wrapping for Product column
    for i, row in enumerate(data[1:], 1):  # Skip header row
        # Process Product column text to ensure it wraps
        if len(row) > product_col and isinstance(row[product_col], str) and len(row[product_col]) > 20:
            # Create a paragraph with word wrapping for the Product column
            product_style = ParagraphStyle(
                'ProductStyle',
                parent=styles['Normal'],
                fontSize=9,
                leading=11,  # Line spacing
                wordWrap='CJK',  # Force aggressive word wrapping
                alignment=0  # Left aligned
            )
            row[product_col] = Paragraph(row[product_col], product_style)
        
        # Process Vendor column text to ensure it wraps
        if len(row) > vendor_col and isinstance(row[vendor_col], str) and len(row[vendor_col]) > 15:
            vendor_style = ParagraphStyle(
                'VendorStyle',
                parent=styles['Normal'],
                fontSize=9,
                leading=11,  # Line spacing
                wordWrap='CJK',  # Force aggressive word wrapping
                alignment=0  # Left aligned
            )
            row[vendor_col] = Paragraph(row[vendor_col], vendor_style)
    
    # Add general styling for these columns
    table_style.add('LEFTPADDING', (vendor_col, 1), (vendor_col, -1), 6)
    table_style.add('LEFTPADDING', (product_col, 1), (product_col, -1), 6)
    table_style.add('RIGHTPADDING', (vendor_col, 1), (vendor_col, -1), 6)
    table_style.add('RIGHTPADDING', (product_col, 1), (product_col, -1), 6)
    # Add extra vertical space for wrapped cells
    table_style.add('TOPPADDING', (product_col, 1), (product_col, -1), 4)
    table_style.add('BOTTOMPADDING', (product_col, 1), (product_col, -1), 4)
    
    # Add row striping
    for i in range(1, len(data)-1):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    # Apply special formatting for sunset rows
    for i, expense in enumerate(expenses, 1):
        if expense.Sunset:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.salmon)
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Define the footer function for PDF/A compatibility
    def footer(canvas, doc):
        canvas.saveState()
        # Draw the footer - centered in landscape mode
        footer_text = f"© {current_year} AppFire LLC. All Rights Reserved."
        p = Paragraph(footer_text, footer_style)
        # In landscape mode, doc.width is actually the height of A4 in portrait
        # and doc.height is the width of A4 in portrait
        page_width = landscape(A4)[0]  # This is the actual width in landscape
        w, h = p.wrap(page_width - inch, doc.bottomMargin)
        # Center the footer text horizontally
        x = (page_width - w) / 2
        p.drawOn(canvas, x, 0.5*inch)
        
        # Add PDF/A compatibility metadata
        canvas.setTitle("LicMan Expenses Report")
        canvas.setAuthor("AppFire LLC")
        canvas.setSubject("Expenses Report")
        canvas.setCreator("LicMan Application")
        # Add PDF/A identifier
        info = canvas._doc.info
        info.PDFAVersion = PDFString('PDF/A-1b:2005')
        # Add XMP metadata for PDF/A compliance
        canvas._doc._catalog.XMP = PDFString(
            '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>'
            '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
            '<rdf:Description rdf:about="" '
            'xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">'
            '<pdfaid:part>1</pdfaid:part>'
            '<pdfaid:conformance>B</pdfaid:conformance>'
            '</rdf:Description>'
            '</rdf:RDF>'
            '</x:xmpmeta>'
            '<?xpacket end="w"?>'
        )
        canvas.restoreState()
    
    # Build the PDF document
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    
    # Get the PDF data from the buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response with PDF data
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=licman_expenses.pdf'
    
    return response

if __name__ == '__main__':
    port = os.getenv('LICMAN_PORT')
    app.run(debug=True, port=port)
