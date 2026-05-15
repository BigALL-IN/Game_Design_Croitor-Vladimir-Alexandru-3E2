import random
from dataclasses import dataclass

from core.constants import NATIONS

FIRST_NAMES = [
    "Aleksei", "Marta", "Boris", "Irina", "Dmitri", "Katya",
    "Pavel",   "Nadia", "Viktor","Olga",  "Gregor", "Vera",
    "Ivan",    "Lena",  "Sergei","Anna",  "Nikolai","Tanya",
]
LAST_NAMES = [
    "Volkov",  "Petrov",  "Sokolov", "Morozov", "Kozlov",  "Novak",
    "Lebedev", "Smirnov", "Fedorov", "Orlov",   "Zhukov",  "Belov",
]
OCCUPATIONS = [
    "Engineer", "Teacher",    "Merchant", "Farmer",
    "Doctor",   "Laborer",    "Journalist","Accountant",
    "Diplomat", "Soldier",
]
EMPLOYERS = [
    "State Factory #7", "Collective Farm", "Ministry of Transport",
    "Kolechia Steel", "Obristan Oil Co.", "Antegria Textiles",
    "State Printing Office", "Ministry of Agriculture",
    "Border Logistics Corp.", "Republia Mining Co.",
]
PURPOSES = ["WORK", "VISIT", "TRANSIT", "IMMIGRATION", "DIPLOMATIC"]
DURATIONS = ["14 DAYS", "30 DAYS", "60 DAYS", "90 DAYS", "6 MONTHS"]

DETAINABLE_FLAWS = {
    "wrong_nation", "name_mismatch", "photo_mismatch",
    "wp_name_mismatch", "ep_nation_mismatch",
}

_FLAW_POOL = [
    ("none",                28),
    ("expired",             12),
    ("wrong_nation",        18),
    ("name_mismatch",       10),
    ("birth_mismatch",      10),
    ("photo_mismatch",      10),
    ("wp_name_mismatch",     6),
    ("wp_expired",           6),
    ("ep_nation_mismatch",   6),
    ("ep_expired",           6),
]

_DOC_FLAW_REQUIRES = {
    "wp_name_mismatch":   "work_permit",
    "wp_expired":         "work_permit",
    "ep_nation_mismatch": "entry_permit",
    "ep_expired":         "entry_permit",
}


def rnd_date(y0: int, y1: int) -> str:
    return f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.{random.randint(y0,y1)}"


@dataclass
class Person:
    first: str
    last:  str
    nation: str
    birth:  str
    sex:    str
    occupation: str
    passport_nation: str
    passport_expiry: str
    id_name:  str
    id_birth: str
    id_number: str
    face_index: int
    doc_index:  int
    should_approve: bool = True
    flaw: str = ""
    is_detainable: bool = False
    wp_name: str = ""
    wp_nation: str = ""
    wp_employer: str = ""
    wp_expiry: str = ""
    wp_number: str = ""
    ep_name: str = ""
    ep_nation: str = ""
    ep_purpose: str = ""
    ep_duration: str = ""
    ep_expiry: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"


def make_person(allowed_nations: set, required_docs: list | None = None) -> "Person":
    from core.assets import ASSETS

    if required_docs is None:
        required_docs = ["passport", "id"]

    first  = random.choice(FIRST_NAMES)
    last   = random.choice(LAST_NAMES)
    nation = random.choice(NATIONS)
    birth  = rnd_date(1920, 1960)
    sex    = random.choice(["M", "F"])
    occ    = random.choice(OCCUPATIONS)
    expiry = rnd_date(1983, 1995)
    id_number = f"{random.randint(100,999)}-{random.randint(10000,99999)}"

    pool = [(ft, w) for ft, w in _FLAW_POOL
            if ft not in _DOC_FLAW_REQUIRES
            or _DOC_FLAW_REQUIRES[ft] in required_docs]
    flaw_types, weights = zip(*pool)
    flaw_type = random.choices(flaw_types, weights=weights)[0]

    passport_nation = nation
    id_name         = f"{first} {last}"
    id_birth        = birth
    flaw_desc       = ""
    should_approve  = True

    full_name = f"{first} {last}"
    wp_name     = full_name
    wp_nation   = nation
    wp_employer = random.choice(EMPLOYERS)
    wp_expiry   = rnd_date(1983, 1995)
    wp_number   = f"WP-{random.randint(10000,99999)}"

    ep_name     = full_name
    ep_nation   = nation
    ep_purpose  = random.choice(PURPOSES)
    ep_duration = random.choice(DURATIONS)
    ep_expiry   = rnd_date(1983, 1995)

    if flaw_type == "expired":
        expiry        = rnd_date(1975, 1981)
        flaw_desc     = "Passport expired"
        should_approve = False

    elif flaw_type == "wrong_nation":
        passport_nation = random.choice([n for n in NATIONS if n != nation])
        flaw_desc       = "Nation mismatch"
        should_approve  = False

    elif flaw_type == "name_mismatch":
        id_name        = random.choice([n for n in FIRST_NAMES if n != first]) + f" {last}"
        flaw_desc      = "Name mismatch (ID vs Passport)"
        should_approve = False

    elif flaw_type == "birth_mismatch":
        id_birth = rnd_date(1920, 1960)
        while id_birth == birth:
            id_birth = rnd_date(1920, 1960)
        flaw_desc      = "Birth date mismatch"
        should_approve = False

    elif flaw_type == "photo_mismatch":
        flaw_desc      = "Photo does not match traveler"
        should_approve = False

    elif flaw_type == "wp_name_mismatch":
        wp_name        = random.choice([n for n in FIRST_NAMES if n != first]) + f" {last}"
        flaw_desc      = "Work permit name mismatch"
        should_approve = False

    elif flaw_type == "wp_expired":
        wp_expiry      = rnd_date(1975, 1981)
        flaw_desc      = "Work permit expired"
        should_approve = False

    elif flaw_type == "ep_nation_mismatch":
        ep_nation      = random.choice([n for n in NATIONS if n != nation])
        flaw_desc      = "Entry permit nation mismatch"
        should_approve = False

    elif flaw_type == "ep_expired":
        ep_expiry      = rnd_date(1975, 1981)
        flaw_desc      = "Entry permit expired"
        should_approve = False

    if flaw_type == "none" and nation not in allowed_nations:
        should_approve = False
        flaw_desc      = f"{nation} not permitted today"

    is_detainable = flaw_type in DETAINABLE_FLAWS

    face_index = ASSETS.random_face_index()
    doc_index  = (ASSETS.random_different_doc_index(face_index)
                  if flaw_type == "photo_mismatch" else face_index)

    return Person(
        first=first, last=last, nation=nation, birth=birth,
        sex=sex, occupation=occ,
        passport_nation=passport_nation, passport_expiry=expiry,
        id_name=id_name, id_birth=id_birth, id_number=id_number,
        face_index=face_index, doc_index=doc_index,
        should_approve=should_approve, flaw=flaw_desc,
        is_detainable=is_detainable,
        wp_name=wp_name, wp_nation=wp_nation, wp_employer=wp_employer,
        wp_expiry=wp_expiry, wp_number=wp_number,
        ep_name=ep_name, ep_nation=ep_nation, ep_purpose=ep_purpose,
        ep_duration=ep_duration, ep_expiry=ep_expiry,
    )