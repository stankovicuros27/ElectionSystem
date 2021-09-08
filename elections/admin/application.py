from flask import Flask, request, Response, jsonify
from elections.configuration import Configuration
from elections.models import database, Participant, \
    Election, ElectionParticipant, Vote
from elections.roleDecorator import roleDecorator
from elections.utils import nameIsValid, emailIsValid, \
    passwordIsValid, jmbgIsValid, participantType, \
    isIndividual, validStartAndEndDates, electionsBetweenExists, \
    validParticipants
from flask_jwt_extended import JWTManager
from datetime import datetime
from electionResultCalculator import calculatePartyElection, calculateIndividualElection

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

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
@roleDecorator(role = "admin")
def createParticipant():
    name = request.json.get("name", "")
    individual = request.json.get("individual", None)

    if len(name) == 0:
        return Response("Field name is missing.", status = 400)
    if individual is None:
        return Response("Field individual is missing.", status = 400)
    if not nameIsValid(name):
        return Response("Invalid name.", status = 400)

    participant = Participant(name = name, type = participantType(individual))
    database.session.add(participant)
    database.session.commit()

    return jsonify(id = participant.id), 200

@application.route("/getParticipants", methods = ["GET"])
@roleDecorator(role = "admin")
def getParticipants():
    participantJsons = []
    for participant in Participant.query.all():
        participantJsons.append(participant.json())

    return jsonify(participants = participantJsons), 200

@application.route("/createElection", methods=["POST"])
@roleDecorator(role = "admin")
def createElection():
    start = request.json.get("start", "")
    end = request.json.get("end", "")
    individual = request.json.get("individual", None)
    participants = request.json.get("participants", None)

    if len(start) == 0:
        return Response("Field start is missing.", status = 400)
    if len(end) == 0:
        return Response("Field end is missing.", status = 400)
    if individual is None:
        return Response("Field individual is missing.", status = 400)
    if participants is None:
        return Response("Field participants is missing.", status = 400)
    if not validStartAndEndDates(start, end) or electionsBetweenExists(start, end):
        return Response("Invalid date and time.", status = 400)
    if not validParticipants(participants, individual):
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
@roleDecorator(role = "admin")
def getElections():
    electionJsons = []
    for election in Election.query.all():
        electionJsons.append(election.json())

    return jsonify(elections = electionJsons), 200


@application.route("/getResults", methods = ["GET"])
@roleCheck(role = "admin")
def getResults():
    id = request.args.get("id", None)

    if id is None:
        return jsonify(message="Field id is missing."), 400

    election = Election.query.filter(Election.id == int(id))
    if not election:
        return jsonify(message = "Election does not exist."), 400

    if election.end >= datetime.now().isoformat():
        return jsonify(message = "Election is ongoing."), 400

    invalidVotes = Vote.query.filter(
        and_(
            Vote.invalid != None,
            Vote.electionId == election.id
        )
    ).all()

    invalidVoteJsons = []
    for invalidVote in invalidVotes:
        invalidVoteJsons.append(invalidVote.json())

    totalVotesOnElection = 0
    participantInfos = {}
    for electionParticipant in ElectionParticipant.query.filter(ElectionParticipant.electionId == election.id):
        participantInfos[electionParticipant.participantNumber] = {
            "totalVotes" : Vote.query.filter(
                and_(
                    Vote.electionId == election.id,
                    Vote.voteFor == electionParticipant.participantNumber,
                    Vote.invalid == None
                )
            ),
            "name" : Participant.query.filter(electionParticipant.participantId == Participant.id).first().name,
            "pollNumber": electionParticipant.participantNumber
        }
        totalVotesOnElection += participantInfos[electionParticipant.participantNumber]["totalVotes"]

    participantResults = []
    if isIndividual(election.type):
        participantResults = calculateIndividualElection(participantInfos, totalVotesOnElection)
    else:
        participantResults = calculatePartyElection(participantInfos, totalVotesOnElection)

    return jsonify(participants = participantResults, invalidVotes = invalidVoteJsons), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug = True)