from app import create_app, db
from app.models import User, Order, Service, Payment, OrderItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Order': Order,
        'Service': Service,
        'Payment': Payment,
        'OrderItem': OrderItem
    }

if __name__ == '__main__':
    app.run()
