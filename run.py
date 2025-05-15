from app import create_app, db
from app.models import User, Order, Service, Payment, OrderItem

app = create_app()
with app.app_context():
    # Create all tables
    db.create_all()
    # Optionally seed with initial data
    if Service.query.count() == 0:
        services = [
            Service(
                name="Basic Service",
                description="A simple starter service",
                price=99.99,
                image_url="/static/images/service1.jpg"
            ),
            Service(
                name="Premium Service",
                description="Our most popular comprehensive service",
                price=199.99,
                image_url="/static/images/service2.jpg"
            ),
            Service(
                name="Ultimate Service",
                description="The complete package with all features",
                price=299.99,
                image_url="/static/images/service3.jpg"
            )
        ]
        db.session.add_all(services)
        db.session.commit()

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
