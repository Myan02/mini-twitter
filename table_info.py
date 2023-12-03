from db import db
from datetime import datetime

class profiles(db.Model):
   _id = db.Column('id', db.Integer, primary_key = True)
   username = db.Column(db.String(64), unique=True, nullable=False)
   password = db.Column(db.String(64))
   display_name = db.Column(db.String(128))
   birthday = db.Column(db.String(64))
   user_type = db.Column(db.String(64))
   account_info = db.Column(db.Integer)
   account_value = db.Column(db.Integer)
   profile_picture = db.Column(db.String(255))
   background_picture = db.Column(db.String(255))
   post = db.relationship('posts', backref='profiles', lazy=True)
   
   def __init__(self, username, password, display_name, birthday, user_type, account_info, account_value, profile_picture = None, background_picture = None):
      self.username = username
      self.password = password
      self.display_name = display_name
      self.birthday = birthday
      self.user_type = user_type
      self.account_info = account_info
      self.account_value = account_value
      self.profile_picture = profile_picture
      self.background_picture = profile_picture

class posts(db.Model):
   _id = db.Column('id', db.Integer, primary_key=True)
   content = db.Column(db.Text, nullable=False)
   time_posted = db.Column(db.String(64), nullable=True, default=datetime.now().strftime('%H:%M %B %d, %Y'))
   user_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
   number_of_likes = db.Column(db.Integer, default=0)
   
   likes = db.relationship('likes', backref='post', lazy=True)
   
   def __init__(self, user_id, content):
      self.user_id = user_id
      self.content = content
      

class likes(db.Model):
   _id = db.Column('id', db.Integer, primary_key=True)
   current_user = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
   liked_post = db.Column(db.Integer, db.ForeignKey('posts.id') , nullable=False)
   
   def __init__(self, current_user, liked_post):
      self.current_user = current_user
      self.liked_post = liked_post
      
      
class table_event():
   def delete_user(temp_username):
      profiles.query.filter_by(username = temp_username).delete()
      db.session.commit()

   def is_liked(temp_id):
      return likes.query.filter_by(liked_post=temp_id).first()
   
   def get_times_liked(temp_id):
      return likes.query.with_entities(likes.liked_post).filter_by(liked_post=temp_id).all()
      
   
   def return_posts(temp_id):
      all_posts = posts.query.with_entities(posts._id, posts.content, posts.time_posted, posts.number_of_likes).filter(posts.user_id == temp_id).all()
         
      post_id = []   
      post_text = []
      post_time = []
      post_like_number = []
      for result in all_posts:
         id = result[0]
         content = result[1]
         time = result[2]
         like_number = result[3]
         
         post_id.append(id)
         post_text.append(content)
         post_time.append(time)
         post_like_number.append(like_number)
      
      return post_id, post_text, post_time, post_like_number
      
   

