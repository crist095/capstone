

from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import os

#database_path = os.environ['postgresql://postgres:telefon095@localhost:5432/capstone']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:telefon095@localhost:5432/project2'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    manager = db.Column(db.Boolean, nullable=False, default=False)
    
    

    def __init__(self, email,password, manager):
        self.name = name
        self.password = password
        self.manager = manager

    def format(self):
        return {
          'id': self.id,
          'email': self.email,
          'password': self.password}