from app import db
from datetime import datetime

class Customers(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_suspended = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    accounts = db.relationship('Accounts', backref='customer', lazy=True)

class AccountTypes(db.Model):
    __tablename__ = 'account_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    accounts = db.relationship('Accounts', backref='account_type', lazy=True)

class Accounts(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    account_type_id = db.Column(db.Integer, db.ForeignKey('account_types.id'), nullable=False)
    balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    is_suspended = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    transactions = db.relationship('Transactions', backref='account', lazy=True)

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    balance = db.Column(db.Numeric(18, 2), nullable=False)
