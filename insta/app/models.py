from app import db, bcrypt
from flask_login import UserMixin
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired


@login_manager.user_loader
def load_user(id):
   return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self, expiration=3600):
        '''
        Generate a password reset change token to email to an existing user
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """Verify the new password for this user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.add(self)
        db.session.commit()
        return True


