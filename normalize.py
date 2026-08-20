import re


TITLE_PATTERNS = [
    r"\s*\(feat\..*?\)",
    r"\s*\(ft\..*?\)",
    r"\s*\[feat\..*?\]",
    r"\s*\[ft\..*?\]",
    r"\s*\(remaster(?:ed)?(?:\s*\d{4})?\)",
    r"\s*\[remaster(?:ed)?(?:\s*\d{4})?\]",
    r"\s*\(radio edit\)",
    r"\s*\[radio edit\]",
    r"\s*\(explicit\)",
    r"\s*\[explicit\]",
]


def normalize(text):
    if not text:
        return text

    text = text.strip()

    for pattern in TITLE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.I)

    return re.sub(r"\s+", " ", text).strip()
