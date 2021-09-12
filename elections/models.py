from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

def isIndividual(type):
    return type == "individual"

class ElectionParticipant(database.Model):
    __tablename__ = "electionparticipants"
    id = database.Column(database.Integer, primary_key = True)
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable = False)
    participantId = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable = False)
    participantNumber = database.Column(database.Integer, nullable = False)

class Participant(database.Model):
    __tablename__ = "participants"
    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(256), nullable = False)
    type = database.Column(database.String(256), nullable = False)
    elections = database.relationship("Election",
                                      secondary = ElectionParticipant.__table__,
                                      back_populates = "participants")

    def __repr__(self):
        return f"{self.name} {self.id} {self.type}"

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "individual": isIndividual(self.type)
        }

    def jsonForElection(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Election(database.Model):
    __tablename__ = "elections"
    id = database.Column(database.Integer, primary_key = True)
    start = database.Column(database.DateTime, nullable = False)
    end = database.Column(database.DateTime, nullable = False)
    type = database.Column(database.String(256), nullable = False)
    votes = database.relationship("Vote", back_populates = "election")
    participants = database.relationship("Participant",
                                         secondary = ElectionParticipant.__table__,
                                         back_populates = "elections")

    def __repr__(self):
        return f"{self.id} {self.type} {self.start} {self.end}"

    def json(self):
        participantsJsons = []
        for participant in self.participants:
            participantsJsons.append(participant.jsonForElection())
        return {
            "id": self.id,
            "start": str(self.start),
            "end": str(self.end),
            "individual": isIndividual(self.type),
            "participants": participantsJsons
        }

class Vote(database.Model):
    __tablename__ = "votes"
    id = database.Column(database.Integer, primary_key = True)
    guid = database.Column(database.String(36), nullable = False)
    electionId = database.Column(database.Integer, database.ForeignKey('elections.id'), nullable = False)
    jmbg = database.Column(database.String(13), nullable = False)
    voteFor = database.Column(database.Integer, nullable = False)
    election = database.relationship("Election", back_populates = "votes")
    invalid = database.Column(database.String(256), nullable = True)

    def __repr__(self):
        return f"{self.guid} {self.jmbg} {self.election} {self.voteFor}"

    def json(self):
        return {
            "ballotGuid": self.guid,
            "electionOfficialJmbg": self.jmbg,
            "reason": self.invalid,
            "pollNumber": self.voteFor
        }

