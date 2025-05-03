from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Service
from app import db
from datetime import datetime

bp = Blueprint('orders', __name__)

@bp.route('/orders')
@login_required
def orders_list():
    if current_user.is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders/list.html', orders=orders)

@bp.route('/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        pickup_location = request.form.get('pickup_location')
        dropoff_location = request.form.get('dropoff_location')
        pickup_time = datetime.strptime(request.form.get('pickup_time'), '%Y-%m-%dT%H:%M')
        services = request.form.getlist('services[]')
        quantities = request.form.getlist('quantities[]')
        
        order = Order(
            user_id=current_user.id,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_time=pickup_time,
            status='pending'
        )
        
        total_amount = 0
        for service_id, quantity in zip(services, quantities):
            service = Service.query.get(service_id)
            if service:
                item = OrderItem(
                    service_id=service_id,
                    quantity=int(quantity),
                    price=service.price
                )
                total_amount += service.price * int(quantity)
                order.items.append(item)
        
        order.total_amount = total_amount
        db.session.add(order)
        db.session.commit()
        
        flash('Order created successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))
    
    services = Service.query.all()
    return render_template('orders/create.html', services=services)

@bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if not current_user.is_admin and order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('orders.orders_list'))
    return render_template('orders/detail.html', order=order)

@bp.route('/orders/<int:order_id>/track')
@login_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    if not current_user.is_admin and order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('orders.orders_list'))
    return render_template('orders/track.html', order=order)