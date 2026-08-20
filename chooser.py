AUTO_SCORE = 90


def deduplicate(candidates):
    """
    Keep only the highest-scoring candidate for each
    (title, artist) pair.
    """

    best = {}

    for c in candidates:
        key = (
            c["title"].strip().lower(),
            c["artist"].strip().lower(),
        )

        if (
            key not in best
            or c["score"] > best[key]["score"]
        ):
            best[key] = c

    return sorted(
        best.values(),
        key=lambda x: x["score"],
        reverse=True,
    )


def choose(candidates, interactive=False):

    if not candidates:
        return None

    candidates = deduplicate(candidates)

    if len(candidates) == 1:
        return candidates[0]

    # Automatic mode
    if not interactive:

        if candidates[0]["score"] >= AUTO_SCORE:
            return candidates[0]

        return candidates[0]

    # Interactive mode

    print()

    for i, c in enumerate(candidates[:5], 1):

        stars = "★" * min(c["score"] // 20, 5)

        print(f"[{i}] {stars} ({c['score']})")
        print(c["title"])
        print(c["artist"])

        if c["album"]:
            print(f"Album: {c['album']}")

        print()

        preview = [
            line
            for line in c["lyrics"].splitlines()
            if line.strip()
        ][:3]

        for line in preview:
            print("♪", line)

        print()

    while True:

        choice = input(
            "Select [1-5] or q: "
        ).strip().lower()

        if choice == "q":
            return None

        if (
            choice.isdigit()
            and 1 <= int(choice) <= len(candidates[:5])
        ):
            return candidates[int(choice) - 1]

        print("Invalid selection.")
