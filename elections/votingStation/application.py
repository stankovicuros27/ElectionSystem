from flask import Flask, request, Response, jsonify
from elections.configuration import Configuration
from elections.roleDecorator import roleDecorator
from elections.utils import nameIsValid, emailIsValid, \
    passwordIsValid, jmbgIsValid
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from redis import Redis
import io
import csv
import datetime

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/vote", methods=["POST"])
@jwt_required()
@roleDecorator(role = "zvanicnik")
def vote():
    file = request.files.get("file", None)

    if file is None:
        #return jsonify(message='Field file is missing.'), 400;
        return Response("Field file is missing.", status = 400)

    fileData = file.stream.read().decode("utf-8")
    reader = csv.reader(io.StringIO(fileData))
    lineCnt = 0

    for row in reader:
        if len(row) != 2:
            #return jsonify(message="Incorrect number of values on line " + str(i) + "."), 400;
            return Response(f"Incorrect number of values on line {lineCnt}.", status = 400)

        voteFor = int(row[1])
        if voteFor < 0:
            return Response(f"Incorrect poll number on line  {lineCnt}.", status = 400)

        lineCnt += 1

    jmbg = get_jwt().get("jmbg", "")
    #if not jmbgIsValid(jmbg):
        #return Response("Invalid jmbg.", status = 400)

    time = datetime.datetime.now()

    reader = csv.reader(io.StringIO(fileData))
    lineCnt = 0

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for row in reader:
            vote = f"{time};{jmbg};{row[0]};{row[1]}"
            redis.rpush(
                Configuration.REDIS_LIST,
                vote
            )
            print(f"Pushed {lineCnt}. vote with value {vote}")
            lineCnt += 1

    return Response(status = 200)

if (__name__ == "__main__"):
    application.run(debug = True)
