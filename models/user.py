from services.database import db
class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(6), nullable=False)
    user_title = db.Column(db.String(50))
    user_level = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email_address": self.email_address,
            "username": self.username,
            "user_title": self.user_title,
            "user_level": self.user_level
        }