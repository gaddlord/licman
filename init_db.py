from app import app, db
from models.models import Years, Accounts, Category, Groups, LicenseModel, Organization, Expense
import datetime

def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Add sample years
        years = [
            Years(YearId='2024', Name='2024'),
            Years(YearId='2025', Name='2025'),
            Years(YearId='2026', Name='2026'),
            Years(YearId='2027', Name='2027'),
        ]
        db.session.add_all(years)
        
        # Add sample accounts
        accounts = [
            Accounts(AccountId=6103, Name="Staff Training"),
            Accounts(AccountId=6207, Name="Charitable Contributions"),
            Accounts(AccountId=6502, Name='Peripherals and Accessories'),
            Accounts(AccountId=6503, Name='Software Expense'),
            Accounts(AccountId=6504, Name='Cloud Services'),
            Accounts(AccountId=6605, Name='Consulting Fees'),
        ]
        db.session.add_all(accounts)
        
        # Add sample categories
        categories = [
            Category(CategoryId='SW', Name='Software'),
            Category(CategoryId='HW', Name='Hardware'),
            Category(CategoryId='INF', Name='Infrastructure'),
            Category(CategoryId='TE', Name='Travel'),
            Category(CategoryId='TR', Name='Training'),
            Category(CategoryId='FTE', Name='Full Time Employee'),
            Category(CategoryId='AWF', Name='Contractor'),
        ]
        db.session.add_all(categories)
        
        # Add sample groups
        groups = [
            Groups(GroupId='COS', Name='Cost of Sales'),
            Groups(GroupId='G&A', Name='General and Administrative'),
        ]
        db.session.add_all(groups)
        
        # Add sample license models
        license_models = [
            LicenseModel(LicenseModelId='FA', Name='Fixed Amount'),
            LicenseModel(LicenseModelId='AS', Name='Annual Subscription'),
            LicenseModel(LicenseModelId='MS', Name='Monthly Subscription'),
            LicenseModel(LicenseModelId='PG', Name='Pay-as-you-go'),
            LicenseModel(LicenseModelId='M', Name='Build Minutes'),
            LicenseModel(LicenseModelId='C', Name='Credits'),
            LicenseModel(LicenseModelId='GB', Name='GB Traffic'),
            LicenseModel(LicenseModelId='US', Name='User Subscription'),
            LicenseModel(LicenseModelId='LC', Name='Lines of Code'),
            LicenseModel(LicenseModelId='A', Name='Number of Agents'),
        ]
        db.session.add_all(license_models)
        
        # Add sample organizations
        organizations = [
            Organization(OrganizationId='ENG', Name='Engineering'),
            Organization(OrganizationId='DVO', Name='DevOps'),
            Organization(OrganizationId='ITO', Name='IT Operations')
        ]
        db.session.add_all(organizations)
        
        # Commit the reference data
        db.session.commit()
        
        # Add sample expenses
        expenses = [
            Expense(
                YearId='2025',
                AccountId=6504,
                OrganizationId='ITO',
                GroupId='COS',
                CategoryId='INF',
                Vendor='Amazon Web Services',
                Product='AWS',
                LicenseModelId='PG',
                CostPerUnit=1200.00,
                NumberOfUnits=0,
                ApprovedValue=12000.00,
                ContractedValue=12000.00,
                Sunset=True,
                SunsetPlan='Moving to new cloud provider in Q3',
                Notes='No EDP plan yet. It will cost us around $400K to get such.',
            ),
        ]
        db.session.add_all(expenses)
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
