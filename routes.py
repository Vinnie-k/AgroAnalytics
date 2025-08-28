from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, AgriculturalData, Report, ChatHistory
from data_service import DataService
from ml_service import MLService
from chatbot_service import ChatbotService
import json
import logging

# Initialize services
data_service = DataService()
ml_service = MLService()
chatbot_service = ChatbotService()

@app.route('/')
def index():
    """Landing page showcasing Kenya-Agro system"""
    # Get sample agricultural statistics for display
    total_farmers = User.query.count()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(3).all()
    
    # Sample key metrics from available data
    sample_metrics = {
        'total_farmers': total_farmers,
        'counties_covered': db.session.query(User.county).distinct().count(),
        'reports_generated': Report.query.count(),
        'data_sources': ['KilimoSTAT', 'KNBS', 'Ministry of Agriculture']
    }
    
    return render_template('index.html', metrics=sample_metrics, recent_reports=recent_reports)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for Kenyan farmers"""
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            full_name = request.form.get('full_name', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            county = request.form.get('county', '').strip()
            sub_county = request.form.get('sub_county', '').strip()
            ward = request.form.get('ward', '').strip()
            farm_size = request.form.get('farm_size', 0)
            farm_type = request.form.get('farm_type', '').strip()
            primary_crops = request.form.getlist('primary_crops')
            farming_experience = request.form.get('farming_experience', 0)
            
            # Validation
            if not all([username, email, password, full_name, county]):
                flash('Please fill in all required fields.', 'error')
                return render_template('register.html')
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone_number=phone_number,
                county=county,
                sub_county=sub_county,
                ward=ward,
                farm_size=float(farm_size) if farm_size else 0,
                farm_type=farm_type,
                primary_crops=json.dumps(primary_crops),
                farming_experience=int(farming_experience) if farming_experience else 0,
                is_admin=False  # Default to non-admin
            )
            user.set_password(password)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    
    # Kenya counties for dropdown
    kenyan_counties = [
        'Baringo', 'Bomet', 'Bungoma', 'Busia', 'Elgeyo-Marakwet', 'Embu',
        'Garissa', 'Homa Bay', 'Isiolo', 'Kajiado', 'Kakamega', 'Kericho',
        'Kiambu', 'Kilifi', 'Kirinyaga', 'Kisii', 'Kisumu', 'Kitui',
        'Kwale', 'Laikipia', 'Lamu', 'Machakos', 'Makueni', 'Mandera',
        'Marsabit', 'Meru', 'Migori', 'Mombasa', 'Murang\'a', 'Nairobi',
        'Nakuru', 'Nandi', 'Narok', 'Nyamira', 'Nyandarua', 'Nyeri',
        'Samburu', 'Siaya', 'Taita-Taveta', 'Tana River', 'Tharaka-Nithi',
        'Trans Nzoia', 'Turkana', 'Uasin Gishu', 'Vihiga', 'Wajir', 'West Pokot'
    ]
    
    # Common Kenyan crops
    kenyan_crops = [
        'Maize', 'Beans', 'Tea', 'Coffee', 'Wheat', 'Rice', 'Sorghum',
        'Millet', 'Sweet Potatoes', 'Irish Potatoes', 'Cassava', 'Bananas',
        'Tomatoes', 'Onions', 'Cabbages', 'Kales', 'Carrots', 'Mangoes',
        'Avocados', 'Oranges', 'Pineapples', 'Passion Fruits', 'Sugarcane','Sunflowers'
    ]
    
    return render_template('register.html', counties=kenyan_counties, crops=kenyan_crops)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for farmers"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'error')
            return render_template('login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)  # Remember login for persistent sessions
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for logged-in farmers"""
    try:
        # Get user-specific agricultural data
        user_crops = json.loads(current_user.primary_crops) if current_user.primary_crops else []
        user_county = current_user.county
        
        # Get recent agricultural data for user's county and crops
        county_data = AgriculturalData.query.filter_by(county=user_county).limit(10).all()
        crop_data = AgriculturalData.query.filter(
            AgriculturalData.crop_name.in_(user_crops)
        ).limit(10).all() if user_crops else []
        
        # Get ML insights for user's farming profile
        ml_insights = ml_service.generate_farmer_insights(current_user)
        
        # Prepare dashboard data
        dashboard_data = {
            'farmer_profile': {
                'name': current_user.full_name,
                'county': current_user.county,
                'farm_size': current_user.farm_size,
                'crops': user_crops,
                'experience': current_user.farming_experience
            },
            'county_data': [
                {
                    'crop': data.crop_name,
                    'value': data.value,
                    'unit': data.unit,
                    'year': data.year
                } for data in county_data
            ],
            'crop_recommendations': ml_insights.get('crop_recommendations', []),
            'market_trends': ml_insights.get('market_trends', {}),
            'weather_insights': ml_insights.get('weather_insights', {})
        }
        
        return render_template('dashboard.html', data=dashboard_data)
        
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard data. Please try again.', 'error')
        return render_template('dashboard.html', data={})

@app.route('/reports')
@login_required
def reports():
    """Reports page showing generated agricultural reports"""
    try:
        # Get user's reports
        user_reports = Report.query.filter_by(user_id=current_user.id).order_by(
            Report.created_at.desc()
        ).all()
        
        # Generate new report if none exist
        if not user_reports:
            report_data = ml_service.generate_agricultural_report(current_user)
            if report_data:
                new_report = Report(
                    title=report_data['title'],
                    report_type=report_data['type'],
                    content=report_data['content'],
                    insights=report_data['insights'],
                    user_id=current_user.id
                )
                db.session.add(new_report)
                db.session.commit()
                user_reports = [new_report]
        
        return render_template('reports.html', reports=user_reports)
        
    except Exception as e:
        logging.error(f"Reports error: {str(e)}")
        flash('Error loading reports. Please try again.', 'error')
        return render_template('reports.html', reports=[])

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """API endpoint for AI chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get chatbot response
        response = chatbot_service.get_response(message, current_user)
        
        # Save chat history
        chat_record = ChatHistory(
            user_id=current_user.id,
            message=message,
            response=response
        )
        db.session.add(chat_record)
        db.session.commit()
        
        return jsonify({'response': response})
        
    except Exception as e:
        logging.error(f"Chatbot API error: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/update-data')
@login_required
def update_data_api():
    """API endpoint to trigger data update from external sources"""
    try:
        # Fetch latest data from KilimoSTAT and KNBS
        update_result = data_service.fetch_latest_data()
        
        if update_result['success']:
            # Get updated data for display
            latest_data = AgriculturalData.query.order_by(
                AgriculturalData.created_at.desc()
            ).limit(10).all()
            
            return jsonify({
                'success': True,
                'message': f"Updated {update_result['records_updated']} records",
                'timestamp': update_result['timestamp'].isoformat(),
                'latest_data': [
                    {
                        'crop': data.crop_name,
                        'county': data.county,
                        'value': data.value,
                        'unit': data.unit,
                        'year': data.year,
                        'source': data.data_source
                    } for data in latest_data
                ]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update data'
            }), 500
            
    except Exception as e:
        logging.error(f"Data update API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/data/view')
@login_required
def view_data_api():
    """API endpoint to view latest agricultural data"""
    try:
        page = request.args.get('page', 1, type=int)
        data_records = AgriculturalData.query.order_by(
            AgriculturalData.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': data.id,
                    'crop': data.crop_name,
                    'county': data.county,
                    'value': data.value,
                    'unit': data.unit,
                    'year': data.year,
                    'source': data.data_source,
                    'created_at': data.created_at.isoformat()
                } for data in data_records.items
            ],
            'pagination': {
                'page': data_records.page,
                'pages': data_records.pages,
                'total': data_records.total,
                'has_next': data_records.has_next,
                'has_prev': data_records.has_prev
            }
        })
    except Exception as e:
        logging.error(f"View data API error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to load data'}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('base.html'), 500
