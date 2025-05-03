from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Order, Payment
from app import db
import requests
import paypalrestsdk
from config import Config

bp = Blueprint('payments', __name__)

# Configure PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" in production
    "client_id": Config.PAYPAL_CLIENT_ID,
    "client_secret": Config.PAYPAL_CLIENT_SECRET
})

@bp.route('/payment/<int:order_id>/process', methods=['GET', 'POST'])
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('orders.orders_list'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'mpesa':
            return initiate_mpesa_payment(order)
        elif payment_method == 'paypal':
            return initiate_paypal_payment(order)
    
    return render_template('payments/process.html', order=order)

def initiate_mpesa_payment(order):
    # M-Pesa API integration
    headers = {
        'Authorization': f'Bearer {get_mpesa_access_token()}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "BusinessShortCode": "174379",
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjMxMTI5MTIxMzI4",
        "Timestamp": "20231129121328",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(order.total_amount),
        "PartyA": "254712345678",  # Customer phone number
        "PartyB": "174379",
        "PhoneNumber": "254712345678",  # Customer phone number
        "CallBackURL": "https://your-callback-url/mpesa/callback",
        "AccountReference": f"BFL-{order.id}",
        "TransactionDesc": "Payment for laundry services"
    }
    
    response = requests.post(Config.MPESA_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='mpesa',
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('M-Pesa payment initiated. Please check your phone to complete the payment.', 'info')
        return redirect(url_for('orders.order_detail', order_id=order.id))
    
    flash('Failed to initiate M-Pesa payment. Please try again.', 'danger')
    return redirect(url_for('payments.process_payment', order_id=order.id))

def initiate_paypal_payment(order):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('payments.execute_paypal_payment', order_id=order.id, _external=True),
            "cancel_url": url_for('payments.process_payment', order_id=order.id, _external=True)
        },
        "transactions": [{
            "amount": {
                "total": str(order.total_amount),
                "currency": "USD"
            },
            "description": f"Payment for order #{order.id}"
        }]
    })
    
    if payment.create():
        # Create payment record
        db_payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='paypal',
            status='pending',
            transaction_id=payment.id
        )
        db.session.add(db_payment)
        db.session.commit()
        
        # Redirect user to PayPal
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    
    flash('Failed to initiate PayPal payment. Please try again.', 'danger')
    return redirect(url_for('payments.process_payment', order_id=order.id))

@bp.route('/payment/paypal/execute/<int:order_id>')
@login_required
def execute_paypal_payment(order_id):
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Update payment record
        db_payment = Payment.query.filter_by(transaction_id=payment_id).first()
        if db_payment:
            db_payment.status = 'completed'
            order = Order.query.get(order_id)
            order.payment_status = 'paid'
            db.session.commit()
            
            flash('Payment completed successfully!', 'success')
            return redirect(url_for('orders.order_detail', order_id=order_id))
    
    flash('Payment failed. Please try again.', 'danger')
    return redirect(url_for('payments.process_payment', order_id=order_id))

def get_mpesa_access_token():
    # Implement M-Pesa access token generation
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = (Config.MPESA_CONSUMER_KEY, Config.MPESA_CONSUMER_SECRET)
    
    try:
        response = requests.get(auth_url, auth=auth)
        return response.json()['access_token']
    except:
        return None