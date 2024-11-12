from datetime import datetime
from services.database import db

class Till(db.Model):
    __tablename__ = 'till'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    time_in = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, username, amount):
        self.user_id = user_id
        self.username = username
        self.amount = amount
