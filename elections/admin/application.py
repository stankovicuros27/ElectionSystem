from flask import Flask, request, Response, jsonify
from elections.configuration import Configuration
from elections.models import database, Participant, \
    Election, ElectionParticipant, Vote
from elections.roleDecorator import roleDecorator
from elections.utils import nameIsValid, emailIsValid, \
    passwordIsValid, jmbgIsValid, participantType, \
    isIndividual, validStartAndEndDates, electionsBetweenExists, \
    validParticipants

application = Flask(__name__)
application.config.from_object(Configuration)

@application.route("/", methods = ["GET"])
def index():
    return "Welcome to admin service!<br>" \
           "Available routes are:<br><br>" \
           " \"/createParticipant\",<br>" \
           " \"/getParticipants\",<br>" \
           " \"/createElection\",<br>" \
           " \"/getElections\",<br>" \
           " \"/getResults\"<br>" \

@application.route("/createParticipant", methods = ["POST"])
#@roleDecorator(role = "admin")
def createParticipant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", None)

    if len(name) == 0:
        return Response("Field name is missing.", status = 400)
    if individual is None:
        return Response("Field individual is missing.", status = 400)
    if not nameIsValid(name):
        return Response("Invalid name.", status = 400)

    participant = Participant( name=name, type = participantType(individual))
    database.session.add(participant)
    database.session.commit()

    return jsonify(id=participant.id), 200

@application.route("/getParticipants", methods = ["GET"])
#@roleDecorator(role = "admin")
def getParticipants():
    ret = []
    for participant in Participant.query.all():
        ret.append({
            'id': participant.id,
            'name': participant.name,
            'individual': isIndividual(participant.type)
        })

    return jsonify(participants = ret), 200

@application.route("/createElection", methods=["POST"])
#@roleDecorator(role = "admin")
def createElection():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", None)
    participants = request.json.get("participants", None)

    if len(start) == 0:
        return Response("Field name is missing.", status = 400)
    if len(end) == 0:
        return Response("Field name is missing.", status = 400)
    if individual is None or not isinstance(individual, bool):
        return Response("Field name is missing.", status = 400)
    if participants is None:
        return Response("Field name is missing.", status = 400)
    if not validStartAndEndDates(start, end) or electionsBetweenExists(start, end):
        return Response("Invalid date and time.", status = 400)
    if not validParticipants(participants):
        return Response("Invalid participant.", status=400)

    election = Election(
        start = start,
        end = end,
        type = participantType(individual)
    )
    database.session.add(election)
    database.session.commit()

    participantsNumbers = []
    nextParticipantNumber = 0
    for id in participants:
        nextParticipantNumber += 1
        participantsNumbers.append(nextParticipantNumber)
        electionParticipant = ElectionParticipant(
            electionId = election.id,
            participantId = id,
            participantNumber = nextParticipantNumber
        )
        database.session.add(electionParticipant)
        database.session.commit()

    return jsonify(pollNumbers = participantsNumbers), 200

@application.route("/getElections", methods=["GET"])
#@roleDecorator(role = "admin")
def getElections():
    elections = Election.query.all()
    return_elections_json_array = []
    for election in elections:
        return_elections_json_array.append({
            'id': election.id,
            'start': election.start,
            'end': election.end,
            'individual': isIndividual(election.type),
            'participants': [
                {
                    "id": participant.id,
                    "name": participant.name
                }
                for participant in election.participants]
        })
    return jsonify(elections = return_elections_json_array), 200

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug = True)