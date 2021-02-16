from app import db

class user_list(db.Model):
    
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)    
        

class image_list(db.Model):
    __tablename__ = 'Image'

    username = db.Column(db.String(20), unique=True, nullable=False)
    imagename = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    image_url=db.Column(db.String(100), primary_key=True)
    upload_hist = db.Column(db.Integer)
        # 0 : image with no faces
        # 1 : image with all faces are wearing mask
        # 2 : image with no faces are wearing mask
        # 3 : image with only some faces
