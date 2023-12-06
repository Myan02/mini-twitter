from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from flask_migrate import Migrate
from sqlalchemy import func
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
   if user.profile_picture:
      return user.profile_picture
   else:
      return 'default.jpg'
   # return user.profile_picture if user.profile_picture else 'default.jpg'

# Function to read censored words from a file
def read_censored_words(filename='static/censored_words.txt'):
   with open(filename, 'r') as file:
      return [word.strip() for word in file.readlines()]
     
# Function to censor specific words in the text
def censor_text(text, censor_list, replacement='****'):
   censor_list = censor_list + [word.upper() for word in censor_list]

   for word in censor_list:
      text = text.replace(word, replacement, -1)
   return text
 
# Welcome page READY!
@app.route('/')# equals to url localhost:5000 or localhost:5000/ or http://127.0.0.1:5000
def welcome(): 
    return render_template('welcome_page.html')
      

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
            profile_picture_filename = 'default.jpg'

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
            background_picture_filename = 'default_background.png'

            
         new_user = profiles(new_username, new_password, new_display_name, new_birthday, chosen_user_type, new_account_info, new_account_value, profile_picture_filename, background_picture_filename)
         db.session.add(new_user)
         db.session.commit()
      except:
         return redirect(url_for('login'))
      
      return redirect(url_for('login'))
   

# Home page, ready
@app.route('/home', methods=['GET', 'POST'])
def home():
    
   selected_post = request.args.get('selected_post', default=None, type=None)
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
      if 'username' in session:
         all_post_ids, all_user_posts, all_post_times, all_post_like_number, all_post_types, all_posts_chars = table_event.return_posts(session['id'])
         current_users_likes = likes.query.with_entities(likes.liked_post).filter(likes.current_user == session['id']).all()
         
         flat_list_of_likes = []
         for row in current_users_likes:
            flat_list_of_likes.extend(row)
         
         # Joining posts and profiles tables
         query = db.session.query(posts, profiles).join(profiles, posts.user_id == profiles._id)
         
            # Executing the query
         all_posts = query.all()
         
         # Transforming the result into a list of dictionaries
         posts_with_profiles = []
         for post, profile in all_posts:
            post_dict = {
               'post_id': post._id,
               'content': post.content,
               'time_posted': post.time_posted,
               'user_id': profile._id,
               'username': profile.username,
               'likes': post.number_of_likes,
               'type': post.post_type
            }
            posts_with_profiles.append(post_dict)
         
         return render_template('home.html', 
                              len = len(all_user_posts), 
                              username=session['username'], 
                              post_id=all_post_ids, 
                              post=all_user_posts, 
                              time_posted=all_post_times,
                              users_likes=flat_list_of_likes,
                              users_number_of_likes=all_post_like_number,
                              posts_with_profiles=posts_with_profiles,
                              _type = all_post_types, 
                              _chars = all_posts_chars, 
                              balance = session['account_value']
                              )
      return redirect(url_for('login'))
   
   # grab info from post text area, set info in table
   elif request.method == 'POST':
      if 'tweet_submit' in request.form:
         try:
            new_post = request.form['post']
            
            censor_words = read_censored_words()
            censored_content = censor_text(new_post, censor_words)
            
            _chars = len(censored_content.split())

            #type of post it is (ad,job,regular)
            action = request.form['post_type']

            # store the post information into a session
            session['new_post'] = censored_content
            session['words'] = _chars
            session['action'] = action
            
               # If you are a TU/OU, write more than 20 words, and it is a regular post
            if (session['type'] != 'CU') and (_chars > 20) and (session['action'] == 'regular'):
               amount_owed = (_chars-20)*0.1
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))
            
            # If you are a TU/OU, write less than 20 words, and it is a regular post
            elif (session['type'] != 'CU') and (_chars < 20) and (session['action'] == 'regular'):
               new_object = posts(session['id'], content=censored_content, post_type=action, characters=_chars)
               db.session.add(new_object)
               db.session.commit()
               return(redirect(url_for('profile')))
            
            # If you are a TU/OU, write more than 20 words, and it is a job or ad posting 
            elif (session['type'] != 'CU') and (_chars > 20) and (session['action'] != 'regular'):
               amount_owed = 10 + (_chars-20)*0.1
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))
            
            # If you are a TU/OU, write less than 20 words, and it is a job or ad posting
            elif (session['type'] != 'CU') and (_chars < 20) and (session['action'] != 'regular'):
               amount_owed = 10
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))

            # If you are a corporate user 
            else:
               amount_owed = _chars
               session['amount_owed'] = amount_owed
               return (redirect(url_for('payment')))
         except:
            flash('Please select one of the options', 'error')
            return redirect(url_for('home'))  
         
      elif 'like_button' in request.form:
         temp_user = session['id']
         temp_post = selected_post

         is_liked = table_event.is_liked(temp_user, temp_post)
         user_post_liked = posts.query.filter(posts._id == temp_post).first()

         if is_liked:
            db.session.delete(is_liked)
            user_post_liked.number_of_likes -= 1
         else:
            new_like = likes(temp_user, temp_post)
            
            db.session.add(new_like)
            user_post_liked.number_of_likes += 1
            
         db.session.commit()
         return redirect(url_for('home'))

# show profile if the user is logged in
@app.route('/profile', methods=['GET', 'POST'])
def profile():
   
   selected_post = request.args.get('selected_post', default=None, type=None)
   
   # Go to page, query posts table for all posts, display
   if request.method == 'GET':
      if 'username' in session:
         all_post_ids, all_user_posts, all_post_times, all_post_like_number, all_post_types, all_posts_chars = table_event.return_posts(session['id'])
         current_users_likes = likes.query.with_entities(likes.liked_post).filter(likes.current_user == session['id']).all()
         
         flat_list_of_likes = []
         for row in current_users_likes:
            flat_list_of_likes.extend(row)

         user = profiles.query.filter_by(username=session['username']).first()
         profile_picture = get_profile_picture_filename(user)
         
         return render_template('profile.html', 
                              len = len(all_user_posts), 
                              username=session['username'], 
                              post_id=all_post_ids, 
                              post=all_user_posts, 
                              time_posted=all_post_times,
                              users_likes=flat_list_of_likes,
                              users_number_of_likes=all_post_like_number,
                              _type = all_post_types, 
                              _chars = all_posts_chars, 
                              balance = session['account_value'],
                              current_username=user.username,
                              display_name=user.display_name,
                              birthday=user.birthday,
                              user_type=user.user_type,
                              account_info=user.account_info,
                              account_value=user.account_value,
                              profile_picture=profile_picture
                              )
      else:
         flash('User not found', 'error')
         return redirect('login')
   
   # grab info from post text area, set info in table
   elif request.method == 'POST':
      if 'tweet_submit' in request.form:
         try:
            new_post = request.form['post']
            
            censor_words = read_censored_words()
            censored_content = censor_text(new_post, censor_words)
            
            _chars = len(censored_content.split())

            #type of post it is (ad,job,regular)
            action = request.form['post_type']

            # store the post information into a session
            session['new_post'] = censored_content
            session['words'] = _chars
            session['action'] = action
            
               # If you are a TU/OU, write more than 20 words, and it is a regular post
            if (session['type'] != 'CU') and (_chars > 20) and (session['action'] == 'regular'):
               amount_owed = (_chars-20)*0.1
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))
            
            # If you are a TU/OU, write less than 20 words, and it is a regular post
            elif (session['type'] != 'CU') and (_chars < 20) and (session['action'] == 'regular'):
               new_object = posts(session['id'], content=censored_content, post_type=action, characters=_chars)
               db.session.add(new_object)
               db.session.commit()
               return(redirect(url_for('profile')))
            
            # If you are a TU/OU, write more than 20 words, and it is a job or ad posting 
            elif (session['type'] != 'CU') and (_chars > 20) and (session['action'] != 'regular'):
               amount_owed = 10 + (_chars-20)*0.1
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))
            
            # If you are a TU/OU, write less than 20 words, and it is a job or ad posting
            elif (session['type'] != 'CU') and (_chars < 20) and (session['action'] != 'regular'):
               amount_owed = 10
               session['amount_owed'] = amount_owed
               return(redirect(url_for('payment')))

            # If you are a corporate user 
            else:
               amount_owed = _chars
               session['amount_owed'] = amount_owed
               return (redirect(url_for('payment')))
         except:
            flash('Please select one of the options', 'error')
            return redirect(url_for('profile'))
   
      elif 'like_button' in request.form:
         
         temp_user = session['id']
         temp_post = selected_post

         is_liked = table_event.is_liked(temp_user, temp_post)
         user_post_liked = posts.query.filter(posts._id == temp_post).first()

         if is_liked:
            db.session.delete(is_liked)
            user_post_liked.number_of_likes -= 1
         else:
            new_like = likes(temp_user, temp_post)
            
            db.session.add(new_like)
            user_post_liked.number_of_likes += 1
            
         db.session.commit()
         return redirect(url_for('profile'))
   
   

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


@app.route('/refill', methods = ['GET', 'POST'])
def refill():
   if request.method == 'POST':

      amount = request.form['amount']
      session['account_value'] = session['account_value'] + int(amount)
      found_user = profiles.query.filter(profiles.username == session['username'], profiles.password == session['password']).first()

      if found_user:
         found_user.account_value = session['account_value']
         db.session.commit()
      return redirect(url_for('profile'))

   return render_template('refill_account.html', account_info = session['account_info'], account_balance = session['account_value'])

@app.route('/payment', methods=['GET', 'POST'])
def payment():
   if request.method == 'POST':
      
         decision = request.form['choice']

         if decision == 'yes':
            if (session['account_value'] <= 0) or (session['account_value'] < session['amount_owed']):

               flash('You do not have enough money! Please refill account!')
               
               return redirect(url_for('refill'))
            else:
               session['account_value'] = session['account_value'] - session['amount_owed']
               session['amount_owed'] = 0

               new_object = posts(session['id'], content=session['new_post'], post_type=session['action'], characters=session['words'])
               db.session.add(new_object)
               db.session.commit()

            found_user = profiles.query.filter(profiles.username == session['username'], profiles.password == session['password']).first()

            if found_user:
               found_user.account_value = session['account_value']
               db.session.commit()
               return redirect(url_for('profile'))
         else:
            return redirect(url_for('profile'))
   return(render_template('payment.html', current_balance = session['account_value'], amount_owed = session['amount_owed']))

       


# run app!
if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)
