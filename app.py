import io
import json
import os
import time
import zipfile
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash



# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_screening.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    subscription_type = db.Column(db.String(20), default='basic')  # basic, medium, premium
    subscription_status = db.Column(db.String(20), default='inactive')  # inactive, active, expired
    subscription_end_date = db.Column(db.DateTime)
    payment_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    job_postings = db.relationship('JobPosting', backref='recruiter', lazy=True)

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resumes = db.relationship('Resume', backref='job_posting', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    match_score = db.Column(db.Float)
    ai_insights = db.Column(db.Text)  # Store as JSON string
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def insights_dict(self):
        """Convert JSON string to dictionary"""
        if self.ai_insights:
            return json.loads(self.ai_insights)
        return None

    @insights_dict.setter
    def insights_dict(self, value):
        """Convert dictionary to JSON string"""
        if value:
            self.ai_insights = json.dumps(value)
        else:
            self.ai_insights = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = JobPosting.query.filter_by(user_id=current_user.id).order_by(JobPosting.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/subscription')
@login_required
def subscription():
    return render_template('subscription.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 