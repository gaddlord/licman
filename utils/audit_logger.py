from models.models import db, AuditLog
from flask import request, session
import inspect
import datetime

def log_changes(table_name, record_id, old_values, new_values):
    """
    Log changes between old and new values of a record.
    
    Args:
        table_name (str): Name of the table being modified
        record_id (int): Primary key of the record being modified
        old_values (dict): Dictionary of old values (attribute_name: value)
        new_values (dict): Dictionary of new values (attribute_name: value)
    """
    # Get current user ID from session if available
    user_id = session.get('user_id', None)
    
    # Compare old and new values to identify changes
    for column, new_value in new_values.items():
        old_value = old_values.get(column)
        
        # Skip if values are the same or if the column shouldn't be tracked
        if old_value == new_value or column in ['_sa_instance_state']:
            continue
        
        # Convert values to strings for storage
        old_value_str = str(old_value) if old_value is not None else None
        new_value_str = str(new_value) if new_value is not None else None
        
        # Create audit log entry
        audit_log = AuditLog(
            ColumnName=column,
            OldValue=old_value_str,
            NewValue=new_value_str,
            Timestamp=datetime.datetime.now(),
            TableName=table_name,
            RecordId=record_id,
            UserId=user_id
        )
        
        # Add to session
        db.session.add(audit_log)
    
    # Note: We don't commit here as it should be part of the same transaction
    # as the actual data change

def log_create(model_instance):
    """
    Log the creation of a new record.
    
    Args:
        model_instance: The SQLAlchemy model instance that was created
    """
    # Get table name and record ID
    table_name = model_instance.__tablename__
    
    # Get primary key value - using __table__ instead of inspect
    table = model_instance.__table__
    primary_key = list(table.primary_key.columns)[0].name
    record_id = getattr(model_instance, primary_key)
    
    # Get all attributes as new values
    new_values = model_instance.__dict__.copy()
    
    # Log each attribute as a creation
    for column, value in new_values.items():
        # Skip internal SQLAlchemy attributes and primary keys
        if column.startswith('_') or column == primary_key:
            continue
            
        # Convert value to string for storage
        value_str = str(value) if value is not None else None
        
        # Create audit log entry
        audit_log = AuditLog(
            ColumnName=column,
            OldValue=None,
            NewValue=value_str,
            Timestamp=datetime.datetime.now(),
            TableName=table_name,
            RecordId=record_id,
            UserId=session.get('user_id', None)
        )
        
        # Add to session
        db.session.add(audit_log)
    
    # Note: We don't commit here as it should be part of the same transaction

def log_delete(model_instance):
    """
    Log the deletion of a record.
    
    Args:
        model_instance: The SQLAlchemy model instance that was deleted
    """
    # Get table name and record ID
    table_name = model_instance.__tablename__
    
    # Get primary key value - using __table__ instead of inspect
    table = model_instance.__table__
    primary_key = list(table.primary_key.columns)[0].name
    record_id = getattr(model_instance, primary_key)
    
    # Get all attributes as old values
    old_values = model_instance.__dict__.copy()
    
    # Log each attribute as a deletion
    for column, value in old_values.items():
        # Skip internal SQLAlchemy attributes and primary keys
        if column.startswith('_') or column == primary_key:
            continue
            
        # Convert value to string for storage
        value_str = str(value) if value is not None else None
        
        # Create audit log entry
        audit_log = AuditLog(
            ColumnName=column,
            OldValue=value_str,
            NewValue=None,
            Timestamp=datetime.datetime.now(),
            TableName=table_name,
            RecordId=record_id,
            UserId=session.get('user_id', None)
        )
        
        # Add to session
        db.session.add(audit_log)
    
    # Note: We don't commit here as it should be part of the same transaction
