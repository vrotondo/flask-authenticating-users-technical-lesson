#!/usr/bin/env python3

from faker import Faker
from app import app
from models import db, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    User.query.delete()

    print("Creating users...")
    users = []
    usernames = []
    
    for i in range(25):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        
        usernames.append(username)
        user = User(username=username)
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    
    print("Complete.")
    print(f"Created {len(users)} users:")
    for user in users[:5]:  # Show first 5 users
        print(f"  - {user.username}")
    print("  ...")