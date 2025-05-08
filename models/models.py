from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

db = SQLAlchemy()

class Years(db.Model):
    __tablename__ = 'Years'
    YearId = Column(String(4), primary_key=True)
    Name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='year')

    def __repr__(self):
        return f'<Year {self.Name}>'

class Accounts(db.Model):
    __tablename__ = 'Accounts'
    AccountId = Column(Integer, primary_key=True)
    Name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='account')

    def __repr__(self):
        return f'<Account {self.Name}>'

class Category(db.Model):
    __tablename__ = 'Category'
    CategoryId = Column(String(100), primary_key=True)
    Name = Column(String(100), nullable=False)
    expenses = relationship('Expense', back_populates='category')

    def __repr__(self):
        return f'<Category {self.Name}>'

class Groups(db.Model):
    __tablename__ = 'Groups'
    GroupId = Column(String(100), primary_key=True)
    Name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='group')

    def __repr__(self):
        return f'<Group {self.Name}>'

class LicenseModel(db.Model):
    __tablename__ = 'LicenseModel'
    LicenseModelId = Column(String(100), primary_key=True)
    Name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='license_model')

    def __repr__(self):
        return f'<LicenseModel {self.Name}>'

class Organization(db.Model):
    __tablename__ = 'Organization'
    OrganizationId = Column(String(100), primary_key=True)
    Name = Column(String(100), unique=True, nullable=False)
    expenses = relationship('Expense', back_populates='organization')

    def __repr__(self):
        return f'<Organization {self.Name}>'

class Expense(db.Model):
    __tablename__ = 'Expense'
    ExpenseId = Column(Integer, primary_key=True, autoincrement=True)
    YearId = Column(String(4), ForeignKey('Years.YearId'), nullable=False)
    AccountId = Column(Integer, ForeignKey('Accounts.AccountId'), nullable=False)
    OrganizationId = Column(String(100), ForeignKey('Organization.OrganizationId'), nullable=False)
    GroupId = Column(String(100), ForeignKey('Groups.GroupId'), nullable=False)
    CategoryId = Column(String(100), ForeignKey('Category.CategoryId'), nullable=False)
    Vendor = Column(String(100), nullable=False)
    Product = Column(String(100), nullable=False)
    LicenseModelId = Column(String(100), ForeignKey('LicenseModel.LicenseModelId'), nullable=False)
    CostPerUnit = Column(Float)
    Sunset = Column(Boolean, default=False, nullable=False)
    SunsetPlan = Column(String(1000))
    Notes = Column(String(1000))
    NumberOfUnits = Column(Integer)
    ApprovedValue = Column(Float, nullable=False)
    ContractedValue = Column(Float)
    ProcurementUrl = Column(String(1000))
    LicensedUsersUrl = Column(String(1000))
    EmployeeName = Column(String(100))
    EmployeeAnnualSalary = Column(Float)
    EmployeeAnnualBonus = Column(Float)
    EmployeeAnnualBenefits = Column(Float)
    EmployeeTargetStartDate = Column(Date)
    TripName = Column(String(100))
    TripNumberOfPassengers = Column(Integer)
    TrainingName = Column(String(100))
    TrainingNumberOfTrainees = Column(Integer)
    WithBreakdown = Column(Boolean, default=False, nullable=False)
    ApprovedJan = Column(Float)
    ApprovedFeb = Column(Float)
    ApprovedMar = Column(Float)
    ApprovedApr = Column(Float)
    ApprovedMay = Column(Float)
    ApprovedJun = Column(Float)
    ApprovedJul = Column(Float)
    ApprovedAug = Column(Float)
    ApprovedSep = Column(Float)
    ApprovedOct = Column(Float)
    ApprovedNov = Column(Float)
    ApprovedDec = Column(Float)
    ActualJan = Column(Float)
    ActualFeb = Column(Float)
    ActualMar = Column(Float)
    ActualApr = Column(Float)
    ActualMay = Column(Float)
    ActualJun = Column(Float)
    ActualJul = Column(Float)
    ActualAug = Column(Float)
    ActualSep = Column(Float)
    ActualOct = Column(Float)
    ActualNov = Column(Float)
    ActualDec = Column(Float)
    Renewal = Column(Date)
    
    # Relationships
    year = relationship('Years', back_populates='expenses')
    account = relationship('Accounts', back_populates='expenses')
    organization = relationship('Organization', back_populates='expenses')
    group = relationship('Groups', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')
    license_model = relationship('LicenseModel', back_populates='expenses')
    licenses = relationship('Licenses', back_populates='expense')

    def __repr__(self):
        return f'<Expense {self.Product} - {self.Vendor}>'

class Licenses(db.Model):
    __tablename__ = 'Licenses'
    LicenseId = Column(Integer, primary_key=True)
    EmployeeEmail = Column(String(256), nullable=False)
    ExpenseId = Column(Integer, ForeignKey('Expense.ExpenseId'), nullable=False)
    
    # Relationship
    expense = relationship('Expense', back_populates='licenses')

    def __repr__(self):
        return f'<License {self.EmployeeEmail}>'

class AuditLog(db.Model):
    __tablename__ = 'AuditLogs'
    AuditLogIds = Column(Integer, primary_key=True, autoincrement=True)
    Timestamp = Column(DateTime, default=datetime.datetime.now)
    TableName = Column(String(100), nullable=False)
    ColumnName = Column(String(100), nullable=False)
    OldValue = Column(String(1000), nullable=True)
    NewValue = Column(String(1000), nullable=True)
    RecordId = Column(Integer, nullable=False)
    UserId = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f'<AuditLog {self.TableName}.{self.Column}:{self.RecordId}>'
