from conversion import db, login_manager
from conversion import bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_adress = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    files = db.relationship('File', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    

class File(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    convert_type = db.Column(db.String(64), nullable=False)
    original_file = db.Column(db.String(length=256), nullable=False)
    converted_file = db.Column(db.String(length=256), nullable=False)
    original_data = db.Column(db.LargeBinary, nullable=True)
    converted_data = db.Column(db.LargeBinary, nullable=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    def __repr__(self):
        return f'ConversionHistory {self.id}: {self.original_file} -> self{self.converted_file} '
    
    def add(self, user):
        self.owner = user.id
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
