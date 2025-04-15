from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    _password_hash: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    bio: Mapped[str] = mapped_column(String)

    recipes: Mapped[List["Recipe"]] = relationship(back_populates="user")

    # Add serialization rules
    serialize_rules = ('-recipes.user',)

    def __repr__(self):
        return f'<User #{self.id} {self.username}!>'

    @hybrid_property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username is required')
        return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[str] = mapped_column(String, nullable=False)
    minutes_to_complete: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped["User"] = relationship(back_populates="recipes")

    # Add serialization rules
    serialize_rules = ('-user.recipes',)

    def __repr__(self):
        return f'<Recipe #{self.id} {self.title}!>'

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError('Title is required')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError('Instructions are required')
        if len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return instructions
