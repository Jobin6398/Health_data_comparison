import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import HealthDataForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'IloveFlask')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL', 'postgresql://neondb_owner:npg_NjOli29xpdkR@ep-rapid-smoke-adxlql80-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("Using DB:", app.config['SQLALCHEMY_DATABASE_URI'])


db = SQLAlchemy(app)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    exercise = db.Column(db.Integer, nullable=False)
    meditation = db.Column(db.Integer, nullable=False)
    sleep = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<HealthData {self.id}>'

class StandardHealthProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.Integer, nullable=False)
    meditation = db.Column(db.Integer, nullable=False)
    sleep = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<StandardHealthProfile {self.id}>'

@app.before_first_request
def create_tables():
    db.create_all()

    # Insert default standard health profile if it doesn't exist
    if not StandardHealthProfile.query.first():
        default_profile = StandardHealthProfile(
            exercise=30,
            meditation=20,
            sleep=8
        )
        db.session.add(default_profile)
        db.session.commit()

    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = HealthDataForm()
    if form.validate_on_submit():
        # Create a new health data entry
        new_data = HealthData(
            username=form.username.data,
            date=form.date.data,
            exercise = form.exercise.data,
            meditation = form.meditation.data,
            sleep = form.sleep.data
        )
        # Add the new data to the database
        db.session.add(new_data)
        db.session.commit()
        # Redirect to the dashboard
        return redirect(url_for('dashboard', username=form.username.data))
    return render_template('form.html', form=form)

@app.route('/dashboard')
def dashboard():
    # Retrieve user-specific health data from the database
     username = request.args.get('username')
     if not username:
        return "Please provide a username in the URL. Example: /dashboard?username=yourname"
     
     user_data = HealthData.query.filter_by(username=username).all()
     
     if not user_data:
         return redirect(url_for('form') + f"?username={username}")
     
       # Get standard profile from DB
     standard_profile = StandardHealthProfile.query.first()

    # Prepare data for charts
     dates = [data.date.strftime("%Y-%m-%d") for data in user_data]
     exercise_data = [data.exercise for data in user_data]
     meditation_data = [data.meditation for data in user_data]
     sleep_data = [data.sleep for data in user_data]

    # Define standard reference values for comparison
     standard_data = {
        'exercise': [standard_profile.exercise] * len(dates),
        'meditation': [standard_profile.meditation] * len(dates),
        'sleep': [standard_profile.sleep] * len(dates),
    }
     scores = []
     for e, m, s in zip(exercise_data, meditation_data, sleep_data):
        exercise_score = min(e / standard_profile.exercise, 1.0) * 100 / 3
        meditation_score = min(m / standard_profile.meditation, 1.0) * 100 / 3
        sleep_score = min(s / standard_profile.sleep, 1.0) * 100 / 3
        total_score = round(exercise_score + meditation_score + sleep_score, 2)
        scores.append(total_score)


     return render_template('dashboard.html', username=username, dates=dates, exercise_data=exercise_data, meditation_data=meditation_data, sleep_data=sleep_data,  standard_data=standard_data, scores=scores)

if __name__ == '__main__':
    app.run(debug=True)