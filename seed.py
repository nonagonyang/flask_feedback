from email import message_from_binary_file
from app import app
from models import db, User,Feedback


db.drop_all()
db.create_all()

User.query.delete()
Feedback.query.delete()

