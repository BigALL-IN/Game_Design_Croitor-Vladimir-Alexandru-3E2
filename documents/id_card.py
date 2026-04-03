import random

import pygame

import core.assets as _assets
from documents.base import DocumentTemplate, ClickableField

ID_DOC_W = 280
ID_DOC_H = 110


class IDCardTemplate(DocumentTemplate):

    @property
    def source_id(self) -> str:
        return "id"

    def build(self, person) -> tuple:
        surf = pygame.Surface((ID_DOC_W, ID_DOC_H))
        surf.fill((210, 195, 160))

        pygame.draw.rect(surf, (30, 60, 110), (0, 0, ID_DOC_W, 22))
        self._text(surf, "CITIZEN IDENTIFICATION CARD", "small", (180, 200, 240),
                   ID_DOC_W // 2, 5, center=True)

        photo_area = pygame.Rect(6, 28, 55, 70)
        photo = _assets.ASSETS.get_doc_photo(person.doc_index, (55, 70))
        surf.blit(photo, photo_area.topleft)
        pygame.draw.rect(surf, (100, 90, 70), photo_area, 1)

        field_defs = [
            ("id_name",   "name",   "NAME",   person.id_name),
            ("id_born",   "birth",  "BORN",   person.id_birth),
            ("id_sex",    "sex",    "SEX",    person.sex),
            ("id_number", "",       "NUMBER", person.id_number),
            ("id_nation", "nation", "NATION", person.nation),
        ]
        VALUE_X   = 70 + 58
        clickable = []
        for key, group, label, val in field_defs:
            y = 28 + len(clickable) * 14
            cf = self._field(
                surf, key, self.source_id, group,
                label, val, "small",
                (60, 50, 30), (20, 20, 10),
                70, VALUE_X, y,
            )
            clickable.append(cf)

        clickable.append(self._photo_field("id_photo", self.source_id,
                                           person.doc_index, photo_area))


        pygame.draw.rect(surf, (80, 70, 50), (0, 0, ID_DOC_W, ID_DOC_H), 2)
        return surf, clickable