from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import User, AgriculturalData, Report, ChatHistory
from functools import wraps
import logging

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    try:
        # Get system statistics
        stats = {
            'total_users': User.query.count(),
            'total_data_records': AgriculturalData.query.count(),
            'total_reports': Report.query.count(),
            'total_chat_messages': ChatHistory.query.count(),
            'recent_users': User.query.order_by(User.created_at.desc()).limit(5).all(),
            'counties_covered': db.session.query(User.county).distinct().count(),
            'data_sources': [source[0] for source in db.session.query(AgriculturalData.data_source).distinct().all()]
        }
        
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        logging.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading admin dashboard.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Manage users"""
    try:
        page = request.args.get('page', 1, type=int)
        users = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('admin/users.html', users=users)
    except Exception as e:
        logging.error(f"Admin users error: {str(e)}")
        flash('Error loading users.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/data')
@login_required
@admin_required
def admin_data():
    """View and manage agricultural data"""
    try:
        page = request.args.get('page', 1, type=int)
        data_records = AgriculturalData.query.order_by(
            AgriculturalData.created_at.desc()
        ).paginate(page=page, per_page=50, error_out=False)
        
        return render_template('admin/data.html', data_records=data_records)
    except Exception as e:
        logging.error(f"Admin data error: {str(e)}")
        flash('Error loading data records.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/api/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle admin status for a user"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_admin = not getattr(user, 'is_admin', False)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_admin': user.is_admin,
            'message': f"{'Granted' if user.is_admin else 'Revoked'} admin access for {user.full_name}"
        })
    except Exception as e:
        logging.error(f"Toggle admin error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update user'}), 500