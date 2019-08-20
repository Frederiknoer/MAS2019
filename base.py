from pygridmas import Colors
from common import CompanyEntity, COMPANY, BASE, BASE_FULL, ORE_DELIVERY


class Base(CompanyEntity):
    color = Colors.BLUE
    group_ids = {BASE}
    cargo = 0

    def step(self):
        if self.cargo >= self.mp.C:
            self.emit_event(self.mp.I // 2, BASE_FULL, None, '{}{}'.format(COMPANY, self.company_id))

    def receive_event(self, event_type, data):
        if event_type == ORE_DELIVERY:
            self.cargo = min(self.cargo + data, self.mp.C)
