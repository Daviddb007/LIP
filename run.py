import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db, migrate
from app.seed import seed_database

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))


@app.cli.command('seed')
def seed_command():
    """Seed the database with initial data."""
    with app.app_context():
        db.create_all()
        seed_database()
        print('Database seeded successfully.')


@app.cli.command('init-db')
def init_db_command():
    """Initialize database tables without seeding."""
    with app.app_context():
        db.create_all()
        print('Database tables created.')


with app.app_context():
    if app.config.get('TESTING') or app.debug:
        db.create_all()
        seed_database()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13000)
