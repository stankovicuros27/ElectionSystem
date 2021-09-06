from flask import Flask, request, Response, jsonify
from elections.configuration import Configuration
from elections.models import database, Participant, \
    Election, ElectionParticipant, Vote
from elections.roleDecorator import roleDecorator
from elections.utils import nameIsValid, emailIsValid, \
    passwordIsValid, jmbgIsValid, participantType, \
    isIndividual, validStartAndEndDates, electionsBetweenExists, \
    validParticipants
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from redis import Redis
import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/vote", methods=["POST"])
#@jwt_required()
#@roleDecorator(role = "zvanicnik")
def vote():
    file = request.files.get("file", None)

    if file is None:
        return Response("Field file is missing.", status = 400)

    content = file.stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);

    lineCnt = 0
    for row in reader:
        if len(row) != 2:
            return Response(f"Incorrect number of values on line {lineCnt}.", status = 400)

        voteFor = int(row[1])
        if voteFor < 0:
            return Response(f"Incorrect poll number on line  {lineCnt}.", status = 400)

        lineCnt += 1


    #claims = get_jwt()
    #jmbg = claims.get("jmbg", "")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    for row in reader:
        with Redis(host = Configuration.REDIS_HOST) as redis:
            redis.rpush(
                Configuration.REDIS_LIST,
                row[0]+"#"+row[1]+"#"
            )
            print("ok")

    return Response(status=200)

if (__name__ == "__main__"):
    # database.init_app(application);
    application.run(debug = True)
