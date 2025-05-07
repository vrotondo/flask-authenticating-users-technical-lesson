from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from marshmallow import Schema, fields

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)

    def __repr__(self):
        return f'User {self.username}, ID {self.id}'

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
