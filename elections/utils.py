from re import match, search
import datetime
from email.utils import parseaddr
from models import Election, Participant
from sqlalchemy import and_, or_

def jmbgIsValid(jmbg):
    if len(jmbg) != 13:
        return False
    if match('^[0-9]{13}$', jmbg) is None:
        return False

    dd = int(jmbg[0:2])
    mm = int(jmbg[2:4])
    yyy = int(jmbg[4:7])
    rr = int(jmbg[7:9])
    k = int(jmbg[12:13])

    try:
        datetime.datetime(year = yyy, month = mm, day = dd)
    except ValueError:
        return False

    if rr < 70 or rr > 90:
        return False

    controlNum = 11 - \
       (7 * (int(jmbg[0]) + int(jmbg[6])) + \
       6 * (int(jmbg[1]) + int(jmbg[7])) + \
       5 * (int(jmbg[2]) + int(jmbg[8])) + \
       4 * (int(jmbg[3]) + int(jmbg[9])) + \
       3 * (int(jmbg[4]) + int(jmbg[10])) + \
       2 * (int(jmbg[5]) + int(jmbg[11]))) % 11

    if controlNum > 9:
        controlNum = 0

    if controlNum != k:
        return False

    return True

def emailIsValid(email):
    if len(email) == 0 or len(email) > 256:
        return False
    if len(parseaddr(email)) == 0:
        return False
    if match("[^@]+@[^@]+\.[^@]+", email) is None:
        return False

    return True

def passwordIsValid(password):
    if len(password) < 8 or len(password) > 256:
        return False
    if not search("[A-Z]", password):
        return False
    if not search("[a-z]", password):
        return False
    if not search("[0-9]", password):
        return False

    return True

def nameIsValid(name):
    if len(name) > 256 or len(name) == 0:
        return False

def participantType(individual):
    return "individual" if individual else "party"

def isIndividual(type):
    return type == "individual"

def validStartAndEndDates(start, end):
   return validIsoTime(start) and validIsoTime(end) and start <= end

def validIsoTime(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True

def electionsBetweenExists(start, end):
    collidingElectionNum = Election.query.filter(
        or_(
            and_(Election.start <= end, Election.start >= start),
            and_(Election.end <= end, Election.end >= start),
            and_(Election.start <= start, Election.end >= end)
        )
    ).count()

    return collidingElectionNum != 0

def validParticipants(participants, individual):
    if len(participants) < 2:
        return False
    for participantID in participants:
        participant = Participant.query.filter(Participant.id == participantID).first()
        if participant.type != participantType(individual):
            return False

    return True