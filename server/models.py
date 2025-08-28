from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt

from config import db, bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False, default=bcrypt.generate_password_hash("defaultpassword").decode('utf-8'))
    image_url = db.Column(db.String, nullable=True)
    bio = db.Column(db.String, nullable=True)

    recipes = db.relationship("Recipe", back_populates="user", cascade="all, delete-orphan", single_parent=True) 
    serialize_rules = ("-recipes.user", "-_password_hash",)

    def __repr__(self):
        return f"<User {self.username}>"
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes cannot be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, value):
        if not value:
            raise ValueError("Username is required")
        return value


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", back_populates="recipes")

    serialize_rules = ("-user.recipes",)

    @validates("title")
    def validate_title(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Title must be present")
        return value

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Instructions must be present")
        if len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return value
    
    def __repr__(self):
        return f"<Recipe {self.title}>" 
