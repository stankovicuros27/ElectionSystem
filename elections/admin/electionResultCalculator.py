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

def calculatePartyElection(participantInfos, totalVotesOnElection):
    threshold = 0.05
    seatsLeft = 250
    underThreshold = []
    overThreshold = []
    for participantInfo in participantInfos:
        participantInfo["seatsSoFar"] = 0
        if participantInfo["totalVotes"] / totalVotesOnElection >= threshold:
            overThreshold.append(participantInfo)
        else:
            underThreshold.append(participantInfo)

    while seatsLeft > 0:
        leadingParty = None
        maxQuof = 0
        for party in overLine:
            if party["totalVotes"] / (party["seatsSoFar"] + 1) > maxQuof:
                maxQuof = party["totalVotes"] / (party["seatsSoFar"] + 1)
                leadingParty = party

        leadingParty["seatsSoFar"] += 1
        seatsLeft -= 1

    participantResults = []
    for participantInfo in [*overThreshold, *underThreshold]:
        participantResults.append(
            {
                "pollNumber": participantInfo["pollNumber"],
                "name": participantInfo["name"],
                "result": participantInfo["seatsSoFar"]
            }
        )
    return participantResults



