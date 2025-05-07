# Technical Lesson: Authenticating Users

## Scenario

We've seen how cookies can be used to store data in a user's browser. One of the most common
uses of cookies is for login. In this lesson, we'll cover how to use the Flask session to log
users in.

## Tools & Resources

- [GitHub Repo](https://github.com/learn-co-curriculum/flask-authenticating-users-technical-lesson)
- [What is Authentication? - auth0](https://auth0.com/intro-to-iam/what-is-authentication)
- [API - Flask: class flask.session](https://flask.palletsprojects.com/en/2.2.x/api/#flask.session)
- [Flask RESTful Documentation](https://flask-restful.readthedocs.io/en/latest/quickstart.html)

## Set Up

There is some starter code in place for a Flask API backend.
To get set up, run:

```bash
pipenv install
pipenv shell
cd server
flask db upgrade
python seed.py
```

You can run the Flask server with:

```bash
python app.py
```

## Instructions

### Task 1: Define the Problem

We are tasked with building the backend for the login feature of a new application.
The frontend will be handled by another team, but we need to provide endpoints for them to
- log a user in
- log a user out
- check if a user is logged in on refresh

### Task 2: Determine the Design

The login/logout flow will look like:

- The user navigates to a login form on the React frontend.
- The user enters their username. There is no password (for now).
- The user submits the form, POSTing to `/login` on the Flask backend.
- In the login view we set a cookie on the user's browser by writing their user
  ID into the session hash.
- Thereafter, the user is logged in. `session['user_id']` will hold their user
  ID.

We'll also use a new package - `flask-restful` - for creating our routes. Flask Restful
will allow us to easily define GET, POST, PATCH, and DELETE requests at a route. For example,
if we have an API that allows full CRUD of a Note:

```python
from flask import Flask, make_response, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Note, NoteSchema

# Define class for endpoint /notes, inheritting from flask_restful's Resource
class Notes(Resource):
    # route function for GET /notes
    def get(self):
        notes = Note.query.all()
        return NoteSchema().dump(notes)

    # route function for POST /notes    
    def post(self):
      new_note = Note(
          title=request.form['title'],
          body=request.form['body'],
      )

      db.session.add(new_record)
      db.session.commit()

      response = make_response(
          NoteSchema().dump(new_note),
          201,
      )

      return response

# Define class for endpoint /notes/<id>, inheritting from flask_restful's Resource
class NoteByID(Resource):
    # route function for GET /notes/<id>
    def get(self, id):

        note = Note.query.filter_by(id=id).first()

        response = make_response(
            NoteSchema().dump(note),
            200,
        )

        return response

    # route function for PATCH /notes/<id>
    def patch(self, id):

        note = Note.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.add(note)
        db.session.commit()

        response = make_response(
            NoteSchema().dump(note),
            200
        )

        return response

    # route function for DELETE /notes/<id>    
    def delete(self, id):

        note = Note.query.filter(Note.id == id).first()

        db.session.delete(note)
        db.session.commit()

        response = make_response(
            {"message": "record successfully deleted"},
            200
        )

        return response

# Add Notes routes to API
api.add_resource(Notes, '/notes')
# Add NoteByID routes to API
api.add_resource(NoteByID, '/notes/<int:id>')
```

### Task 3: Develop, Test, and Refine the Code

#### Step 1: Allowing Users to Login

Let's write a view to handle our login route. This class will handle `POST`
requests to `/login`:

```py
# Define class for /login routes
class Login(Resource):

    def get(self):
        ...

    def post(self):
        ...

# Add routes from Login class to API
api.add_resource(Login, '/login')
```

This request should include login credentials (such as username and password)
from a frontend login form. We'll discuss password protection in the next module.
For now, we'll just look at receiving a "username" from the frontend.

When we get the username, we'll want to look in our database to see if that user exists.
If the user exists, we need to log them in by creating a session. If the user doesn't,
we'll send an invalid login response.

```py
class Login(Resource):

    def post(self):
        user = User.query.filter(
            User.username == request.get_json()['username']
        ).first()
        
        if user:
            session['user_id'] = user.id
            return UserSchema().dump(user)
        else:
            return {'message': 'Invalid login'}, 401
```

Once logged in, there's no way for the server to log a user out right now.
To allow log out, we'll have to delete the cookie from the user's browser.

Here's what the login component might look like on the frontend:

```jsx
function Login({ onLogin }) {
  const [username, setUsername] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username }),
    })
      .then((r) => r.json())
      .then((user) => onLogin(user));
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

When the user submits the form, they'll be logged in! Our `onLogin` callback
function would handle saving the logged in user's details in state.

#### Step 2: Allowing Users to Stay Logged In

Using the wristband analogy, in the example above, we've shown our ID at the
door (`username`) and gotten our wristband (`session['user_id']`) from the
backend. So our backend has a means of identifying us with each request using
the session object.

Our frontend also knows who we are, because our user data was saved in state
after logging in.

What happens now if we leave the club and try to come back in, by refreshing the
page on the frontend? Well, our **frontend** doesn't know who we are any more,
since we lose our frontend state after refreshing the page. Our **backend** does
know who we are though — so we need a way of getting the user data from the
backend into state when the page first loads.

Here's how we might accomplish that. First, we need a route to retrieve the
user's data from the database using the session hash:

```py
class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return UserSchema().dump(user)
        else:
            return {'message': '401: Not Authorized'}, 401

api.add_resource(CheckSession, '/check_session')
```

The frontend would then be able to include a request to `/check_session` in
a useEffect, so on page load the application will be able to keep the user logged in.

Here's what that might look like in the React App component:

```jsx
function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("/check_session").then((response) => {
      if (response.ok) {
        response.json().then((user) => setUser(user));
      }
    });
  }, []);

  if (user) {
    return <h2>Welcome, {user.username}!</h2>;
  } else {
    return <Login onLogin={setUser} />;
  }
}
```

This is the equivalent of letting someone use their wristband to come back into
the club.

#### Step 3: Allowing Users to Log Out

The log out flow is even simpler. We can add a new route for logging out:

```py
class Logout(Resource):

    def delete(self):
        session['user_id'] = None
        return {'message': '204: No Content'}, 204

api.add_resource(Logout, '/logout')
```

Here's how that might look in the frontend:

```jsx
function Navbar({ onLogout }) {
  function handleLogout() {
    fetch("/logout", {
      method: "DELETE",
    }).then(() => onLogout());
  }

  return (
    <header>
      <button onClick={handleLogout}>Logout</button>
    </header>
  );
}
```

The `onLogout` callback function would handle removing the information about the
user from state.

#### Step 4: Commit and Push Git History

* Commit and push your code:

```bash
git add .
git commit -m "final solution"
git push
```

* If you created a separate feature branch, remember to open a PR on main and merge.

### Task 4: Document and Maintain

Best Practice documentation steps:
* Add comments to the code to explain purpose and logic, clarifying intent and functionality of your code to other developers.
* Update README text to reflect the functionality of the application following https://makeareadme.com. 
  * Add screenshot of completed work included in Markdown in README.
* Delete any stale branches on GitHub
* Remove unnecessary/commented out code
* If needed, update git ignore to remove sensitive data

## Conclusion

At its base, login is very simple: the user provides you with credentials by
filling out a form, you verify those credentials and set a token in the
`session`. In this example, our token was their user ID. We can also log users
out by removing their user ID from the session.

## Considerations

### Cookies, Sessions, and Proxies

Since they can't run on the same port, we normally run our `React` client on
`http://localhost:3000` and `Flask` server on `http://localhost:5555` . We've
seen how to enable `CORS` in the server to receive requests from other origins
(different ports mean different origins). However, by default `CORS` does not
allow cookies to be submitted across origins due to potential security
implications . Thus, while `CORS` enables the server to accept requests from
other origins, the browser is not actually storing the cookies/sessions
generated by the server. Since a session is stored as a cookie, this presents a
challenge to our ability to authenticate users.

The simplest solution is to use a proxy. Recall a proxy field must be specified
in `package.json`:

```
"proxy": "http://localhost:5555"
```

We've seen how a proxy let's us write `fetch` requests in our `React` frontend
that don't include the backend domain. Thus, we can pass `"/login"` as the first
parameter to `fetch` rather than `"http://localhost:5555/login"`.

```jsx
function Login({ onLogin }) {
  const [username, setUsername] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    fetch("/login", {
      ...
    })
    ...
```

The proxy also let's us get around the `CORS` cookie issue. Rather than the
browser sending a request to the server directly, the proxy acts as a bridge to
send the request to `http://localhost:5555/login`. The server sends its response
back through the proxy. The proxy makes it appear as if the client request and
server response were from the same origin, thus allowing us to use cookies and
sessions for user authorization.
