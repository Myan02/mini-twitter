from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from table_info import profiles, posts, likes, table_event
from db import db
import os

from datetime import timedelta, datetime

# Set up the app and configure sqlalchemy          
app = Flask(__name__)

app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db.init_app(app)

def allowed_file(filename):
   return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_profile_picture_filename(user):
   return user.profile_picture if user.profile_picture else 'default.jpg'

# Function to read censored words from a file
def read_censored_words(filename='static/censored_words.txt'):
   with open(filename, 'r') as file:
      return [word.strip() for word in file.readlines()]
     
# Function to censor specific words in the text
def censor_text(text, censor_list, replacement='****'):
   for word in censor_list:
      text = text.replace(word, replacement, -1)
   return text
 
# Welcome page READY!
@app.route('/')# equals to url localhost:5000 or localhost:5000/ or http://127.0.0.1:5000
def welcome(): 
    return render_template('welcome_page.html')
      
# Home page, ready
@app.route('/home', methods=['GET', 'POST'])
def home():
    
   selected_post = request.args.get('selected_post', default=None, type=None)
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
         if 'username' in session:
            all_post_ids, all_user_posts, all_post_times = table_event.return_posts(session['id'])
            current_users_likes = likes.query.with_entities(likes.liked_post).filter(likes.current_user == session['id']).all()
            
            flat_list_of_likes = []
            for row in current_users_likes:
               flat_list_of_likes.extend(row)

            print(f'\n\n{flat_list_of_likes}\n\n')
            print(f'\n\n{all_post_ids}\n\n')
            return render_template('home.html', 
                                 len = len(all_user_posts), 
                                 username=session['username'], 
                                 post_id=all_post_ids, 
                                 post=all_user_posts, 
                                 time_posted=all_post_times,
                                 users_likes=flat_list_of_likes
                                 )
         return redirect(url_for('login'))
   
   # grab info from post text area, set info in table
   elif request.method == 'POST':
      if 'like_button' in request.form:
         is_liked = table_event.is_liked(selected_post)
         print(f'\n\n {is_liked} \n\n')

         if is_liked:
            db.session.delete(is_liked)
            db.session.commit()
         else:
            new_like = likes(session['id'], selected_post)
            db.session.add(new_like)
            db.session.commit()
         
         return redirect(url_for('home'))
      

# Allow users to make and look at their posts
@app.route('/user_posts', methods=['GET', 'POST'])
def user_posts():
   
   selected_post = request.args.get('selected_post', default=None, type=None)
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
         if 'username' in session:
            all_post_ids, all_user_posts, all_post_times = table_event.return_posts(session['id'])
            current_users_likes = likes.query.with_entities(likes.liked_post).filter(likes.current_user == session['id']).all()
            
            flat_list_of_likes = []
            for row in current_users_likes:
               flat_list_of_likes.extend(row)

            print(f'\n\n{flat_list_of_likes}\n\n')
            print(f'\n\n{all_post_ids}\n\n')
            return render_template('user_posts.html', 
                                 len = len(all_user_posts), 
                                 username=session['username'], 
                                 post_id=all_post_ids, 
                                 post=all_user_posts, 
                                 time_posted=all_post_times,
                                 users_likes=flat_list_of_likes
                                 )
         return redirect(url_for('login'))
   
   # grab info from post text area, set info in table
   elif request.method == 'POST':
      if 'tweet_submit' in request.form:
         new_post = request.form['post']
         
         censor_words = read_censored_words()
         censored_content = censor_text(new_post, censor_words)
         
         db.session.add(posts(session['id'], censored_content))
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
         
         if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            profile_picture_filename = secure_filename(profile_picture.filename)

            if profile_picture and allowed_file(profile_picture_filename):
                  profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename))
            else:
                  flash('Invalid profile picture file type. Allowed types are: png, jpg, jpeg, gif')
                  return redirect(request.url)
         else:
            # No profile picture file included, set a default profile picture filename
            profile_picture_filename = 'default_profile.jpg'

         # Check if background picture file is included in the request
         if 'background_picture' in request.files:
            background_picture = request.files['background_picture']
            background_picture_filename = secure_filename(background_picture.filename)

            if background_picture and allowed_file(background_picture_filename):
                  background_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], background_picture_filename))
            else:
                  flash('Invalid background picture file type. Allowed types are: png, jpg, jpeg, gif')
                  return redirect(request.url)
         else:
            # No background picture file included, set a default background picture filename
            background_picture_filename = 'default_background.jpg'

            
         new_user = profiles(new_username, new_password, new_display_name, new_birthday, chosen_user_type, new_account_info, new_account_value)
         db.session.add(new_user)
         db.session.commit()
      except:
         return redirect(url_for('login'))
      
      return redirect(url_for('login'))
   
# show profile if the user is logged in
@app.route('/profile')
def profile():
    if 'username' in session:
        # Get the user from the database
        user = profiles.query.filter_by(username=session['username']).first()

        if user:
            # Get the profile picture filename from the database or use a default value
            profile_picture = get_profile_picture_filename(user)
            return render_template('profile.html', current_username=user.username,
                                   display_name=user.display_name,
                                   birthday=user.birthday,
                                   user_type=user.user_type,
                                   account_info=user.account_info,
                                   account_value=user.account_value,
                                   profile_picture=profile_picture)
        else:
            flash('User not found', 'error')
            return redirect('login')
    else:
        return redirect('login')


# Add a new route for updating the profile picture
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' in session:
        if request.method == 'GET':
            return render_template('update_profile.html', username=session['username'])
        elif request.method == 'POST':
            # Handle profile picture update here
            profile_picture = request.files['profile_picture']
            # background_picture = request.files['background_picture']

            # Check and save the profile picture
            if profile_picture and allowed_file(profile_picture.filename):
                profile_filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_filename))
            else:
                flash('Invalid profile picture file type. Allowed types are: png, jpg, jpeg, gif')
                return redirect(url_for('update_profile'))

            # Check and save the background picture
            # if background_picture and allowed_file(background_picture.filename):
            #     background_filename = secure_filename(background_picture.filename)
            #     background_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], background_filename))
            # else:
            #     flash('Invalid background picture file type. Allowed types are: png, jpg, jpeg, gif')
            #     return redirect(url_for('update_profile'))

            # Update the user's profile and background pictures in the database
            user = profiles.query.filter_by(username=session['username']).first()
            user.profile_picture = profile_filename
            # user.background_picture = background_filename
            db.session.commit()

            flash('Profile and background pictures updated successfully', 'success')
            return redirect(url_for('profile', username=session['username']))

    # If 'username' is not in session, redirect to login
    return redirect(url_for('login'))

# # show profile if the user is logged in
# @app.route('/user')
# def profile():
#    if 'username' in session:
#       return render_template('profile.html', current_username=session['username'])
#    else:
#       return redirect('login')

# run app!
if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)
