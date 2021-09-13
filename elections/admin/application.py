from flask import Flask, request, jsonify
from configuration import Configuration
from models import database, Participant, \
    Election, ElectionParticipant, Vote
from roleDecorator import roleDecorator
from utils import participantType, \
    isIndividual, validStartAndEndDates, electionsBetweenExists, \
    validParticipants
from flask_jwt_extended import JWTManager
from datetime import datetime
from electionResultCalculator import calculatePartyElection, calculateIndividualElection
from sqlalchemy import and_
from dateutil.parser import parse

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
        return jsonify(message = "Field name is missing."), 400
    if individual is None:
        return jsonify(message = "Field individual is missing."), 400
    #if not nameIsValid(name):
    #    return jsonify(message = "Invalid name."), 400

    participant = Participant(
        name = name,
        type = participantType(individual)
    )
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
        return jsonify(message = "Field start is missing."), 400
    if len(end) == 0:
        return jsonify(message = "Field end is missing."), 400
    if individual is None:
        return jsonify(message = "Field individual is missing."), 400
    if participants is None:
        return jsonify(message = "Field participants is missing."), 400
    if not validStartAndEndDates(start, end) or electionsBetweenExists(start, end):
        return jsonify(message = "Invalid date and time."), 400
    if not validParticipants(participants, individual):
        return jsonify(message = "Invalid participants."), 400

    start = parse(str(start))
    end = parse(str(end))

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
@roleDecorator(role = "admin")
def getResults():
    id = request.args.get("id", None)

    if id is None:
        return jsonify(message = "Field id is missing."), 400

    election = Election.query.filter(Election.id == int(id)).first()
    if not election:
        return jsonify(message = "Election does not exist."), 400

    if election.end >= parse(str(datetime.now())):
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
            ).count(),
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
    application.run(debug = True, host = "0.0.0.0", port = 5001)