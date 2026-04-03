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

_FLAW_POOL = [
    ("none",           40),
    ("expired",        12),
    ("wrong_nation",   18),
    ("name_mismatch",  10),
    ("birth_mismatch", 10),
    ("photo_mismatch", 10),
]


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

    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"


def make_person(allowed_nations: set) -> "Person":
    from core.assets import ASSETS

    first  = random.choice(FIRST_NAMES)
    last   = random.choice(LAST_NAMES)
    nation = random.choice(NATIONS)
    birth  = rnd_date(1920, 1960)
    sex    = random.choice(["M", "F"])
    occ    = random.choice(OCCUPATIONS)
    expiry = rnd_date(1983, 1995)
    id_number = f"{random.randint(100,999)}-{random.randint(10000,99999)}"

    flaw_types, weights = zip(*_FLAW_POOL)
    flaw_type = random.choices(flaw_types, weights=weights)[0]

    passport_nation = nation
    id_name         = f"{first} {last}"
    id_birth        = birth
    flaw_desc       = ""
    should_approve  = True

    if flaw_type == "expired":
        expiry        = rnd_date(1975, 1981)
        flaw_desc     = "Passport expired"
        should_approve = False

    elif flaw_type == "wrong_nation":
        passport_nation = random.choice([n for n in NATIONS if n != nation])
        flaw_desc       = "Nation mismatch"
        should_approve  = False

    elif flaw_type == "name_mismatch":
        id_name = [n for n in FIRST_NAMES if n != first]
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

    if flaw_type == "none" and nation not in allowed_nations:
        should_approve = False
        flaw_desc      = f"{nation} not permitted today"

    face_index = ASSETS.random_face_index()
    doc_index  = (ASSETS.random_different_doc_index(face_index) if flaw_type == "photo_mismatch" else face_index)

    return Person(
        first=first, last=last, nation=nation, birth=birth,
        sex=sex, occupation=occ,
        passport_nation=passport_nation, passport_expiry=expiry,
        id_name=id_name, id_birth=id_birth, id_number=id_number,
        face_index=face_index, doc_index=doc_index,
        should_approve=should_approve, flaw=flaw_desc,
    )