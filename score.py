def score(query, candidate):
    score = 0

    if query["title"].lower() == candidate["title"].lower():
        score += 50

    if query["artist"].lower() == candidate["artist"].lower():
        score += 40

    if query["duration"] and candidate["duration"]:
        diff = abs(query["duration"] - candidate["duration"])

        if diff <= 1:
            score += 20
        elif diff <= 3:
            score += 15
        elif diff <= 5:
            score += 10

    if query.get("album") and candidate.get("album"):
        if query["album"].lower() == candidate["album"].lower():
            score += 10

    title = candidate["title"].lower()

    if "live" in title:
        score -= 20

    if "karaoke" in title:
        score -= 15

    if "instrumental" in title:
        score -= 10

    return score
