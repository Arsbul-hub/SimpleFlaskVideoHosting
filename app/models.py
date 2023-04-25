from sqlalchemy_serializer import SerializerMixin

from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa

__basemodel = db.Model


class User(UserMixin, __basemodel, SerializerMixin):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(), index=True, unique=True)
    password_hash = sa.Column(sa.String(128))
    recommendations = sa.Column(sa.String)
    studios = db.relationship('Studios', backref='user', lazy=True)

    def __repr__(self):
        return 'Пользователь {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class VideoPosts(__basemodel, SerializerMixin):
    __tablename__ = 'video_posts'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String())
    description = sa.Column(sa.String())
    cover_id = sa.Column(sa.Integer())
    source_id = sa.Column(sa.Integer())
    studio_id = sa.Column(sa.Integer(), db.ForeignKey('studios.id'))
    timestamp = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)


class Resource(__basemodel, SerializerMixin):
    __tablename__ = 'resources'
    id = sa.Column(sa.Integer, primary_key=True)
    format = sa.Column(sa.String)
    source = sa.Column(sa.String)
    timestamp = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)


class Studios(__basemodel, SerializerMixin):
    __tablename__ = 'studios'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String())
    description = sa.Column(sa.String())
    cover_id = sa.Column(sa.Integer(), sa.ForeignKey('resources.id'))
    user_id = sa.Column(sa.Integer, db.ForeignKey('user.id'), nullable=True)
    videos = db.relationship('VideoPosts', backref='studios', lazy=True)
