from flask import Flask, request, Response, jsonify
from redis import Redis
from elections.models import database, Election, Vote, Participant, ElectionParticipant
from elections.configuration import Configuration
from sqlalchemy import and_, or_
from dateutil.parser import parse

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)

with application.app_context() as context:
    with Redis(host = Configuration.REDIS_HOST) as redis:
        while True:
            while len(redis.lrange(Configuration.REDIS_LIST, 0, 0)) == 0:
                pass

            fields = redis.lpop(Configuration.REDIS_LIST).decode("utf-8").split(";")

            timestamp = fields[0]
            election = Election.query.filter(
                and_(
                    Election.start <= parse(timestamp),
                    Election.end >= parse(timestamp)
                )
            ).first()
            if not election:
                print(f"No ongoing election for timestamp: {timestamp}")
                continue

            guid = fields[2]
            voteFor = fields[3]
            duplicateVote = Vote.query.filter(Vote.guid == guid).first()
            if duplicateVote is not None:
                print(f"Duplicate vote for guid: {guid}")
                invalidVote = Vote (
                    jmbg = fields[1],
                    electionId = election.id,
                    voteFor = voteFor,
                    guid = guid,
                    invalid = "Duplicate ballot."
                )
                database.session.add(invalidVote)
                database.session.commit()
                continue

            guid = fields[2]
            voteFor = fields[3]
            electionParticipant = ElectionParticipant.query.filter(
                and_(
                    ElectionParticipant.electionId == election.id,
                    ElectionParticipant.participantNumber == voteFor
                )
            ).first()
            if not electionParticipant:
                print(f"Participant doesn't exist: {voteFor}")
                invalidVote = Vote(
                    jmbg=fields[1],
                    electionId=election.id,
                    voteFor=voteFor,
                    guid=guid,
                    invalid="Invalid poll number."
                )
                database.session.add(invalidVote)
                database.session.commit()
                continue

            validVote = Vote(
                jmbg = fields[1],
                electionId = election.id,
                voteFor = voteFor,
                guid = guid
            )
            database.session.add(validVote)
            database.session.commit()
