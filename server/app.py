#!/usr/bin/env python3

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

# Define class for /login routes
class Login(Resource):
    
    def post(self):
        """
        Handle user login by checking username and creating session.
        
        Expects JSON: {"username": "some_username"}
        Returns: User data if successful, error message if not
        """
        try:
            data = request.get_json()
            username = data.get('username')
            
            if not username:
                return {'message': 'Username is required'}, 400
            
            # Look for user in database by username
            user = User.query.filter(User.username == username).first()
            
            if user:
                # User exists - create session and log them in
                session['user_id'] = user.id
                return UserSchema().dump(user), 200
            else:
                # User doesn't exist - return error
                return {'message': 'Invalid login'}, 401
                
        except Exception as e:
            return {'message': 'Login failed'}, 400


class CheckSession(Resource):
    
    def get(self):
        """
        Check if user is logged in by verifying session.
        
        Returns: User data if session is valid, error message if not
        """
        # Get user_id from session
        user_id = session.get('user_id')
        
        if user_id:
            # Session exists - look up user in database
            user = User.query.filter(User.id == user_id).first()
            if user:
                return UserSchema().dump(user), 200
        
        # No valid session found
        return {'message': '401: Not Authorized'}, 401


class Logout(Resource):
    
    def delete(self):
        """
        Log out user by clearing their session.
        
        Returns: Success message
        """
        # Clear the user_id from session to log them out
        session['user_id'] = None
        return {'message': '204: No Content'}, 204


# Add routes from classes to API
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)