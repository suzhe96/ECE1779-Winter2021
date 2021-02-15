from app import db

class user_list(db.Model):
    
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)    
        

class image_list(db.Model):
    imagename = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)

