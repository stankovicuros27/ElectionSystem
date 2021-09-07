from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User (database.Model):
    __tablename__ = "users"
    jmbg = database.Column(database.String(13), primary_key = True)
    email = database.Column(database.String (256), nullable = False, unique = True)
    password = database.Column(database.String(256), nullable = False)
    forename = database.Column(database.String(256), nullable = False)
    surname = database.Column(database.String(256), nullable = False)
    roleId = database.Column(database.Integer, database.ForeignKey("roles.id"))
    role = database.relationship ("Role", back_populates = "users")

    def __repr__ ( self ):
        return f"{self.forename} {self.surname} {self.email} {self.jmbg} {self.role.name}"

    def json(self):
        return {
            "forename": self.forename,
            "surname": self.surname,
            "email": self.email,
            "role": self.role.name
        }


class Role (database.Model):
    __tablename__ = "roles"
    id = database.Column (database.Integer, primary_key = True)
    name = database.Column (database.String(256), nullable = False, unique = True)
    users = database.relationship("User", back_populates = "role")

    def __repr__ ( self ):
        return f"{self.name} {str(self.users)}"

    def json(self):
        return {
            "name": self.name,
            "users": self.users
        }
