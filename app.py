from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from table_info import profiles, posts, likes, table_event
from db import db

from datetime import timedelta, datetime

# Set up the app and configure sqlalchemy          
app = Flask(__name__)

app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Home page, not ready
@app.route('/')
def home():
   return '<p> work in progress </p>'

# Allow users to make and look at their posts
@app.route('/user_posts', methods=['GET', 'POST'], defaults={'selected_post': 0})
@app.route('/user_posts/<selected_post>', methods=['POST'])
def user_posts(selected_post):
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
         if 'username' in session:
            all_post_ids, all_user_posts, all_post_times = table_event.return_posts(session['id'])
            current_users_likes = likes.query.with_entities(likes.liked_post).filter(likes.current_user == session['id']).all()
            
            flat_list_of_users = []
            for row in current_users_likes:
               flat_list_of_users.extend(row)

            print(f'\n\n{flat_list_of_users}\n\n')
            print(f'\n\n{all_post_ids}\n\n')
            print(f'\n\n{current_users_likes}\n\n')
            return render_template('index.html', 
                                 len = len(all_user_posts), 
                                 username=session['username'], 
                                 post_id=all_post_ids, 
                                 post=all_user_posts, 
                                 time_posted=all_post_times,
                                 users_likes=flat_list_of_users
                                 )
         return redirect(url_for('login'))
   
   # grab info from post text area, set info in table
   elif request.method == 'POST':
      if 'tweet_submit' in request.form:
         new_post = request.form['post']
      
         db.session.add(posts(session['id'], new_post))
         db.session.commit()
         
         return redirect(url_for('user_posts'))
      
      elif 'like_button' in request.form:
         is_liked = table_event.is_liked(selected_post)
         print(f'\n\n {is_liked} \n\n')

         if is_liked:
            db.session.delete(is_liked)
            db.session.commit()
         else:
            new_like = likes(session['id'], selected_post)
            db.session.add(new_like)
            db.session.commit()
         return redirect(url_for('user_posts'))

# login or redirect to create profile
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