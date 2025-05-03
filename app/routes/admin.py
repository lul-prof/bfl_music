from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Order, Service, Payment
from app import db
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_users = User.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_users=total_users,
                         recent_orders=recent_orders)

@bp.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status:
        order.status = status
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    return redirect(url_for('admin.orders'))

@bp.route('/services')
@login_required
@admin_required
def services():
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@bp.route('/services/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_service():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        
        service = Service(name=name, description=description, price=price)
        db.session.add(service)
        db.session.commit()
        
        flash('Service created successfully!', 'success')
        return redirect(url_for('admin.services'))
    
    return render_template('admin/create_service.html')