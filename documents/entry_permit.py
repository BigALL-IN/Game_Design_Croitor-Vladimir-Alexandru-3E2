import pygame

from documents.base import DocumentTemplate

EP_DOC_W = 260
EP_DOC_H = 140


class EntryPermitTemplate(DocumentTemplate):

    @property
    def source_id(self) -> str:
        return "entry_permit"

    def build(self, person) -> tuple:
        surf = pygame.Surface((EP_DOC_W, EP_DOC_H))
        surf.fill((180, 210, 180))

        pygame.draw.rect(surf, (30, 80, 45), (0, 0, EP_DOC_W, 24))
        self._text(surf, "ENTRY PERMIT", "title", (180, 230, 180),
                   EP_DOC_W // 2, 4, center=True)
        pygame.draw.line(surf, (60, 120, 60), (0, 28), (EP_DOC_W, 28), 1)

        field_defs = [
            ("ep_name",     "name",   "NAME",      person.ep_name),
            ("ep_nation",   "nation", "NATION",    person.ep_nation),
            ("ep_purpose",  "",       "PURPOSE",   person.ep_purpose),
            ("ep_duration", "",       "DURATION",  person.ep_duration),
            ("ep_expiry",   "expiry", "VALID UNTIL", person.ep_expiry),
        ]
        VALUE_X = 14 + 90
        clickable = []
        for key, group, label, val in field_defs:
            y = 34 + len(clickable) * 16
            cf = self._field(
                surf, key, self.source_id, group,
                label, val, "small",
                (30, 70, 30), (10, 30, 10),
                14, VALUE_X, y,
            )
            clickable.append(cf)

        pygame.draw.rect(surf, (50, 110, 50), (0, 0, EP_DOC_W, EP_DOC_H), 2)
        return surf, clickable
