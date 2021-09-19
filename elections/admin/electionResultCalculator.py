def calculateIndividualElection(participantInfos, totalVotesOnElection):
    participantResults = []
    for key in participantInfos:
        participantResults.append(
            {
                "pollNumber": participantInfos[key]["pollNumber"],
                "name": participantInfos[key]["name"],
                "result": round(participantInfos[key]["totalVotes"] / totalVotesOnElection, 2)
                    if totalVotesOnElection != 0
                    else 0
            }
        )
    return participantResults

def calculatePartyElection(participantInfos, totalVotesOnElection):
    threshold = 0.05
    seatsLeft = 250
    underThreshold = []
    overThreshold = []
    for key in participantInfos:
        participantInfos[key]["seatsSoFar"] = 0
        if totalVotesOnElection != 0 and participantInfos[key]["totalVotes"] / totalVotesOnElection >= threshold:
            overThreshold.append(participantInfos[key])
        else:
            underThreshold.append(participantInfos[key])

    if len(overThreshold) > 0:
        while seatsLeft > 0:
            leadingParty = None
            maxQuof = -1
            for party in overThreshold:
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



