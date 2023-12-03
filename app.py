from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from table_info import profiles, posts, table_event
from flask_migrate import Migrate
from db import db
from sqlalchemy import func

from datetime import timedelta, datetime

# Set up the app and configure sqlalchemy          
app = Flask(__name__)

app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate= Migrate(app,db)

# Home page, not ready
@app.route('/')
def home():
   return '<p> work in progress </p>'

@app.route('/refill', methods = ['GET', 'POST'])
def refill():
   if request.method == 'POST':

      amount = request.form['amount']
      session['account_value'] = session['account_value'] + int(amount)
      found_user = profiles.query.filter(profiles.username == session['username'], profiles.password == session['password']).first()

      if found_user:
         found_user.account_value = session['account_value']
         db.session.commit()
      return redirect(url_for('user_posts'))

   return render_template('refill_account.html', account_info = session['account_info'], account_balance = session['account_value'])

@app.route('/payment', methods=['GET', 'POST'])
def payment():
   if request.method == 'POST':
      
         decision = request.form['choice']

         if decision == 'yes':
            if (session['account_value'] <= 0) or (session['account_value'] < session['amount_owed']):
               last_post = posts.query.filter_by(_id = db.session.query(func.max(posts._id))).first()
               if last_post:
                  db.session.delete(last_post)
                  db.session.commit()
               flash('You do not have enough money!, Please refill account!')
               return redirect(url_for('refill'))
            else:
               session['account_value'] = session['account_value'] - session['amount_owed']
               session['amount_owed'] = 0

            found_user = profiles.query.filter(profiles.username == session['username'], profiles.password == session['password']).first()

            if found_user:
               found_user.account_value = session['account_value']
               db.session.commit()
               return redirect(url_for('user_posts'))
         else:
            last_post = posts.query.filter_by(_id = db.session.query(func.max(posts._id))).first()
            if last_post:
               db.session.delete(last_post)
               db.session.commit()
            return redirect(url_for('user_posts'))
   return(render_template('payment.html', current_balance = session['account_value'], amount_owed = session['amount_owed']))

       

# Allow users to make and look at their posts
@app.route('/user_posts', methods=['GET', 'POST'])
def user_posts():
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
      if 'username' in session:     
         all_user_posts, all_post_times, all_post_types, all_posts_chars = table_event.return_posts(session['id'])



         return render_template('index.html', len = len(all_user_posts), username=session['username'], post=all_user_posts, time_posted=all_post_times, _type = all_post_types, _chars = all_posts_chars, balance = session['account_value'])
      return redirect(url_for('login'))
   
   # grab info from post text area, set info in table
   else:

      
      new_post = request.form['post']
      _chars = len(new_post.split())

      action = request.form['post_type']


      new_object = posts(session['id'], content=new_post, post_type=action, characters=_chars)

      db.session.add(new_object)
      db.session.commit()

      if (session['type'] != 'CU') and (_chars > 20):
         amount_owed = (_chars-20)*0.1
         session['amount_owed'] = amount_owed
         return(redirect(url_for('payment')))
      else:
         amount_owed = _chars
         session['amount_owed'] = amount_owed
         return (redirect(url_for('payment')))


      # new_object = posts(session['id'], content=new_post, post_type=action, characters=_chars)
      # db.session.add(new_object)
      # db.session.commit()
      
      # return redirect(url_for('user_posts'))
      
# login or redirect to create profilef
@app.route('/login', methods=['GET', 'POST'])
def login():
   
   # if logged in, redirect to profile
   if request.method == 'GET':
      if 'username' in session:
         return redirect(url_for('profile', username=session['username']))
      return render_template('login.html')
   
   # take info from login form, set those as current session, query and check if this user account has been made
   else:
      session.permanent = True
      
      current_user = request.form['username']
      current_password = request.form['password']
      
      session['username'] = current_user
      session['password'] = current_password
      
      found_user = profiles.query.filter(profiles.username == current_user, profiles.password == current_password).first()
      
      # If the user is found, log them in and set the id in the session
      if found_user:
         session['id'] = found_user._id
         session['type'] = found_user.user_type
         session['account_value'] = found_user.account_value
         session['account_info'] = found_user.account_info
         
         return redirect(url_for('profile', username=session['username']))
      
      # if the user doesnt exist, redirect to create profile
      else:
         session.clear()
         return redirect(url_for('create_profile'))
      
# when this url is inputted, pop the session info (log user out)
@app.route('/logout')
def logout():
   if 'username' in session:
      session.clear()
   return redirect(url_for('login'))      

# get info from form, set into table
@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
   if request.method == 'GET':
      return render_template('create_profile.html')
   else:
      try:
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
      except:
         return redirect(url_for('login'))
      
      return redirect(url_for('login'))

# show profile if the user is logged in
@app.route('/user')
def profile():
   if 'username' in session:
      return render_template('profile.html', current_username=session['username'])
   else:
      return redirect('login')

# run app!
if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)