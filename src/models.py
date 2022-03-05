from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

"""
! Asociation tables for the Many-To-Many relationships
* OvidioSantoro - 2022-02-22
"""
FacultyMembers = db.Table('faculty_members',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('faculty_id', db.ForeignKey("faculty.id"), primary_key=True)
)

ClassStudents = db.Table('class_students',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('class_id', db.ForeignKey("class.id"), primary_key=True)
)

UserTags = db.Table('user_tags',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('tag_id', db.ForeignKey("tag.id"), primary_key=True)
)

FavoriteFiles = db.Table('favorite_files',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('file_id', db.ForeignKey("file.id"), primary_key=True)
)

FavoriteColls = db.Table('favorite_colls',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('coll_id', db.ForeignKey("coll.id"), primary_key=True)
)

# ----------------------------------------------------------------------------------------------

"""
! Asociation objects for the like tables
* OvidioSantoro - 2022-02-22
? Needed to handle the difference between like & dislike in one table
? in this case we use a Boolean (True = Like, False = Dislike)
"""
class LikedFiles(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    file_id = db.Column(db.ForeignKey("file.id"), primary_key=True)
    is_like = db.Column(db.Boolean, default=True)
    file_liker = db.relationship("User", back_populates="liked_files")
    liked_file = db.relationship("File", back_populates="file_liked")

    def __repr__(self):
        return f"{self.file_liker} like/dislike to {self.liked_file}"

    def serialize(self):
        return{
            "liker": self.file_liker,
            "liked": self.liked_file,
            "isLike": self.is_like,
        }
    
class LikedColls(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    coll_id = db.Column(db.ForeignKey("coll.id"), primary_key=True)
    is_like = db.Column(db.Boolean, default=True)
    coll_liker = db.relationship("User", back_populates="liked_colls")
    liked_coll = db.relationship("Coll", back_populates="coll_liked")

    def __repr__(self):
        return f"{self.coll_liker} like/dislike to {self.liked_coll}"

    def serialize(self):
        return{
            "liker": self.coll_liker,
            "liked": self.liked_coll,
            "isLike": self.is_like,
        }

# ----------------------------------------------------------------------------------------------

"""
! Message Model & methods
* OvidioSantoro - 2022-02-21
"""
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message #{self.id} from User #{self.sender} to User #{self.receiver}"

    def serialize(self):
        return{
            "id": self.id,
            "sender": User.query.get(self.sender).username,
            "receiver": User.query.get(self.receiver).username, 
            "content": self.content
        }


    # Creates a new message
    def newMessage(sender, receiver, content):
        message = Message(
            sender=sender,
            receiver=receiver, 
            content=content,
        )
        db.session.add(message)
        db.session.commit()

    # TODO: Add a way for a user to remove messages ONLY FOR HIMSELF
    """
    TODO: Decide whether a user should be able to edit or remove messages (à la WhatsApp)
        or if they should be "permanent" (like an email).
    """

    # Returns all messages received by the user
    def sentMessages(user_id):
        messages = Message.query.filter_by(sender=user_id)
        return messages

    # Returns all messages sent by the user
    def receivedMessages(user_id):
        messages = Message.query.filter_by(receiver=user_id)
        return messages

# ----------------------------------------------------------------------------------------------

"""
! User Model & methods
* OvidioSantoro - 2022-02-23
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    registered = db.Column(db.Date, default=datetime.date.today())
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    description = db.Column(db.Text)
    biography = db.Column(db.Text)
    faculties = db.relationship("Faculty", secondary=FacultyMembers, back_populates="students")
    classes = db.relationship("Class", secondary=ClassStudents, back_populates="students")
    tags = db.relationship("Tag", secondary=UserTags, back_populates="users")
    faved_files = db.relationship("File", secondary=FavoriteFiles, back_populates="file_faved")
    liked_files = db.relationship("LikedFiles", back_populates="file_liker")
    fav_colls = db.relationship("Coll", secondary=FavoriteColls, back_populates="favs_colls")
    liked_colls = db.relationship("LikedColls", back_populates="coll_liker")
    files = db.relationship("File", backref="uploader")
    colls = db.relationship("Coll", back_populates="sender")
    comments = db.relationship("Comment", back_populates="commenter")
    sent = db.relationship("Message", backref="message_sender", foreign_keys=Message.sender)
    received = db.relationship("Message", backref="message_receiver", foreign_keys=Message.receiver)
    networks = db.relationship("Network", backref="network_owner")

    def __repr__(self):
        return f"{self.username}"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "registered": self.registered,
            "faculties": list(map(lambda x: x.serialize(), self.faculties)),
            "tags": self.tags,
            "name": self.name,
            "surname": self.surname,
            "description": self.description,
            "biography": self.biography
        }


    # Checks the hashed password
    def check_password(userPassword, password):
        return check_password_hash(userPassword, password)

    # Register the user into the database
    def register(username, email, password, faculty, classes):
        user = User(
            username = username, 
            email = email, 
            password = generate_password_hash(password),
            faculties = [Faculty.query.get(faculty)],
            classes = [Class.query.get(_class) for _class in classes]
        )
        db.session.add(user)
        db.session.commit()

    # Updates the user's data in the database
    def update(id, username, password, faculty, classes):
        user = User.query.get(id)
        user.username = username
        user.password = generate_password_hash(password)
        user.faculties = [Faculty.query.get(faculty)]
        user.classes = [Class.query.get(_class) for _class in classes]

        db.session.commit()

    # Deletes an user from the database
    def delete(id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        
# ----------------------------------------------------------------------------------------------

"""
! Network Model & methods
* OvidioSantoro - 2022-02-23
"""
class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    link = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"User #{self.owner}'s {self.name}: {self.link}"

    def serialize(self):
        return{
            "id": self.id,
            "owner": self.owner, 
            "name": self.name ,
            "link": self.link 
        }


    # Creates a Network for the User
    def create(owner, name, link):
        network = Network(
            owner=owner, 
            name=name, 
            link=link
        )
        db.session.add(network)
        db.session.commit()

    # Updates user's network the database
    def update(user_id, username, password, faculty, classes):
        user = User.query.get(user_id)
        user.username = username
        user.password = generate_password_hash(password)
        user.faculties = [Faculty.query.get(faculty)]
        user.classes = [Class.query.get(_class) for _class in classes]
      
        db.session.commit()

    # Deletes a network from the database
    def delete(id):
        network = Network.query.get(id)
        db.session.delete(network)
        db.session.commit()

# ----------------------------------------------------------------------------------------------

"""
! Tag Model & methods
* OvidioSantoro - 2022-02-23
"""
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    users = db.relationship("User", secondary=UserTags, back_populates="tags")

    def __repr__(self):
        return f"Tag {self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name
        }


# ----------------------------------------------------------------------------------------------

"""
! College Model & methods
* OvidioSantoro - 2022-02-23
"""
class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    faculties = db.relationship("Faculty", back_populates="college")

    def __repr__(self):
        return f"{self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculties": [faculty.serialize() for faculty in self.faculties]
        }

# ----------------------------------------------------------------------------------------------

"""
! Faculty Model & methods
* OvidioSantoro - 2022-02-23
"""
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    students = db.relationship("User", secondary=FacultyMembers, back_populates="faculties")
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"), nullable=False)
    college = db.relationship("College", back_populates="faculties")
    classes = db.relationship("Class", back_populates="faculty")

    def __repr__(self):
        return f"{self.name} ({self.college})"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "college": College.query.get(self.college_id).name
        }

# ----------------------------------------------------------------------------------------------

"""
! Class Model & methods
* OvidioSantoro - 2022-02-23
"""
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"))
    faculty = db.relationship("Faculty", back_populates="classes")
    students = db.relationship("User", secondary=ClassStudents, back_populates="classes")
    files = db.relationship("File", back_populates="_class")
    colls = db.relationship("Coll", back_populates="_class")

    def __repr__(self):
        return f"{self.name} ({self.faculty})"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculty": Faculty.query.get(self.faculty_id).name,
            "students": [student.username for student in self.students]
        }

    # Updates the Class' students
    def update_students(id, students):
        _class = Class.query.get(id)
        _class.students = students
        db.session.commit()
        
# ----------------------------------------------------------------------------------------------

"""
! File Model & methods
* OvidioSantoro - 2022-02-23
"""
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    _class = db.relationship("Class", back_populates="files") 
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    type = db.Column(db.String(12), nullable=False)
    file_liked = db.relationship("LikedFiles", back_populates="liked_file")
    file_faved = db.relationship("User", secondary=FavoriteFiles, back_populates="faved_files")

    def __repr__(self):
        return f"<{self.title}> uploaded by {self.uploader} in {self._class}"

    def serialize(self):
        return{
            "id": self.id,
            "content": self.content,
            "uploader": self.uploader,
            "class": self._class
        }

# ----------------------------------------------------------------------------------------------        

"""
! Coll Model & methods
* OvidioSantoro - 2022-02-23
"""
class Coll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sender = db.relationship("User", back_populates="colls")
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    _class = db.relationship("Class", back_populates="colls")
    type = db.Column(db.String(12), nullable=False)
    favs_colls = db.relationship("User", secondary=FavoriteColls, back_populates="fav_colls")
    coll_liked = db.relationship("LikedColls", back_populates="liked_coll")
    comments = db.relationship("Comment", back_populates="coll")

    def __repr__(self):
        return f"{self.title} in {self._class}"

    def serialize(self):
        return{
            "id": self.id,
            "sender": User.query.get(self.sender_id).username,
            "title": self.title,
            "class": Class.query.get(self.class_id).name,
            "content": self.content
        }


    # Creates a new Coll
    def create(sender, title, content, _class, type):
        coll = Coll(
            sender_id = sender,
            title = title, 
            content = content, 
            class_id = _class,
            type = type
        )

        db.session.add(coll)
        db.session.commit()

    # Updates a Coll
    def update(coll, title, content):
        coll.title = title
        coll.content = content
        db.session.commit()

    # Deletes a Coll from the database
    def delete(coll):
        db.session.delete(coll)
        db.session.commit()

# ----------------------------------------------------------------------------------------------

"""
! Comment Model & methods
* OvidioSantoro - 2022-02-23
"""
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    commenter = db.relationship("User", back_populates="comments")
    coll_id = db.Column(db.Integer, db.ForeignKey("coll.id"))
    coll = db.relationship("Coll", back_populates="comments")

    def __repr__(self):
        return f"User #{self.commenter} commented in '{self.coll}'"

    def serialize(self):
        return{
            "id": self.id,
            "commenter": self.commenter,
            "coll": self.coll,
            "content": self.content
        }