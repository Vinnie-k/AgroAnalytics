import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import User
import stripe
import logging

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get domain for Stripe redirects
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', '').split(',')[0] if os.environ.get('REPLIT_DOMAINS') else 'localhost:5000'

@app.route('/subscription')
@login_required
def subscription():
    """Subscription plans page"""
    plans = {
        'basic': {
            'name': 'Basic Plan',
            'price': 0,  # Free plan per month
            'features': [
                'Access to basic agricultural data',
                'AI chatbot assistance',
                'Basic crop recommendations',
                'Monthly reports'
            ],
            'stripe_price_id': 'price_basic_plan'  # Replace with actual Stripe price ID
        },
        'premium': {
            'name': 'Premium Plan', 
            'price': 2500,  # KES 2500 per month
            'features': [
                'All Basic features',
                'Advanced market insights',
                'Weather predictions',
                'Priority AI support',
                'Weekly detailed reports',
                'Export data functionality'
            ],
            'stripe_price_id': 'price_premium_plan'  # Replace with actual Stripe price ID
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price': 5000,  # KES 5000 per month
            'features': [
                'All Premium features',
                'Custom data integrations',
                'Dedicated support',
                'Advanced analytics',
                'API access',
                'Custom reports'
            ],
            'stripe_price_id': 'price_enterprise_plan'  # Replace with actual Stripe price ID
        }
    }
    
    return render_template('subscription.html', plans=plans, current_user=current_user)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        plan_type = data.get('plan_type')
        
        # Plan configurations
        price_configs = {
            'basic': 'price_1234567890_basic',  # Replace with actual Stripe price IDs
            'premium': 'price_1234567890_premium',
            'enterprise': 'price_1234567890_enterprise'
        }
        
        if plan_type not in price_configs:
            return jsonify({'error': 'Invalid plan type'}), 400
            
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[
                {
                    'price': price_configs[plan_type],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f'https://{YOUR_DOMAIN}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{YOUR_DOMAIN}/subscription/cancel',
            client_reference_id=str(current_user.id),
            metadata={
                'user_id': current_user.id,
                'plan_type': plan_type
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        logging.error(f"Stripe checkout error: {str(e)}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

@app.route('/subscription/success')
@login_required
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Update user subscription status
                current_user.subscription_status = 'active'
                current_user.subscription_plan = session.metadata.get('plan_type', 'basic')
                db.session.commit()
                
                flash('Subscription activated successfully! Welcome to Kenya-Agor Premium!', 'success')
            else:
                flash('Payment verification pending. Please contact support if issues persist.', 'warning')
                
        except Exception as e:
            logging.error(f"Subscription success error: {str(e)}")
            flash('Error verifying payment. Please contact support.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/subscription/cancel')
@login_required
def subscription_cancel():
    """Handle cancelled subscription"""
    flash('Subscription cancelled. You can subscribe anytime from your dashboard.', 'info')
    return redirect(url_for('subscription'))

@app.route('/api/subscription/status')
@login_required
def subscription_status():
    """Get current user subscription status"""
    return jsonify({
        'status': getattr(current_user, 'subscription_status', 'none'),
        'plan': getattr(current_user, 'subscription_plan', 'none'),
        'features_enabled': {
            'advanced_insights': getattr(current_user, 'subscription_status', 'none') in ['active', 'premium'],
            'export_data': getattr(current_user, 'subscription_status', 'none') == 'active',
            'priority_support': getattr(current_user, 'subscription_status', 'none') in ['active', 'premium']
        }
    })

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logging.error("Invalid payload in Stripe webhook")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        logging.error("Invalid signature in Stripe webhook")
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_invoice_payment_succeeded(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return jsonify({'status': 'success'})

def handle_checkout_session_completed(session):
    """Handle completed checkout session"""
    try:
        user_id = session.get('client_reference_id')
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_status = 'active'
                user.subscription_plan = session['metadata'].get('plan_type', 'basic')
                db.session.commit()
                logging.info(f"Activated subscription for user {user_id}")
    except Exception as e:
        logging.error(f"Error handling checkout session: {str(e)}")

def handle_invoice_payment_succeeded(invoice):
    """Handle successful invoice payment"""
    try:
        customer_id = invoice.get('customer')
        if customer_id:
            # Update subscription status
            logging.info(f"Payment succeeded for customer {customer_id}")
    except Exception as e:
        logging.error(f"Error handling invoice payment: {str(e)}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription.get('customer')
        if customer_id:
            # Find user and deactivate subscription
            logging.info(f"Subscription cancelled for customer {customer_id}")
    except Exception as e:
        logging.error(f"Error handling subscription deletion: {str(e)}")