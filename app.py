from flask import Flask, render_template, url_for, redirect, request, session, flash
from table_info import profiles, posts, profile_update
from db import db

from datetime import timedelta, datetime

# # create an instance of a flask web app and store it in app
# app = Flask(__name__)

# # create a secret key value to allow POST methods for safe data retrieval
# app.secret_key = 'key'

# # configure app for SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # set the time data is kept in the server session to 5 minutes
# app.permanent_session_lifetime = timedelta(minutes = 5)

# db = SQLAlchemy(app)

# class users(db.Model):
#    _id = db.Column('id', db.Integer, primary_key = True)
#    name = db.Column(db.String(64))
#    email = db.Column(db.String(128))
   
#    def __init__(self, name, email):
#       self.name = name
#       self.email = email

# # route to the home page
# @app.route('/')
# def home():
#    return render_template('index.html')

# @app.route('/view')
# def view():
#    return render_template('view.html', values=users.query.all())

# # route to the profile page
# @app.route('/profile')
# def profile():
#    return render_template('profile.html')

# # route to the login page and get user info through POST
# @app.route('/login', methods=["GET", "POST"])
# def login():
#    # if we are submitting information from the form: create a session and redirect to the user page
#    if request.method == 'POST':
#       session.permanent = True      # make the 5 minute sessions true
#       user = request.form['un']     # get the value from the text form and store it in user
#       session['user'] = user        # set 'user' as the key, and our username as the value
      
#       found_user = users.query.filter_by(name = user).first()
#       if found_user:
#          session['email'] = found_user.email
#       else:
#          usr = users(user, None)
#          db.session.add(usr)
#          db.session.commit()
      
      
#       flash("login success!")
#       return redirect(url_for('user'))
#    # if we are just visiting the page, redirect to the login page, or to the user if their info is still stored
#    else:
#       if 'user' in session:         # if the value user exists in our session, redirect to the user page
#          flash("Already logged in!")
#          return redirect(url_for('user'))
#       return render_template('login.html')
      
   
# # route to the user page only after logging in, else just go to the login page
# @app.route('/user', methods=["GET", "POST"])
# def user():
#    email = None
#    if 'user' in session:
#       user = session['user']
      
#       if request.method == "POST":
#          email = request.form['email']
#          session['email'] = email
#          found_user = users.query.filter_by(name = user).first()
#          found_user.email = email
#          db.session.commit()
#          flash('email was saved!')
#       else:
#          if 'email' in session:
#             email = session["email"]
         
#       return render_template('user.html', email = email)
#    else:
#       flash('You are not logged in.')
#       return redirect(url_for('login'))
   
# # basically a function to delete info on the user and redirect to the login page
# @app.route('/logout')
# def logout():
#    if 'user' in session:
#       user = session['user']
#       session.pop('user', None)
#       session.pop('email', None)
#       flash(f'You have been logged out, {user}.', 'info')   # category info, warning, and error built in
#    return redirect(url_for('login'))

# # run the instance of the flask application
# if __name__ == '__main__':
#    with app.app_context():
#       db.create_all()
#    app.run(debug = True)


app = Flask(__name__)

app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():
   if request.method == 'GET':
      return render_template('index.html')
   else:
      pass
   

      
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'GET':
      if 'username' in session:
         return redirect(url_for('profile', username=session['username']))
      return render_template('login.html')
   else:
      session.permanent = True
      current_user = request.form['username']
      current_password = request.form['password']
      session['username'] = current_user
      session['password'] = current_password
      
      found_user = profiles.query.filter(profiles.username == current_user, profiles.password == current_password).first()
      if found_user:
         session['type'] = found_user.user_type
         
         return redirect(url_for('profile', username=session['username']))
      else:
         session.clear()
         return redirect(url_for('create_profile'))
      
@app.route('/logout')
def logout():
   if 'username' in session:
      session.clear()
   return redirect(url_for('login'))      

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
   if request.method == 'GET':
      return render_template('create_profile.html')
   else:
      new_username = request.form['create_username']
      new_password = request.form['create_password']
      new_display_name = request.form['display_name']
      new_birthday = request.form['birthday']
      chosen_user_type = request.form['user_type']
      new_account_info = request.form['account_info']
      new_account_value = request.form['account_value']
      
      new_user = profiles(new_username, new_password, new_display_name, new_birthday, chosen_user_type, new_account_info, new_account_value)
      db.session.add(new_user)
      db.session.commit()
      
      return redirect(url_for('login'))

@app.route('/user/<username>')
def profile(username):
   if 'username' in session:
      return render_template('profile.html', current_username=username)
   else:
      return redirect('login')

if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)