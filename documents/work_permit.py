import pygame

from documents.base import DocumentTemplate

WP_DOC_W = 260
WP_DOC_H = 130


class WorkPermitTemplate(DocumentTemplate):

    @property
    def source_id(self) -> str:
        return "work_permit"

    def build(self, person) -> tuple:
        surf = pygame.Surface((WP_DOC_W, WP_DOC_H))
        surf.fill((200, 185, 150))

        pygame.draw.rect(surf, (120, 90, 40), (0, 0, WP_DOC_W, 24))
        self._text(surf, "WORK PERMIT", "title", (240, 225, 180),
                   WP_DOC_W // 2, 4, center=True)
        pygame.draw.line(surf, (140, 110, 60), (0, 28), (WP_DOC_W, 28), 1)

        field_defs = [
            ("wp_name",     "name",   "NAME",      person.wp_name),
            ("wp_nation",   "nation", "NATION",    person.wp_nation),
            ("wp_employer", "",       "EMPLOYER",  person.wp_employer),
            ("wp_expiry",   "expiry", "VALID UNTIL", person.wp_expiry),
            ("wp_number",   "",       "PERMIT #",  person.wp_number),
        ]
        VALUE_X = 14 + 90
        clickable = []
        for key, group, label, val in field_defs:
            y = 34 + len(clickable) * 16
            cf = self._field(
                surf, key, self.source_id, group,
                label, val, "small",
                (90, 70, 30), (30, 20, 5),
                14, VALUE_X, y,
            )
            clickable.append(cf)

        pygame.draw.rect(surf, (140, 110, 50), (0, 0, WP_DOC_W, WP_DOC_H), 2)
        return surf, clickable
