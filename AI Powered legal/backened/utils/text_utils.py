import re


def split_terms(terms: str) -> list[str]:

    return [
        item.strip(" -•\t")
        for item in re.split(
            r";|\n",
            terms or "",
        )
        if item.strip()
    ]


def sanitize_text(text: str) -> str:

    return (
        (text or "")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2022", "-")
        .replace("\x00", "")
        .strip()
    )