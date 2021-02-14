import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import create_engine, select,update, and_
from sqlalchemy import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker

app = Flask(__name__, static_folder="images")
app.secret_key='secret_key'
app.config['WTF_CSRF_SECRET_KEY'] = "b'_\xe0z\x04\x93\x1eo/\x94cc\x16\xeb\xfd\x12W]\xd4\xe8(\xa21w\xa9'"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
engine = create_engine("postgres://bwbvzhwczmhedg:8ea3f2bd04330c4c5da37ace8ec658fbb75bdd428555e342be3d413dba84c91d@ec2-3-214-3-162.compute-1.amazonaws.com:5432/dbcbhap8dc3h2c", convert_unicode=True)
conn = engine.connect()
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

things  = Table('things', metadata, autoload=True)

class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    def __repr__(self):
       return " "

    def is_active(self):
       return True

@login_manager.user_loader
def load_user(id):
    return session.query(users).get(int(id))

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=40)])

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),Length(min=3 ,max=50)])
    password = PasswordField('password', validators=[InputRequired(),Length(min=8 ,max=40)])


#users  = Table('user', metadata, autoload=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = session.query(users).filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = users(username=form.username.data, email=form.email.data, password=hashed_password)
        session.add(new_user)
        session.commit()
        form_for_login = LoginForm()
        return render_template('login.html',form=form_for_login)

    return render_template('signup.html', form=form)

@app.route("/", methods=['GET', 'POST'])
def index():
    result = conn.execute(things.select())
    return render_template('home.html', res = result)


@app.route("/filter", methods=[ 'GET','POST'])
def filter():
    return render_template('filter.html')


@app.route("/upload/<filename>")
def send_image(filename):
    return send_from_directory("images", filename)


@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method =='POST':
        name = request.form.get('name')
        title = request.form.get('title')
        email = request.form.get('email')
        description = request.form.get('description')
        tag = request.form.get('tag')
        image_variable = 0
        image1 = ""
        image2 = ""
        image3 = ""
        target = os.path.join(APP_ROOT, 'images\\')
        if not os.path.isdir(target):
            os.mkdir(target)
        for file in request.files.getlist("file"):
            print(file)
            fileName = file.filename + "enagotit"
            if image_variable == 0:
                image1 = fileName
                print(image1+"***")
            elif image_variable == 1:
                image2 = fileName
                print(image2+"***")
            elif image_variable == 2:
                image3 = fileName
                print(image3+"***")
            else:
                print("3 images are enough")
            destination = "\\".join([target,fileName])
            file.save(destination)
            image_variable = image_variable + 1 
        conn.execute(things.insert(), description=description, name=title, img1=image1, img2=image2, img3=image3, tag=tag)
        return render_template('upload.html')
    return render_template('upload.html')
