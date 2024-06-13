from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

from models import Customers, Accounts, Transactions, AccountTypes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Customers.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid credentials','error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        existing_user = Customers.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered','error')
            return redirect(url_for('register'))

        new_customer = Customers(full_name=full_name, email=email, address=address, password_hash=password_hash)
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Registration successful! Please login.','success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/customer_dashboard')
def customer_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    customer = Customers.query.get(user_id)
    accounts = Accounts.query.filter_by(customer_id=user_id).all()
    transactions = db.session.query(Transactions).join(Accounts, Transactions.account_id == Accounts.id).filter(Accounts.customer_id == user_id).all()
    return render_template('customer_dashboard.html', customer=customer, accounts=accounts, transactions=transactions)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    #customers = Customers.query.filter(Customers.is_suspended != 1, Customers.is_closed != 1).all()
    customers = Customers.query.filter(Customers.is_admin == 0, Customers.is_suspended != 1, Customers.is_closed != 1, Customers.is_suspended != 1).all()
    return render_template('admin_dashboard.html', customers=customers)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        customer_email = request.form['email']
        account_number = request.form['account_number']
        account_type_id = request.form['account_type']
        initial_deposit = float(request.form['initial_deposit'])
        
        customer = Customers.query.filter_by(email=customer_email).first()
        if not customer:
            flash('Customer does not exist. Please register the customer first.','error')
            return redirect(url_for('create_account'))

        ac_number_exists = Accounts.query.filter_by(account_number=account_number).first()
        if ac_number_exists:
            flash('That account number is already in use by another customer. Please use a different account number.','error')
            return redirect(url_for('admin_dashboard'))
        
        new_account = Accounts(customer_id=customer.id, account_number=account_number, account_type_id=account_type_id, balance=initial_deposit)
        db.session.add(new_account)
        db.session.commit()  # Commit to get the new account ID
        
        initial_transaction = Transactions(account_id=new_account.id, transaction_type='Deposit', amount=initial_deposit, balance=initial_deposit)
        db.session.add(initial_transaction)
        db.session.commit()
        
        flash('Account created successfully.','success')
        return redirect(url_for('admin_dashboard'))
    
    account_types = AccountTypes.query.all()
    email = request.args.get('email', '')
    customer = Customers.query.filter_by(email=email).first() if email else None
    return render_template('create_account.html', account_types=account_types, email=email, customer=customer)

@app.route('/view_account/<int:customer_id>')
def view_account(customer_id):
    customer = Customers.query.get(customer_id)
    account = Accounts.query.filter_by(customer_id=customer_id, is_suspended=0, is_closed=0).first()
    transactions = Transactions.query.filter_by(account_id=account.id).all()
    return render_template('customer_transactions.html', customer=customer, account=account, transactions=transactions)

@app.route('/suspend_account/<int:customer_id>')
def suspend_account(customer_id):
    account = Accounts.query.filter_by(customer_id=customer_id, is_suspended=0, is_closed=0).first()
    if account:
        account.is_suspended = 1
        db.session.commit()
        flash('Customer account is suspended.','success')
    return redirect(url_for('admin_dashboard'))


@app.route('/suspend_customer/<int:customer_id>')
def suspend_customer(customer_id):
    customer = Customers.query.get(customer_id)
    customer.is_suspended = 1
    db.session.commit()
    flash('Customer is suspended.','success')    
    return redirect(url_for('admin_dashboard'))


@app.route('/close_account/<int:customer_id>')
def close_account(customer_id):
    account = Accounts.query.filter_by(customer_id=customer_id, is_suspended=0, is_closed=0).first()
    if account:
        account.is_closed = 1
        db.session.commit()
        flash('Customer account is closed.')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
