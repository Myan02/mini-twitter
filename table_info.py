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
   post = db.relationship('posts', backref='profiles', lazy=True)
   
   def __init__(self, username, password, display_name, birthday, user_type, account_info, account_value):
      self.username = username
      self.password = password
      self.display_name = display_name
      self.birthday = birthday
      self.user_type = user_type
      self.account_info = account_info
      self.account_value = account_value

class posts(db.Model):
   _id = db.Column('id', db.Integer, primary_key=True)
   content = db.Column(db.Text, nullable=False)
   time_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   user_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
   
   def __init__(self, content):
      self.content = content
      
   

