def is_instrumental(result):
    if result is None:
        return False

    return result.get("instrumental", False)
