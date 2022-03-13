"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
#from crypt import methods
import os
from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_migrate import Migrate
from sqlalchemy import null
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from utils import APIException, generate_sitemap
import operator
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

""" Setup the Flask-JWT-Extended extension """
#TODO: STORE THIS KEY INSIDE THE ENV VARIABLES
app.config["JWT_SECRET_KEY"] = "4c73578c1dade3172998bfc97d1d14801e1a27c31ced907653f694efc939d017"
jwt = JWTManager(app)
# ----------------------------------------------------------------------------------------------

# """
# ! Callback to reload the user from the ID stored in the session
# * OvidioSantoro - 2022-02-23
# """
# @login_manager.user_loader
# def load_user(user_id):
#     if User.query.get(user_id):
#         return User.query.get(user_id)
#     else:
#         return None

# @login_manager.unauthorized_handler
# def unauthorized():
#     # TODO: Return an actual unauthorized handler
#     return "YOU NEED TO BE LOGGED IN"

"""
TODO: Main route
"""
@app.route("/", methods=["GET"])
def todo():
    return jsonify("Ucoll Backend is up and running!")


# ----------------------------------------------------------------------------------------------
#####################
# ? CLASS ENDPOINTS
#####################

"""
! Gets the list of all Classes
* OvidioSantoro - 2022-02-25
"""
@app.route("/classes", methods=["GET"])
#@login_required
def classes():
    return jsonify(list(map(lambda x: x.serialize(), Class.query.all())))

"""
! Gets the list of all Classes from a Faculty
* OvidioSantoro - 2022-02-25
"""
@app.route("/classes/faculty/<int:facultyId>", methods=["GET"])
#@login_required
def faculty_classes(facultyId):
    return jsonify(list(map(lambda x: x.serialize(), Class.query.filter_by(faculty_id=facultyId))))

"""
! Gets a certain Class or add current user to it
* OvidioSantoro - 2022-03-04
"""
@app.route("/classes/<int:classId>", methods=["GET", "POST"])
#@login_required
def get_class(classId):
    _class = Class.query.get(classId)
    if request.method == "GET":
        return jsonify(_class.serialize())
    else:
        students = [student for student in _class.students]
        #TODO: CURRENT USER
        user = User.query.get(2)
        students.append(user)
        Class.update_students(_class.id, students)
        return redirect(f"/classes/{classId}")

"""
! Removes current user from a Class
* OvidioSantoro - 2022-03-04
"""
@app.route("/classes/<int:classId>/leave", methods=["POST"])
#@login_required
def leave_class(classId):
    _class = Class.query.get(classId)
    #TODO: CURRENT USER
    user = User.query.get(2)
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
#@login_required
def colls():
    # Return all Colls
    if request.method == "GET":
        return jsonify(list(map(lambda x: x.serialize(), Coll.query.all())))
    
    # Create a new Coll
    else:
        """ Check that every field is received """
        try:
            title = request.json["title"]
            content = request.json["content"]
            _class = request.json["_class"]
            type = request.json["type"]
        except: 
            return {"success": False,
                    "msg": "Unable to receive all data"}, 400
    
        # If all fields are filled, save the Coll
        if title != "" and content != "" and _class != "" and type != "":
            # TODO: Change hardocded user when register is implemented in the front
            Coll.create(
                2, 
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
#@login_required
def get_class_colls(classId):
    colls = Class.query.filter_by(class_id = classId)
    return jsonify(list(map(lambda x: x.serialize(), colls)))

"""
! Returns a single Coll (For full-page) or edits it
* OvidioSantoro - 2022-02-25
"""
@app.route("/colls/<int:collId>", methods=["GET", "POST"])
##@login_required
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
#@login_required
def delete_coll(collId):
    coll = Coll.query.get(collId)
    Coll.delete(coll)
    return redirect("/colls")

"""
! Handles the Like/Dislike clicks
* OvidioSantoro - 2022-03-08
"""
@app.route("/colls/<int:collId>/like", methods=["GET", "POST"])
#@login_required
def handle_like(collId):
    # TODO: Remove hardcoded User (2 = Harry Potter)
    likedColl = LikedColls.query.filter_by(coll_id=collId, user_id=2).first()

    if request.method == "GET":
        if not likedColl:
            return jsonify(None)
        else:
            return jsonify(likedColl.is_like)
    
    else:
        try:
            like = request.json["like"]
        except: 
            return {"success": False,
                    "msg": "Unable to like Coll"}, 500

        if not likedColl:
            # TODO: Remove hardcoded User (2 = Harry Potter)
            LikedColls.create(2, collId, like)
            return jsonify("Coll liked/disliked")
        else:
            if likedColl.is_like == like:
                LikedColls.delete(likedColl)
                return jsonify("Valoration removed")
            else:
                LikedColls.update(likedColl, like)
                return jsonify("Valoration updated")

"""
! Handles the Fav clicks
* OvidioSantoro - 2022-03-10
"""
@app.route("/colls/<int:collId>/fav", methods=["POST"])
#@login_required
def handle_fav(collId):
    # TODO: Remove hardcoded User (2 = Harry Potter)
    user_id = 2
    user = User.query.get(user_id)
    favedColls = list(map(lambda x: x.serialize(),User.query.get(user_id).fav_colls))
    coll = Coll.query.get(collId)

    if coll.serialize() in favedColls:
        Coll.unfav(coll, user)
        return jsonify("Coll unfaved")
    else:
        Coll.fav(coll, user)
        return jsonify("Coll faved") 

# ----------------------------------------------------------------------------------------------
#####################
# ? COLLEGE ENDPOINTS
#####################

"""
! Gets the list of all Colleges
* OvidioSantoro - 2022-02-25
"""
@app.route("/colleges", methods=["GET"])
#@login_required
def colleges():
    return jsonify(list(map(lambda x: x.serialize(), College.query.all())))

"""
! Gets a certain College
* OvidioSantoro - 2022-03-05
"""
@app.route("/colleges/<int:collegeId>", methods=["GET"])
#@login_required
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
##@login_required
def faculties():
    return jsonify(list(map(lambda x: x.serialize(), Faculty.query.all())))

"""
! Return all Faculties from a College
* OvidioSantoro - 2022-02-25
"""
@app.route("/faculties/college/<int:collegeId>", methods=["GET"])
##@login_required
def college_faculties(collegeId):
    return jsonify(list(map(lambda x: x.serialize(), Faculty.query.filter_by(college_id=collegeId))))

"""
! Gets a certain Faculty
* OvidioSantoro - 2022-03-05
"""
@app.route("/faculties/<int:facultyId>", methods=["GET"])
#@login_required
def get_faculty(facultyId):
    faculty = Faculty.query.get(facultyId)
    return jsonify(faculty.serialize())


# ----------------------------------------------------------------------------------------------
#####################
# ? FILE ENDPOINTS
#####################

# TODO: All of these endpoints

# ----------------------------------------------------------------------------------------------
#####################
# ? HOME ENDPOINTS
#####################

"""
! Renders the home page
* OvidioSantoro - 2022-03-05
"""
# TODO: When the Front is installed, check whether this should return something
@app.route("/home")
def sitemap():
    return redirect("/colls")

# ----------------------------------------------------------------------------------------------
#####################
# ? MESSAGE ENDPOINTS
#####################

"""
! Get received Messages or sends a Message
* OvidioSantoro - 2022-02-24
"""
@app.route("/messages", methods=["GET", "POST"])
#@login_required
def message():
    if request.method == "GET":
        #TODO: CURRENT USER
        messages = Message.query.filter_by(receiver = 2)
        return jsonify(list(map(lambda x: x.serialize(), messages)))

    else:
        try:
            receiver = request.form["receiver"]
            content = request.form["content"]
        except: 
            return {"success": False,
                    "msg": "Unable to send message"}, 400
        
        #TODO: CURRENT USER AND CHECK, THIS MIGHT BE WRONG
        Message.create(2, receiver, content)
        return redirect("/messages")

"""
! Gets sent messages
* OvidioSantoro - 2022-03-05
"""
@app.route("/messages/sent", methods=["GET"])
#@login_required
def sent_messages():
    #TODO: CURRENT USER
    messages = Message.query.filter_by(sender = 2)
    return jsonify(list(map(lambda x: x.serialize(), messages)))

"""
! Gets a certain Message or deletes it
* OvidioSantoro - 2022-03-05
"""
@app.route("/messages/<int:messageId>", methods=["GET", "POST"])
#@login_required
def get_message(messageId):
    message = Message.query.get(messageId)
    if request.method == "GET":
        return jsonify(message.serialize())

    else:
        try:
            content = request.form["content"]
        except: 
            return {"success": False,
                    "msg": "Unable to send message"}, 400
        
        Message.update(message, content)
        return redirect("/messages/sent")

"""
! Delete a Message
* OvidioSantoro - 2022-03-05
"""
@app.route("/messages/<int:messageId>/delete", methods=["POST"])
#@login_required
def delete_messages(messageId):
    message = Message.query.get(messageId)
    Message.delete(message)
    return redirect("/messages/sent")

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
        #TODO: CURRENT USER
        networks = Network.query.filter_by(owner=2)
        return jsonify(list(map(lambda x: x.serialize(), networks)))

    else:
        data = request.form
        try:
            name = data["name"]
            link = data["link"]
        except: 
            return {"success": False,
                    "msg": "Unable to create Network"}, 400
    
    #TODO: CURRENT USER
    Network.create(2, name, link)
    return redirect ("/networks")

"""
! Updates User's network
* OvidioSantoro - 2022-03-03
"""
@app.route("/networks/<int:networkId>", methods=["POST"])
def network_update(networkId):
    data = request.form
    try:
        name = data["name"]
        link = data["link"]
    except: 
        return {"success": False,
                "msg": "Unable to create Network"}, 400
    
    network = Network.query.get(networkId)
    Network.update(network, name, link)
    return redirect ("/networks")

"""
!  Deletes User's network
* OvidioSantoro - 2022-03-03
"""
@app.route("/networks/<int:networkId>/delete", methods=["POST"])
def network_delete(networkId):
    network = Network.query.get(networkId)
    Network.delete(network)
    return redirect("/networks")

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
    data = request.json
    try:
        username = data["username"]
        email = data["email"]
        password = data["password"]
        confirmation = data["confirmation"]
        faculty = data["faculty"]
        classes = data["classes"]
    except: 
        return {"success": False,
                "msg": "Unable to retrieve register data"}, 403

    if password != confirmation:
        return {"success": False,
                "msg": "Password confirmation incorrect"}, 403

    """ Check that the unique properties are not already taken """
    if User.query.filter_by(username=username).count() != 0:
        return {"success": False,
                "msg": f"Username {username} already in use"}, 403

    if User.query.filter_by(email=email).count() != 0:
        return {"success": False,
                "msg": f"Email {email} already in registered"}, 403

    """ Register the user into the database """
    print(classes)
    user = User.register(username, email, password, faculty, classes)
    # TODO: Auto log in the user when registered
    return jsonify("USER REGISTERED")


"""
! Performs the Login
* OvidioSantoro - 2022-02-23
"""
@app.route("/login", methods=["POST"])
def login():
    #TODO: CURRENT USER
    # if current_user.is_authenticated:
    #     return redirect("/home")
    
    password = request.json["password"]
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()

    if user is not None and User.check_password(user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token)
    else: 
        return "Something went wrong, please check your login data"

# ----------------------------------------------------------------------------------------------
#####################
#? TAG ENDPOINTS
#####################

"""
! Return all Tags associated to the User
* OvidioSantoro - 2022-06-03
"""
@app.route("/tags", methods=["GET", "POST"])
#@login_required
def tags():
    #TODO: CURRENT USER
    user = User.query.get(2)
    if request.method == "GET":
        return jsonify(list(map(lambda x: x.serialize(), Tag.query.filter_by(user=user))))
    else:
        try:
            name = request.form["name"]
        except:
            return {"success": False,
                    "msg": "Unable to retrieve all the data"}, 400
        
        Tag.create(name, user)
    return redirect("/tags")

@app.route("/tags/<int:tagId>", methods=["POST"])
#@login_required
def update_tag(tagId): 
    try:
        name = request.form["name"]
    except:
        return {"success": False,
                "msg": "Unable to retrieve all the data"}, 400
    
    tag = Tag.query.get(tagId)
    Tag.update(tag, name)
    return redirect("/tags")

@app.route("/tags/<int:tagId>/delete", methods=["POST"])
#@login_required
def delete_tag(tagId): 
    tag = Tag.query.get(tagId)
    Tag.delete(tag)
    return redirect ("/tags")

# ----------------------------------------------------------------------------------------------
#####################
# ? USER ENDPOINTS (ME & PROFILE)
#####################

"""
! Gets or Updates the current User's profile
* OvidioSantoro - 2022-03-03
"""
@app.route("/me", methods=["GET", "POST"])
@jwt_required()
def me():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
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
            faculty = data["faculty"]
            classes = data.getlist("classes")
        except: 
            return {"success": False,
                    "msg": "Unable to retrieve all the data"}, 400

        if not User.check_password(user.password, old_password):
            return {"success": False,
                    "msg": "Old password is not correct"}, 403

        if password != confirmation:
            return {"success": False,
                    "msg": "Password confirmation incorrect"}, 403
    

        """ Check that the unique properties are not already taken """
        if (username != user.username) and User.query.filter_by(username=username).count() != 0:
            return {"success": False,
                    "msg": f"Username {username} already in use"}, 403


        """ Register the user into the database """
        User.update(user, username, password, faculty, classes)

        return redirect("/me")


"""
! Retrieves the selected user's profile
* OvidioSantoro - 2022-02-24
"""
@app.route("/user/<int:userId>", methods=["GET"])
def userProfile(userId):
    user = User.query.get(userId)
    return jsonify(user.serialize())


"""
! Deletes the current User's profile
* OvidioSantoro - 2022-03-03
"""
@app.route("/me/delete", methods=["POST"])
def me_delete():
    #TODO: CURRENT USER
    User.delete(2)
    return jsonify("Goodbye, you will be missed :(")

# ----------------------------------------------------------------------------------------------

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3702))
    app.run(host='0.0.0.0', port=PORT, debug=False)
