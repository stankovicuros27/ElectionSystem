def calculateIndividualElection(participantInfos, totalVotesOnElection):
    participantResults = []
    for participantInfo in participantInfos:
        participantResults.append(
            {
                "pollNumber": participantInfo["pollNumber"],
                "name": participantInfo["name"],
                "result": round(participantInfo["totalVotes"] / totalVotesOnElection, 2)
            }
        )
    return participantResults

#TODO
def calculatePartyElection(participantInfos, totalVotesOnElection):
    seatsLeft = 250
    return None
