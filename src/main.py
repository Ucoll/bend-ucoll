"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
#from crypt import methods
import os
from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Message, Network, Tag, College, Faculty, Class, File, Coll, Comment, LikedFiles, LikedColls

# ----------------------------------------------------------------------------------------------

""" Initializes the database """
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# ----------------------------------------------------------------------------------------------
""" Handle/serialize errors like a JSON object"""
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

""" Configures the Login Manager & secret key for sessions """
# TODO: Change the Flask_login for a custom JWT Token generator and verifier
login_manager = LoginManager(app)
login_manager.init_app(app)
# TODO: Redirect user to the Log In page
# login_manager.login_view = "login"
app.secret_key = "4c73578c1dade3172998bfc97d1d14801e1a27c31ced907653f694efc939d017"

# ----------------------------------------------------------------------------------------------

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

@login_manager.unauthorized_handler
def unauthorized():
    # TODO: Return an actual unauthorized handler
    return "YOU NEED TO BE LOGGED IN"


# ----------------------------------------------------------------------------------------------
#####################
# ? CLASS ENDPOINTS
#####################

"""
! Gets the list of all Classes
* OvidioSantoro - 2022-02-25
"""
@app.route("/classes", methods=["GET"])
@login_required
def classes():
    return jsonify(list(map(lambda x: x.serialize(), Class.query.all())))

"""
! Gets a certain Class or add current user to it
* OvidioSantoro - 2022-03-04
"""
@app.route("/classes/<int:classId>", methods=["GET", "POST"])
@login_required
def get_class(classId):
    _class = Class.query.get(classId)
    if request.method == "GET":
        return jsonify(_class.serialize())
    else:
        students = [student for student in _class.students]
        user = User.query.get(current_user.id)
        students.append(user)
        Class.update_students(_class.id, students)
        return redirect(f"/classes/{classId}")

"""
! Removes current user from a Class
* OvidioSantoro - 2022-03-04
"""
@app.route("/classes/<int:classId>/leave", methods=["POST"])
@login_required
def leave_class(classId):
    _class = Class.query.get(classId)
    user = User.query.get(current_user.id)
    students = [student for student in _class.students]
    students.remove(user)
    Class.update_students(_class.id, students)
    return redirect("/home")
    

# ----------------------------------------------------------------------------------------------
#####################
# ? COLL ENDPOINTS
#####################

"""
! Return all the Colls or Create a new Coll
* OvidioSantoro - 2022-02-25
"""
@app.route("/colls", methods=["GET", "POST"])
@login_required
def colls():
    # Return all Colls
    if request.method == "GET":
        return jsonify(list(map(lambda x: x.serialize(), Coll.query.all())))
    
    # Create a new Coll
    else:
        """ Check that every field is received """
        try:
            title = request.form["title"]
            content = request.form["content"]
            _class = request.form["_class"]
            type = request.form["type"]
        except: 
            return {"success": False,
                    "msg": "Unable to create Coll"}, 400
    
        # If all fields are filled, save the Coll
        if title != "" and content != "" and _class != "" and type != "":
            Coll.create(
                current_user.get_id(), 
                title,
                content,
                _class,
                type
            )
            return redirect("/colls")
        else:
            return {"success": False,
                    "msg": "Unable to create Coll"}, 400


"""
! Returns the Colls of a certain Class
* OvidioSantoro - 2022-02-25
"""
@app.route("/colls/class/<int:classId>", methods=["GET"])
@login_required
def get_class_colls(classId):
    colls = Class.query.filter_by(class_id = classId)
    return jsonify(list(map(lambda x: x.serialize(), colls)))

"""
! Returns a single Coll (For full-page) or edits it
* OvidioSantoro - 2022-02-25
"""
@app.route("/colls/<int:collId>", methods=["GET", "POST"])
@login_required
def get_coll(collId):
    coll = Coll.query.get(collId)
    if request.method == "GET":
        return jsonify(coll.serialize())
    else:
        title = request.form["title"]
        content = request.form["content"]
        Coll.update(coll, title, content)
        return redirect(f"/colls/{collId}")


"""
! Removes a Coll from the database
* OvidioSantoro - 2022-03-05
"""
@app.route("/colls/<int:collId>/delete", methods=["POST"])
@login_required
def delete_coll(collId):
    coll = Coll.query.get(collId)
    Coll.delete(coll)
    return redirect("/colls")

# ----------------------------------------------------------------------------------------------
#####################
# ? COLLEGE ENDPOINTS
#####################

"""
! Gets the list of all Colleges
* OvidioSantoro - 2022-02-25
"""
@app.route("/colleges", methods=["GET"])
@login_required
def colleges():
    return jsonify(list(map(lambda x: x.serialize(), College.query.all())))

"""
! Gets a certain College
* OvidioSantoro - 2022-03-05
"""
@app.route("/colleges/<int:collegeId>", methods=["GET"])
@login_required
def get_college(collegeId):
    college = College.query.get(collegeId)
    return jsonify(college.serialize())

# ----------------------------------------------------------------------------------------------
#####################
# ? FACULTY ENDPOINTS
#####################

"""
! Return all Faculties
* OvidioSantoro - 2022-02-25
"""
@app.route("/faculties", methods=["GET"])
#@login_required
def faculties():
    return jsonify(list(map(lambda x: x.serialize(), Faculty.query.all())))

"""
! Gets a certain Faculty
* OvidioSantoro - 2022-03-05
"""
@app.route("/faculties/<int:facultyId>", methods=["GET"])
@login_required
def get_faculty(facultyId):
    faculty = Faculty.query.get(facultyId)
    return jsonify(faculty.serialize())


# ----------------------------------------------------------------------------------------------
#####################
# ? FILE ENDPOINTS
#####################
# ----------------------------------------------------------------------------------------------
#####################
# ? HOME ENDPOINTS
#####################

"""
! Renders the Landing Page
* OvidioSantoro - 2022-03-XX
"""
@app.route("/")
def sitemap():
    return generate_sitemap(app)

# ----------------------------------------------------------------------------------------------
#####################
# ? MESSAGE ENDPOINTS
#####################

"""
! Gets the current user's received messages
* OvidioSantoro - 2022-02-24
"""
@app.route("/inbox", methods=["GET"])
#@login_required
def receivedMessages():
    return jsonify(list(map(lambda x: x.serialize(), Message.receivedMessages(current_user.get_id()).all())))


"""
! Gets the current user's sent messages
* OvidioSantoro - 2022-02-24
"""
@app.route("/inbox/sent", methods=["GET"])
@login_required
def sentMessages():
    return jsonify(list(map(lambda x: x.serialize(), Message.sentMessages(current_user.get_id()).all())))


"""
! Sends a message to another user
* OvidioSantoro - 2022-02-24
"""
@app.route("/message", methods=["POST"])
@login_required
def message():
    """ Check that every field is received """
    try:
        receiver = request.form["receiver"]
        content = request.form["content"]
    except: 
        return {"success": False,
                "msg": "Unable to send message"}, 400
    
    # Creates the new message
    Message.newMessage(current_user.get_id(), receiver, content)
    return "Message sent"

# ----------------------------------------------------------------------------------------------
#####################
#? NETWORK ENDPOINTS
#####################

"""
! Creates or retrieves User's networks
* OvidioSantoro - 2022-02-24
"""
@app.route("/networks", methods=["GET", "POST"])
def networks():
    if request.method == "GET":
        networks = Network.query.filter_by(owner=current_user.id)
        return jsonify(list(map(lambda x: x.serialize(), networks)))

    else:
        data = request.form
        try:
            name = data["name"]
            link = data["link"]
        except: 
            return {"success": False,
                    "msg": "Unable to create Network"}, 400
    
    Network.create(current_user.id, name, link)
    return jsonify("Network Created")
        


"""
! Updates User's network
* OvidioSantoro - 2022-03-03
"""
@app.route("/networks/<int:networkId>", methods=["POST"])
def network_update():
    network_id = request.args.get("networkId")
    networks = Network.query.filter_by(owner=current_user.id)


"""
!  Deletes User's network
* OvidioSantoro - 2022-03-03
"""
@app.route("/networks/<int:networkId>/delete", methods=["POST"])
def network_delete():
    network_id = request.args.get("networkId")
    networks = Network.query.filter_by(owner=current_user.id)

# ----------------------------------------------------------------------------------------------
#####################
#? REGISTER & LOGIN ENDPOINTS
#####################

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
        #college = data["college"] # This is used to generate the list of faculties
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

# ----------------------------------------------------------------------------------------------
#####################
# ? USER ENDPOINTS (ME & PROFILE)
#####################

"""
! Gets or Updates the current User's profile
* OvidioSantoro - 2022-03-03
"""
@app.route("/me", methods=["GET", "POST"])
def me():
    user = User.query.get(current_user.id)
    if request.method == "GET":
        return jsonify(user.serialize())
        
    else:
        """ Check that every field is received """
        data = request.form
        try:
            username = data["username"]
            old_password = data["old_password"]
            password = data["password"]
            confirmation = data["confirmation"]
            #college = data["college"] # This is used to generate the list of faculties
            faculty = data["faculty"]
            classes = data.getlist("classes")
        except: 
            return {"success": False,
                    "msg": "Unable to retrieve register data"}, 400

        if not User.check_password(user.password, old_password):
            return {"success": False,
                    "msg": "Old password is not correct"}, 403

        if password != confirmation:
            return {"success": False,
                    "msg": "Password confirmation incorrect"}, 400
    

        """ Check that the unique properties are not already taken """
        if (username != user.username) and User.query.filter_by(username=username).count() != 0:
            return {"success": False,
                    "msg": f"Username {username} already in use"}, 403


        """ Register the user into the database """
        User.update(user.id, username, password, faculty, classes)

        # TODO: Add an actual response
        # TODO: Ideally, auto-perform a login for the newly created user
        return jsonify("USER UPDATED")


"""
! Retrieves the selected user's profile
* OvidioSantoro - 2022-02-24
"""
@app.route("/user/<int:userId>", methods=["GET"])
def userProfile(request):
    userId = request.args.get("userId")
    user = User.query.get(userId)

    return user


"""
! Deletes the current User's profile
* OvidioSantoro - 2022-03-03
"""
@app.route("/me/delete", methods=["POST"])
def me_delete():
    User.delete(current_user.id)
    return jsonify("Goodbye, you will be missed :(")

# ----------------------------------------------------------------------------------------------

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
