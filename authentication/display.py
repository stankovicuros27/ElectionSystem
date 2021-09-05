from flask import Blueprint
from models import User, Role

displayBlueprint = Blueprint("display", __name__)

@displayBlueprint.route("/", methods = ["GET"])
def index():
    return "Welcome to authentication display blueprint!<br>" \
           "Available routes are:<br><br>" \
           " \"/users\",<br>" \
           " \"/roles\"<br>"

@displayBlueprint.route("/users", methods = ["GET"])
def displayUsers():
    return str(User.query.all())

@displayBlueprint.route("/roles", methods = ["GET"])
def displayRoles():
    return str(Role.query.all())