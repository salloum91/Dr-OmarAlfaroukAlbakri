
#app.py

from collections import UserString

from click import DateTime
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
 # Assuming your Question model is defined in a file named 'models.py'
from app import db
from flask_migrate import Migrate

import requests
from flask_cors import CORS
import datetime
from datetime import datetime
from sqlalchemy import Date, DateTime 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking

db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded pictures


migrate = Migrate(app, db)


# Create the 'uploads' folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Create the 'uploads' folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class Fatawa(db.Model):
    __tablename__ = 'fatawa'

    id = db.Column(db.Integer, primary_key=True)
    numberfatwa = db.Column(db.String(50))
    onwan = db.Column(db.String(255))
    soaal = db.Column(db.Text)
    jawabe = db.Column(db.Text)
    verite = db.Column(db.Text)
    verite1 = db.Column(db.Text)
    views = db.Column(db.Integer)
    created_at = db.Column(db.String(20), default=datetime.utcnow().strftime('%d-%m-%Y'))  # Use String type to store datetime as string

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f"<Fatawa {self.onwan}>"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Question {self.id}>"
    


class AdminQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.Text, nullable=True)  # Add a column to store the admin answers
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question', backref=db.backref('admin_questions', uselist=False))
    

    def __repr__(self):
        return f"<AdminQuestion {self.id}>"



app.secret_key = 'your_secret_key'

# Add a route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password are correct (you should replace this with your actual authentication logic)
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)


@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/hijri-data', methods=['GET'])
def hijri_data():
    try:
        data = get_hijri_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def get_hijri_data():
    api_url = "https://api.aladhan.com/v1/gToH"
    response = requests.get(api_url)

    # Print the API response for debugging
    print(response.text)

    data = response.json()
    return data







@app.route('/index')
def index():
    posts = Post.query.all()
    pictures = Picture.query.all()
    return render_template('home.html', posts=posts, pictures=pictures)


# Modify the existing admin_panel route to check for login status
@app.route('/admin')
def admin_panel():
    if 'logged_in' in session and session['logged_in']:
        users = User.query.all()
        posts = Post.query.all()
        pictures = Picture.query.all()
        fatawas = Fatawa.query.all()  # Retrieve fatawas here or from wherever they are stored
        return render_template('admin_panel.html', users=users, posts=posts, pictures=pictures,fatawas= fatawas )
    else:
        return redirect(url_for('login'))


# Add a route for logging out
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin/add_post', methods=['POST'])
def add_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))

# New route to serve images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/add_picture', methods=['POST'])
def add_picture():
    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files['file']

        if file and file.filename != '':
            # Save the uploaded file to the specified folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Create a new Picture object and save it to the database with only the filename
            new_picture = Picture(title=title, url=file.filename)
            db.session.add(new_picture)
            db.session.commit()

        return redirect(url_for('index'))
    

# ... (existing code) ...

@app.route('/admin/delete_post', methods=['POST'])
def admin_delete_post():
    if request.method == 'POST':
        post_id = int(request.form.get('post_id'))
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_picture', methods=['POST'])
def admin_delete_picture():
    if request.method == 'POST':
        picture_id = int(request.form.get('picture_id'))
        picture = Picture.query.get_or_404(picture_id)
        # Delete the file from the 'uploads' folder
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], picture.url))
        db.session.delete(picture)
        db.session.commit()

    return redirect(url_for('admin_panel'))

# ... (existing code) ...

# Add this route for deleting posts from the home page
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if request.method == 'POST':
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for('index'))

# Add this route for deleting pictures from the home page
@app.route('/delete_picture/<int:picture_id>', methods=['POST'])
def delete_picture(picture_id):
    if request.method == 'POST':
        picture = Picture.query.get_or_404(picture_id)
        # Delete the file from the 'uploads' folder
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], picture.url))
        db.session.delete(picture)
        db.session.commit()

    return redirect(url_for('index'))

# Add a route to reset the database
@app.route('/reset_database', methods=['POST'])
def reset_database():
    if request.method == 'POST':
        # Drop and recreate all tables
        with app.app_context():
            db.drop_all()
            db.create_all()

        # Redirect to the admin panel after resetting the database
        return redirect(url_for('admin_panel'))


#######################
@app.route('/fatawa')
def fatawa():
    fatawas = Fatawa.query.all()
    return render_template('fatawa.html', fatawas=fatawas)
    
@app.route('/delete_fatawa/<int:fatawa_id>', methods=['POST'])
def delete_fatawa(fatawa_id):
    if request.method == 'POST':
        fatawa = Fatawa.query.get_or_404(fatawa_id)
        db.session.delete(fatawa)
        db.session.commit()

    return redirect(url_for('fatawa'))




@app.route('/admin/add_fatawa', methods=['POST'])
def add_fatawa():
    if request.method == 'POST':
        numberfatwa = request.form.get('numberfatwa')
        onwan = request.form.get('onwan')
        soaal = request.form.get('soaal')
        jawabe = request.form.get('jawabe')
        verite = request.form.get('verite')
        verite1 = request.form.get('verite1')
        views = int(request.form.get('views', 0))
        created_at = db.Column(DateTime, default=datetime.utcnow)
        new_fatawa = Fatawa(numberfatwa=numberfatwa, onwan=onwan, soaal=soaal, jawabe=jawabe, verite=verite, verite1=verite1, views=views)
        db.session.add(new_fatawa)
        db.session.commit()

    return redirect(url_for('admin_panel'))


@app.route('/fatawa/<int:fatawa_id>')
def fatawa_details(fatawa_id):
    fatawa = Fatawa.query.get_or_404(fatawa_id)
    return render_template('fatawa_details.html', fatawa=fatawa)

@app.route('/all_fatawa')
def all_fatawa():
    # Assuming you retrieve all fatawas from the database
    fatawas = Fatawa.query.all()
    return render_template('all_fatawa.html', fatawas=fatawas)
    ################################


# Routes for handling user questions
@app.route('/askme', methods=['GET', 'POST'])
def askme():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        question = request.form.get('question')

        # Create a new instance of the Question model
        new_question = Question(name=name, email=email, question=question)
        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('askme.html')


# Route for displaying user questions and allowing admin to reply
@app.route('/answers', methods=['GET', 'POST'])
def answers():
    if request.method == 'POST':
        # Admin replies to a question
        question_id = request.form.get('question_id')
        reply = request.form.get('reply')

        question = Question.query.get_or_404(question_id)
        question.reply = reply
        db.session.commit()

    # Fetch all questions
    questions = Question.query.all()
    return render_template('answers.html', questions=questions)

# Route for displaying questions posted by admin
# Modify the query to join AdminQuestion with Question


@app.route('/followersquestions', methods=['GET', 'POST'])
def followersquestions():
    if request.method == 'POST':
        # Add logic for posting questions by admin
        pass

    # Modify the query to join AdminQuestion with Question
   # Modify the query to join AdminQuestion with Question
    admin_questions = AdminQuestion.query.join(Question).all()

# Pass the data to the template
    return render_template('followersquestions.html', admin_questions=admin_questions)



@app.route('/myanswers')
def my_answers():
    # Fetch all admin questions with answers
    admin_questions = AdminQuestion.query.join(Question).all()
    return render_template('myanswers.html', admin_questions=admin_questions)

# python web server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True, port=os.getenv("PORT", default=5000))

