from flask_sqlalchemy import SQLAlchemy
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

"""
! Asociation object for the like tables
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

"""
! Data Models
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
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=False, nullable=False)
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
            "faculties": self.faculties,
            "tags": self.tags,
            "name": self.name,
            "surname": self.surname,
            "description": self.description,
            "biography": self.biography
        }

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

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    faculties = db.relationship("Faculty", back_populates="college")

    def __repr__(self):
        return f"{self.name}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name
        }

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    students = db.relationship("User", secondary=FacultyMembers, back_populates="faculties")
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"), nullable=False)
    college = db.relationship("College", back_populates="faculties")
    classes = db.relationship("Class", back_populates="faculty")

    def __repr__(self):
        return f"{self.name} from {self.college}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "college": self.college_id
        }

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"))
    faculty = db.relationship("Faculty", back_populates="classes")
    students = db.relationship("User", secondary=ClassStudents, back_populates="classes")
    files = db.relationship("File", back_populates="_class")
    colls = db.relationship("Coll", back_populates="_class")

    def __repr__(self):
        return f"{self.name} in {self.faculty}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculty": self.faculty_id
        }

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
            "title": self.title,
            "class": self._class
        }

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