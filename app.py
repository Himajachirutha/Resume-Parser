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

from utils.resume_processor import ResumeProcessor

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

# Initialize ResumeProcessor
resume_processor = ResumeProcessor(os.environ.get('MISTRAL_API_KEY'))

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

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False)
    payment_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('payments', lazy=True))

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

@app.route('/payment/<subscription_type>', methods=['GET', 'POST'])
@login_required
def payment(subscription_type):
    if subscription_type not in ['basic', 'medium', 'premium']:
        flash('Invalid subscription type', 'error')
        return redirect(url_for('subscription'))
    
    prices = {
        'basic': 29.99,
        'medium': 49.99,
        'premium': 99.99
    }
    
    if request.method == 'POST':
        try:
            # In a real application, you would validate the payment details here
            # and process the payment through a payment gateway
            
            # Create a payment record
            payment = Payment(
                user_id=current_user.id,
                amount=prices[subscription_type],
                subscription_type=subscription_type,
                payment_id=f"PAY-{int(time.time())}",  # Generate a unique payment ID
                status='completed'
            )
            db.session.add(payment)
            
            # Update user's subscription status
            current_user.subscription_type = subscription_type
            current_user.subscription_status = 'active'
            current_user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
            current_user.payment_id = payment.payment_id
            current_user.payment_status = 'completed'
            
            db.session.commit()
            
            flash('Payment successful! Your subscription is now active.', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing payment: {str(e)}', 'error')
            return redirect(url_for('subscription'))
    
    return render_template('payment.html', 
                         subscription_type=subscription_type,
                         price=prices[subscription_type])

@app.route('/create_job', methods=['GET', 'POST'])
@login_required
def create_job():
    if current_user.subscription_status != 'active':
        flash('Please subscribe to create job postings.', 'warning')
        return redirect(url_for('subscription'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills', '')  # Get required skills from form
        experience = request.form.get('experience')
        industry = request.form.get('industry')
        
        if not all([title, description, required_skills, experience, industry]):
            flash('All fields are required.', 'error')
            return redirect(url_for('create_job'))
            
        job = JobPosting(
            title=title,
            description=description,
            required_skills=required_skills,  # Add required skills to job posting
            experience=experience,
            industry=industry,
            user_id=current_user.id
        )
        
        try:
            db.session.add(job)
            db.session.commit()
            flash('Job posting created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating job posting: {str(e)}', 'error')
            return redirect(url_for('create_job'))
            
    return render_template('create_job.html')

@app.route('/upload_resumes/<int:job_id>', methods=['POST'])
@login_required
def upload_resumes(job_id):
    if current_user.subscription_status != 'active':
        flash('Please subscribe to upload resumes.', 'error')
        return redirect(url_for('subscription'))
        
    job = JobPosting.query.get_or_404(job_id)
    
    if job.user_id != current_user.id:
        flash('You do not have permission to upload resumes for this job.', 'error')
        return redirect(url_for('dashboard'))
        
    if 'resumes' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
        
    file = request.files['resumes']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
        
    if not file.filename.endswith('.zip'):
        flash('Please upload a ZIP file', 'error')
        return redirect(url_for('dashboard'))
        
    try:
        # Get resume limit based on subscription
        resume_limit = {
            'basic': 10,
            'medium': 25,
            'premium': float('inf')
        }.get(current_user.subscription_type, 10)
        
        # Process the ZIP file
        resumes = resume_processor.process_resumes(file, {
            'title': job.title,
            'skills': job.required_skills,
            'experience': job.experience,
            'industry': job.industry
        })
        
        # Check if adding these resumes would exceed the limit
        current_resume_count = Resume.query.filter_by(job_posting_id=job_id).count()
        if current_resume_count + len(resumes) > resume_limit:
            flash(f'Uploading these resumes would exceed your plan limit of {resume_limit} resumes per job.', 'error')
            return redirect(url_for('dashboard'))
            
        # Save the resumes
        for resume in resumes:
            db_resume = Resume(
                job_posting_id=job_id,
                filename=resume['filename'],
                file_path=resume['file_path'],
                match_score=resume['match_score'],
                ai_insights=json.dumps(resume['ai_insights'])
            )
            db.session.add(db_resume)
            
        db.session.commit()
        flash(f'Successfully processed {len(resumes)} resumes!', 'success')
        
    except Exception as e:
        flash(f'Error processing resumes: {str(e)}', 'error')
        
    return redirect(url_for('dashboard'))

@app.route('/view_shortlist/<int:job_id>')
@login_required
def view_shortlist(job_id):
    job = JobPosting.query.get_or_404(job_id)
    if job.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    resumes = Resume.query.filter_by(job_posting_id=job_id).order_by(Resume.match_score.desc()).all()
    return render_template('view_shortlist.html', job=job, resumes=resumes)

@app.route('/download_resume/<int:resume_id>')
@login_required
def download_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.job_posting.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(
        resume.file_path,
        as_attachment=True,
        download_name=resume.filename
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 