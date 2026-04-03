import pygame

import core.assets as _assets
from documents.base import DocumentTemplate, ClickableField

DOC_W = 280
DOC_H = 150

class PassportTemplate(DocumentTemplate):

    @property
    def source_id(self) -> str:
        return "passport"

    def build(self, person) -> tuple:
        surf = pygame.Surface((DOC_W, DOC_H))
        surf.fill((30, 60, 50))

        pygame.draw.rect(surf, (20, 45, 35), (0, 0, DOC_W, 30))
        self._text(surf, "PASSPORT",               "title", (180, 220, 170), DOC_W // 2, 8,  center=True)
        self._text(surf, person.passport_nation.upper(), "small", (150, 200, 140), DOC_W // 2, 24, center=True)
        pygame.draw.line(surf, (80, 120, 80), (0, 34), (DOC_W, 34), 1)

        photo_area = pygame.Rect(8, 40, 70, 85)
        photo = _assets.ASSETS.get_doc_photo(person.doc_index, (70, 85))
        surf.blit(photo, photo_area.topleft)
        pygame.draw.rect(surf, (80, 120, 80), photo_area, 1)

        field_defs = [
            ("pp_name",   "name",   "NAME",   f"{person.first} {person.last}"),
            ("pp_nation", "nation", "NATION", person.passport_nation),
            ("pp_born",   "birth",  "BORN",   person.birth),
            ("pp_sex",    "sex",    "SEX",    person.sex),
            ("pp_occ",    "",       "OCC",    person.occupation),
            ("pp_expiry", "expiry", "EXPIRY", person.passport_expiry),
        ]
        VALUE_X   = 88 + 60
        clickable = []
        for key, group, label, val in field_defs:
            y = 42 + len(clickable) * 14
            cf = self._field(
                surf, key, self.source_id, group,
                label, val, "small",
                (100, 160, 100), (220, 230, 200),
                88, VALUE_X, y,
            )
            clickable.append(cf)

        clickable.append(self._photo_field("pp_photo", self.source_id,
                                           person.doc_index, photo_area))

        pygame.draw.rect(surf, (80, 160, 80), (0, 0, DOC_W, DOC_H), 2)
        return surf, clickable