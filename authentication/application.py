from flask import Flask, request, Response, jsonify
from models import database, User, Role
from utils import jmbgIsValid, emailIsValid, passwordIsValid
from flask_jwt_extended import JWTManager, create_access_token, \
    create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from configuration import Configuration
from roleDecorator import roleDecorator
from display import displayBlueprint

application = Flask(__name__)
application.config.from_object(Configuration)
application.register_blueprint(displayBlueprint, url_prefix = "/display")

@application.route("/", methods=["GET"])
def index():
    return "Welcome to authentication service!<br>" \
           "Available routes are:<br><br>" \
           " \"/display\",<br>" \
           " \"/register\",<br>" \
           " \"/login\",<br>" \
           " \"/check\",<br>" \
           " \"/refresh\",<br>" \
           " \"/delete\"<br>"

@application.route("/register", methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    if len(jmbg) == 0:
        #return jsonify({'message': 'Field jmbg is missing.'}), 400;
        return Response("Field jmbg is missing.", status = 400)
    if len(email) == 0:
        return Response("Field email is missing.", status = 400)
    if len(password) == 0:
        return Response("Field password is missing.", status = 400)
    if len(forename) == 0:
        return Response("Field forename is missing.", status = 400)
    if len(surname) == 0:
        return Response("Field surname is missing.", status = 400)
    if not jmbgIsValid(jmbg):
        return Response("Invalid jmbg.", status = 400)
    if not emailIsValid(email):
        return Response("Invalid email.", status = 400)
    if not passwordIsValid(password):
        return Response("Invalid password.", status = 400)
    if User.query.filter(User.email == email).first() is not None:
        return Response("Email already exists.", status=400)

    try:
        user = User(
            jmbg = jmbg,
            email = email,
            password = password,
            forename = forename,
            surname = surname,
            roleId = Role.query.filter(
                Role.name == "zvanicnik"
            ).first().id
        )
        database.session.add(user)
        database.session.commit()
    except:
        #return jsonify({'message': 'JMBG already exists.'}), 400;
        return Response("JMBG already exists.")

    return Response(status = 200)

jwt = JWTManager(application)

@application.route ("/login", methods = ["POST"])
def login():
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    if len(email) == 0:
        return Response("Field email is missing.", status = 400)
    if len(password) == 0:
        return Response("Field password is missing.", status = 400)
    if not emailIsValid(email):
        return Response("Invalid email.", status = 400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        #return jsonify({'message': 'Invalid credentials.'}), 400;
        return Response ("Invalid credentials.", status = 400)

    additionalClaims = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role.name
    }

    return jsonify(
        accessToken = create_access_token (identity = user.email, additional_claims = additionalClaims),
        refreshToken = create_refresh_token (identity = user.email, additional_claims = additionalClaims)
    ), 200

@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid"

@application.route("/refresh", methods = ["POST"])
@jwt_required(refresh = True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "jmbg": refreshClaims["jmbg"],
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"]
    }

    return jsonify(
        accessToken = create_access_token (identity = identity, additional_claims = additionalClaims)
    ), 200

@application.route("/delete", methods=["POST"])
@roleDecorator(role = "admin")
def delete():
    email = request.json.get("email", "")

    if len(email) == 0:
        #return jsonify({'message': 'Field email is missing.'}), 400;
        return Response("Field email is missing.", status = 400)
    if not emailIsValid(email):
        return Response("Invalid email.", status = 400)

    user = User.query.filter(User.email == email).first()
    if not user:
        return Response("Unknown user.", status = 400)

    database.session.delete(user)
    database.session.commit()

    return Response(status = 200)

if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug = True, host = "0.0.0.0", port = 5002)