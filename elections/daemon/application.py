from flask import Flask, request, Response, jsonify
from redis import Redis
from elections.models import database, Election, Vote, Participant, ElectionParticipant
from elections.configuration import Configuration
from sqlalchemy import and_, or_

with Redis(host = Configuration.REDIS_HOST) as redis:
    while True:
        while len(redis.lrange(Configuration.REDIS_LIST, 0, 0)) > 0:
            vote = redis.lpop(Configuration.REDIS_LIST).decode("utf-8")
            print(vote)

            fields = vote.split(";")

            timestamp = fields[0]
            election = Election.query.filter(
                and_(
                    Election.start <= timestamp,
                    Election.end >= timestamp
                )
            ).first()
            if not election:
                print(f"No ongoing election for time: {timestamp}")
                continue

            voteFor = int(fields[3])
            guid = fields[2]
            duplicateVote = Vote.query.filter(
                and_(
                    Vote.guid == guid,
                    Vote.electionId == election.id
                )
            ).first()
            if duplicateVote is not None:
                # TODO add duplicate vode with invalid field
                print(f"Duplicate vote for guid: {guid}")
                continue


            voteFor = fields[3]
            electionParticipant = ElectionParticipant.query.filter(
                and_(
                    ElectionParticipant.electionId == election.id,
                    ElectionParticipant.participantNumber == voteFor
                )
            ).first()
            if not electionParticipant:
                # TODO add invalid field
                print(f"Participant doesn't exist: {voteFor}")
                continue

            vote = Vote(
                jmbg = fields[1],
                electionId = election.id,
                voteFor = voteFor,
                guid = guid
            )

            database.session.add(vote)
            database.session.commit()
