from db import db
from datetime import datetime

class profiles(db.Model):
   _id = db.Column('id', db.Integer, primary_key = True)
   username = db.Column(db.String(64), unique=True, nullable=False)
   password = db.Column(db.String(64), nullable=False)
   display_name = db.Column(db.String(128), nullable=False)
   birthday = db.Column(db.String(64), nullable=False)
   user_type = db.Column(db.String(64), nullable=False)
   account_info = db.Column(db.Integer, unique=True, nullable=False)
   account_value = db.Column(db.Integer, nullable=False)
   profile_picture = db.Column(db.String(255), default="default.jpg")
   background_picture = db.Column(db.String(255), default="default_background.png")
   bio_info = db.Column(db.String(225), default = "bio")
   post = db.relationship('posts', backref='profiles', lazy=True)
   
   def __init__(self, username, password, display_name, birthday, user_type, account_info, account_value, profile_picture, background_picture, bio_info):
      self.username = username
      self.password = password
      self.display_name = display_name
      self.birthday = birthday
      self.user_type = user_type
      self.account_info = account_info
      self.account_value = account_value
      self.profile_picture = profile_picture
      self.background_picture = background_picture
      self.bio_info = bio_info

class posts(db.Model):
   _id = db.Column('id', db.Integer, primary_key=True)
   content = db.Column(db.Text, nullable=False)
   post_type = db.Column(db.String(50), nullable=False)
   characters = db.Column('characters', db.Integer)
   time_posted = db.Column(db.String(64), nullable=True, default=datetime.now().strftime('%H:%M %B %d, %Y'))
   user_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
   number_of_likes = db.Column(db.Integer, default=0)
   
   likes = db.relationship('likes', backref='post', lazy=True)
   
   def __init__(self, user_id, content, post_type, characters):
      self.user_id = user_id
      self.content = content
      self.post_type = post_type
      self.characters = characters
      

class likes(db.Model):
   _id = db.Column('id', db.Integer, primary_key=True)
   current_user = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
   liked_post = db.Column(db.Integer, db.ForeignKey('posts.id') , nullable=False)
   
   user = db.relationship('profiles', foreign_keys=[current_user])
   
   foreign_posts = db.relationship('posts', foreign_keys=[liked_post])
   
   def __init__(self, current_user, liked_post):
      self.current_user = current_user
      self.liked_post = liked_post
      
      
class table_event():
   def delete_user(temp_username):
      profiles.query.filter_by(username = temp_username).delete()
      db.session.commit()

   def is_liked(temp_user, temp_post):
      # return likes.query.filter_by(liked_post=temp_id).first()
      return likes.query.filter_by(current_user=temp_user, liked_post=temp_post).first()
   
   def get_times_liked(temp_id):
      return likes.query.with_entities(likes.liked_post).filter_by(liked_post=temp_id).all()
      
   
   def return_posts(temp_id):
      all_posts = posts.query.with_entities(posts._id, posts.content, posts.time_posted, posts.number_of_likes, posts.post_type, posts.characters).filter(posts.user_id == temp_id).all()
         
      post_id = []   
      post_text = []
      post_time = []
      post_like_number = []
      post_type = []
      post_chars = []
      for result in all_posts:
         id = result[0]
         content = result[1]
         time = result[2]
         like_number = result[3]
         _type = result[4]
         _chars = result[5]
         
         post_id.append(id)
         post_text.append(content)
         post_time.append(time)
         post_like_number.append(like_number)
         post_type.append(_type)
         post_chars.append(_chars)
      
      return post_id, post_text, post_time, post_like_number, post_type, post_chars
      
   

