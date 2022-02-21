from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

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

LikedFiles = db.Table('liked_files',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('file_id', db.ForeignKey("file.id"), primary_key=True)
)

FavoriteColls = db.Table('favorite_colls',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('coll_id', db.ForeignKey("coll.id"), primary_key=True)
)

LikedColls = db.Table('liked_colls',
    db.Column('user_id', db.ForeignKey("user.id"), primary_key=True),
    db.Column('coll_id', db.ForeignKey("coll.id"), primary_key=True)
)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message #{self.id} from {self.sender} to {self.receiver}"

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
    faculties = db.relationship("Faculty", secondary=FacultyMembers, back_populates="students")
    classes = db.relationship("Class", secondary=ClassStudents, back_populates="students")
    fav_files = db.relationship("File", secondary=FavoriteFiles, back_populates="favs_files")
    like_files = db.relationship("File", secondary=LikedFiles, back_populates="liked_files")
    fav_colls = db.relationship("Coll", secondary=FavoriteColls, back_populates="favs_colls")
    like_colls = db.relationship("Coll", secondary=LikedColls, back_populates="liked_colls")
    files = db.relationship("File", back_populates="uploader")
    colls = db.relationship("Coll", back_populates="sender")
    comments = db.relationship("Comment", back_populates="commenter")
    """ TODO: SHOULD I USE A MIDDLE TABLE OR STORE IT AS A PICKLE? """
    # tags = db.Column(db.ARRAY(db.Integer())
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    description = db.Column(db.Text)
    biography = db.Column(db.Text)
    sent = db.relationship("Message", backref="message_sender", foreign_keys=Message.sender)
    received = db.relationship("Message", backref="message_receiver", foreign_keys=Message.receiver)
    networks = db.relationship("Network", backref="network_owner")

    def __repr__(self):
        return f"User {self.id}: {self.username}"

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
        return f"{self.owner}'s {self.name}: {self.link}"

    def serialize(self):
        return{
            "id": self.id,
            "owner": self.owner, 
            "name": self.name ,
            "link": self.link 
        }

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    """" TODO: THIS DEPENDS ON HOW I KEEP THE TAGS """
    # user = db.Column(db.Integer, ForeignKey("user.id"))
    name = db.Column(db.String(20))

    """ TODO: ADD REPR AND SERIALIZATION WHEN THE TABLE IS FINISHED """

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    faculties = db.relationship("Faculty", back_populates="college")

    def __repr__(self):
        return f"College #{self.id}: {self.name}"

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
        return f"{self.name} in {self.college}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "college": self.college_id
        }

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    faculty = db.relationship("Faculty", back_populates="classes")
    students = db.relationship("User", secondary=ClassStudents, back_populates="classes")
    files = db.relationship("File", back_populates="_class")
    colls = db.relationship("Coll", back_populates="_class")

    def __repr__(self):
        return f"{self.name} in {self.faculty.id}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculty": self.faculty_id
        }

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _class = db.relationship("Class", back_populates="files") 
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    uploader = db.relationship("User", back_populates="files")
    type = db.Column(db.String(12), nullable=False)
    favs_files = db.relationship("User", secondary=FavoriteFiles, back_populates="fav_files")
    liked_files = db.relationship("User", secondary=LikedFiles, back_populates="like_files")
    # TODO: Almacenamiento archivo

    # TODO: SERIALIZE AND REPR CORRECTLY
    def __repr__(self):
        return f"{self.name} in {self.faculty.id}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculty": self.faculty_id
        }

class Coll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sender = db.relationship("User", back_populates="colls")
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    _class = db.relationship("Class", back_populates="colls")
    type = db.Column(db.String(12), nullable=False)
    favs_colls = db.relationship("User", secondary=FavoriteColls, back_populates="fav_colls")
    liked_colls = db.relationship("User", secondary=LikedColls, back_populates="like_colls")
    comments = db.relationship("Comment", back_populates="coll")
    # TODO: Almacenamiento como HTML del contenido del Coll

    # TODO: SERIALIZE AND REPR CORRECTLY
    def __repr__(self):
        return f"{self.name} in {self.faculty.id}"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "faculty": self.faculty_id
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    commenter = db.relationship("User", back_populates="comments")
    coll_id = db.Column(db.Integer, db.ForeignKey("coll.id"))
    coll = db.relationship("Coll", back_populates="comments")
    content = db.Column(db.Text, nullable=False)

    # TODO: SERIALIZE AND REPR CORRECTLY