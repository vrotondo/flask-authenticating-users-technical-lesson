!/usr/bin/env python3

from flask import Flask, make_response, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Define routes

if __name__ == '__main__':
    app.run(port=5555, debug=True)