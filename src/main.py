"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
#from crypt import methods
import os
from flask import Flask, render_template, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Message, Network, Tag, College, Faculty, Class, File, Coll, Comment, LikedFiles, LikedColls

""" Initializes the database """
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

""" Configures the Login Manager & secret key for sessions """
login_manager = LoginManager(app)
login_manager.init_app(app)
# TODO: Redirect user to the Log In page
# login_manager.login_view = "login"
app.secret_key = "4c73578c1dade3172998bfc97d1d14801e1a27c31ced907653f694efc939d017"

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


"""
! Callback to reload the user from the ID stored in the session
* OvidioSantoro - 2022-02-23
"""
@login_manager.user_loader
def load_user(user_id):
    if User.query.get(user_id):
        return User.query.get(user_id)
    else:
        return None


"""
! TODO THESE ROUTES
* OvidioSantoro - 2022-02-23
"""
@app.route("/")
def sitemap():
    return generate_sitemap(app)

@app.route("/test")
def test():
    return render_template("test.html", user=current_user)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "This will be the main route"
    }

    return jsonify(response_body), 200

@login_manager.unauthorized_handler
def unauthorized():
    # TODO: Return an actual unauthorized handler
    return "YOU NEED TO BE LOGGED IN"


"""
! Gets the current user's received messages
* OvidioSantoro - 2022-02-24
"""
@app.route("/inbox", methods=["GET"])
@login_required
def receivedMessages():
    return Message.receivedMessages(current_user.id)


"""
! Gets the current user's sent messages
* OvidioSantoro - 2022-02-24
"""
@app.route("/inbox/sent", methods=["GET"])
@login_required
def sentMessages():
    return "Message.sentMessages(current_user.id)"


"""
! Sends a message to another user
* OvidioSantoro - 2022-02-24
"""
@app.route("/message", methods=["POST"])
@login_required
def message(request):
    """ Check that every field is received """
    try:
        receiver = request.form["receiver"]
        content = request.form["content"]
    except: 
        return {"success": False,
                "msg": "Unable to send message"},
    
    # Creates the new message
    Message.newMessage(current_user.id, receiver, content)


"""
! Performs the Login
* OvidioSantoro - 2022-02-23
"""
@app.route("/login", methods=["POST"])
def login():
    # TODO: Redirect if the user accesses /login beign already logged in
    if current_user.is_authenticated:
        return "You're already logged"
    
    # Check if the user is in the database
    # TODO: add a double verification to allow logging in also with email
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()
    if user is not None and User.check_password(user.password, password):
        login_user(user)
        # login_user(user, remember=request.form["rememberme"])
        # TODO: Redirect to the main page logged in
        return "Very good, you're in!"
    else: 
        # TODO: Redirect back to the login page with the data already filled
        return "Something went wrong, please check your data"


"""
! Logs out the user
* OvidioSantoro - 2022-02-23
"""
@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    # TODO: Redirect to the Landing Page
    return "You're logged out"


"""
! Creates or retrieves User's networks
* OvidioSantoro - 2022-02-24
"""
@app.route("/networks", methods=["GET", "POST"])
def networks(request):
    if request.method == "GET":
        networks = Network.query.filter_by(owner=current_user.id)
    else:
        pass


"""
! Registers a User into the database
* OvidioSantoro - 2022-02-23
"""
@app.route("/register", methods=["POST"])
def register():

    """ Check that every field is received """
    data = request.form
    try:
        username = data["username"]
        email = data["email"]
        password = data["password"]
        confirmation = data["confirmation"]
        college = data["college"] # This is used to generate the list of faculties
        faculty = data["faculty"]
        classes = data.getlist("classes")
    except: 
        return {"success": False,
                "msg": "Unable to retrieve register data"}, 400

    if password != confirmation:
        return {"success": False,
                "msg": "Password confirmation incorrect"}, 400
    

    """ Check that the unique properties are not already taken """
    if User.query.filter_by(username=username).count() != 0:
        return {"success": False,
                "msg": f"Username {username} already in use"}, 400

    if User.query.filter_by(email=email).count() != 0:
        return {"success": False,
                "msg": f"Email {email} already in registered"}, 400

    # return jsonify(classes) 

    """ Register the user into the database """
    User.register(username, email, password, faculty, classes)

    # TODO: Add an actual response
    # TODO: Ideally, auto-perform a login for the newly created user
    return jsonify("USER REGISTERED")


"""
! Retrieves the selected user's profile
* OvidioSantoro - 2022-02-24
"""
@app.route("/user/<int:userId>", methods=["GET"])
def userProfile(request):
    userId = request.args.get("userId")
    user = User.query.get(userId)

    return user


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
