from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

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
        return f"{self.file_liker}"

    def serialize(self):
        return{
            "liker": self.file_liker,
            "liked": self.liked_file,
            "isLike": self.is_like,
        }
    
class LikedColls(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    coll_id = db.Column(db.ForeignKey("coll.id"), primary_key=True)
    is_like = db.Column(db.Boolean)
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

    def create(user, coll, like):
        likedColl = LikedColls(
            user_id = user,
            coll_id = coll,
            is_like = like,
            coll_liker = User.query.get(user),
            liked_coll = Coll.query.get(coll)
        )
        db.session.add(likedColl)
        db.session.commit()
        return likedColl

    def update(likedColl, like):
        likedColl.is_like = like
        db.session.commit()

    def delete(likedColl):
        db.session.delete(likedColl)
        db.session.commit()
        

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
    timestamp = db.Column(db.DateTime, default=datetime.now())


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
    def create(sender, receiver, content):
        message = Message(
            sender = sender,
            receiver = receiver, 
            content = content,
        )
        db.session.add(message)
        db.session.commit()

    # Updates a message in the database
    def update(message, content):
        message.content = content
        db.session.commit()

    # Deletes a message from the database
    def delete(message):
        db.session.delete(message)
        db.session.commit()

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
    portrait = db.Column(db.String(300), default="https://i.pravatar.cc/300")
    registered = db.Column(db.Date, default=date.today())
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    description = db.Column(db.Text)
    biography = db.Column(db.Text)
    faculties = db.relationship("Faculty", secondary=FacultyMembers, back_populates="students")
    classes = db.relationship("Class", secondary=ClassStudents, back_populates="students")
    tags = db.relationship("Tag", back_populates="user")
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
            "portrait": self.portrait,
            "email": self.email,
            "classes": list(map(lambda x: x.serialize(), self.classes)),
            "registered": self.registered,
            "faculties": list(map(lambda x: x.serialize(), self.faculties)),
            "tags": list(map(lambda x: x.serialize(), self.tags)),
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
        return user

    # Updates the user's data in the database
    def update(user, username, password, faculty, classes):
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
            "owner": User.query.get(self.owner).username, 
            "name": self.name,
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

    # Updates a network the database
    def update(network, name, link):
        network.name = name
        network.link = link
      
        db.session.commit()

    # Deletes a network from the database
    def delete(network):
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
    user = db.relationship("User", back_populates="tags")
    user_id =  db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Tag {self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name
        }

    # Creates a new Tag
    def create(name, user):
        tag = Tag(
            name = name,
            user = user, 
        )

        db.session.add(tag)
        db.session.commit()

    # Updates a Tag
    def update(tag, name):
        tag.name = name
        db.session.commit()

    # Deletes a Tag from the database
    def delete(tag):
        db.session.delete(tag)
        db.session.commit()

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
    timestamp = db.Column(db.DateTime, default=datetime.now())


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
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"{self.title} in {self._class}"

    def serialize(self):
        return{
            "id": self.id,
            "portrait": User.query.get(self.sender_id).portrait,
            "sender": User.query.get(self.sender_id).username,
            "class": Class.query.get(self.class_id).name,
            "studies": [faculty.name for faculty in User.query.get(self.sender_id).faculties],
            "timestamp": f"{self.timestamp.strftime('%x, %X')}",
            "title": self.title,
            "likes": [{like.coll_liker.username: like.is_like} for like in LikedColls.query.filter_by(coll_id=self.id)],
            "content": self.content,
            "comments": [comment.content for comment in self.comments],
            "favs": [fav.username for fav in self.favs_colls],
            "type": self.type
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

    # Favs a Coll
    def fav(coll, user):
        favs = coll.favs_colls
        favs.append(user)
        coll.favs_colls = favs
        db.session.commit()

    # Favs a Coll
    def unfav(coll, user):
        favs = coll.favs_colls
        favs.remove(user)
        coll.favs_colls = favs
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
    timestamp = db.Column(db.DateTime, default=datetime.now())


    def __repr__(self):
        return f"User #{self.commenter} commented in '{self.coll}'"

    def serialize(self):
        return{
            "id": self.id,
            "commenter": self.commenter,
            "coll": self.coll,
            "content": self.content
        }