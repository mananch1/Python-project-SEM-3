from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atm_database.db'  
app.config['SECRET_KEY'] = 'your_secret_key' 
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    vid = db.Column(db.String(10), unique=True, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    recipient_vid = db.Column(db.String(10), nullable=True)  # New field for recipient VID

# Database tables
with app.app_context():
    db.create_all()

# Route for the welcome page
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html')

# Route for the registration page
def generate_vid(length=10):
    """Generate a random unique VID."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Generate a unique VID
        vid = generate_vid()
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, vid=vid, balance=0.0)

        db.session.add(new_user)
        db.session.commit()
        
        # Flash message for successful registration
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', username=user.username, balance=user.balance, vid=user.vid)
    flash('You need to log in first.', 'warning')
    return redirect(url_for('login'))

# Route for the withdraw page
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        
        if user.balance >= amount:
            user.balance -= amount
            transaction = Transaction(user_id=user.id, amount=-amount, description='Withdrawal')
            db.session.add(transaction)
            db.session.commit()
            flash('Withdrawal successful!', 'success')  # Success message
            return redirect(url_for('dashboard'))  # Redirect to dashboard after success
        else:
            flash('Insufficient balance! Please check your account balance and try again.', 'danger')  # Error message
            return render_template('withdraw.html')  # Render the withdrawal page again on error
    
    return render_template('withdraw.html')


# Route for the deposit page
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Please enter a valid amount.', 'danger')
                return render_template('deposit.html')

            user = User.query.get(user_id)
            user.balance += amount
            transaction = Transaction(user_id=user.id, amount=amount, description='Deposit')
            db.session.add(transaction)
            db.session.commit()
            flash('Deposit successful!', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('Invalid amount. Please enter a number.', 'danger')
            return render_template('deposit.html')

    return render_template('deposit.html')


# Route for the transfer page
# Route for the transfer page
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    user_id = session.get('user_id')
    if request.method == 'POST':
        recipient_vid = request.form['vid']
        amount = float(request.form['amount'])
        pin = request.form['pin']  # Implement PIN validation if necessary
        user = User.query.get(user_id)
        recipient = User.query.filter_by(vid=recipient_vid).first()
        
        if recipient and user.balance >= amount:
            # Deduct from the sender's balance
            user.balance -= amount
            # Add to the recipient's balance
            recipient.balance += amount
            
            # Create a transaction record for the sender
            transaction_sender = Transaction(user_id=user.id, amount=-amount, description=f'Transfer to {recipient_vid}')
            # Create a transaction record for the recipient
            transaction_recipient = Transaction(user_id=recipient.id, amount=amount, description=f'Transfer from {user.vid}')
            
            # Add both transactions to the session
            db.session.add(transaction_sender)
            db.session.add(transaction_recipient)
            
            db.session.commit()  # Commit the transaction records
            flash('Transfer successful!', 'success')
        else:
            flash('Transfer failed. Check recipient Vid or insufficient balance.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('transfer.html')


# Route for the transaction history page
@app.route('/transaction_history')
def transaction_history():
    user_id = session.get('user_id')
    transactions = Transaction.query.filter_by(user_id=user_id).all()  # Fetch transactions for the logged-in user
    return render_template('transaction_history.html', transactions=transactions)


# Route for password recovery page
@app.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        username = request.form['username']
        # Implement password recovery logic here
        flash('Password recovery instructions have been sent to your email.', 'success')
        return redirect(url_for('login'))
    return render_template('password_recovery.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)
