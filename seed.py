from app import db
from app import HealthData
from datetime import datetime, timedelta
import random

# Clear the database
db.drop_all()
db.create_all()

# Generate dummy data for the past 3 months
start_date = datetime.now() - timedelta(days=90)
for i in range(90):
    date = start_date + timedelta(days=i)
    exercise = random.randint(0, 120)  # Exercise in minutes
    meditation = random.randint(0, 60)  # Meditation in minutes
    sleep = random.uniform(4, 10)  # Sleep in hours
    data = HealthData(date=date, exercise=exercise, meditation=meditation, sleep=sleep)
    db.session.add(data)

db.session.commit()
print("Database seeded with dummy data.")