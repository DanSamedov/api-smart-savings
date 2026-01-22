# app/core/utils/profanity_check.py

import asyncio
import re
import unicodedata
from functools import lru_cache

# English profanity
EN_PROFANITY = {
    "fuck",
    "shit",
    "bitch",
    "ass",
    "asshole",
    "dick",
    "cock",
    "pussy",
    "cunt",
    "whore",
    "slut",
    "porn",
    "sex",
    "nude",
    "faggot",
    "nigger",
    "retard",
    "penis",
}
# Spanish profanity
ES_PROFANITY = {
    "puta",
    "puto",
    "mierda",
    "joder",
    "coño",
    "polla",
    "verga",
    "culo",
    "zorra",
    "maricon",
    "porno",
    "pene",
}
# Polish profanity
PL_PROFANITY = {
    "kurwa",
    "chuj",
    "pizda",
    "jebac",
    "jebany",
    "dupa",
    "cipa",
    "pierdol",
    "porno",
    "pizda",
    "pizde",
    "pizdej",
    "pizdem",
    "pizdemu",
    "pizdemy",
}

PROFANE_WORDS = EN_PROFANITY | ES_PROFANITY | PL_PROFANITY

# Pre-compile the regex pattern (using substring matching)
PROFANE_RE = re.compile("|".join(re.escape(word) for word in PROFANE_WORDS))

# Translation table for leetspeak
LEET_MAP = str.maketrans(
    {"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"}
)

NON_LETTER_RE = re.compile(r"[^a-z]")
REPEAT_RE = re.compile(r"(.)\1{2,}")  # fffuck -> fuck


@lru_cache(maxsize=10_000)
def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = text.translate(LEET_MAP)
    text = REPEAT_RE.sub(r"\1", text)
    return NON_LETTER_RE.sub("", text)


def is_text_allowed(text: str) -> bool:
    clean = normalize(text)
    return not bool(PROFANE_RE.search(clean))


async def is_text_allowed_async(text: str) -> bool:
    """True async wrapper using a thread pool to avoid blocking the event loop."""
    return await asyncio.to_thread(is_text_allowed, text)
