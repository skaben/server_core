from tools_testing.helpers import gen_random_str
from tools_testing.assembly import Assembly


class MenuItem(Assembly):
    """Generate payload for Menu Item objects"""

    payload = dict()

    def __init__(self, **kwargs):
        self.payload['label'] = kwargs.get('label', gen_random_str())
        self.payload['action'] = kwargs.get('action', gen_random_str())
        self.payload['response'] = kwargs.get('response', gen_random_str())
        self.payload['access'] = kwargs.get('access', '10')

        super().__init__(**kwargs)

    def get_payload(self, field_list=None):
        """Call to super"""
        return super().get_payload(field_list)


def ingame_assembly(item_type, **kwargs):
    """Assembling ingame items"""
    _d = {
        'menu_item': MenuItem,
        'menu': MenuItem,
    }

    item = _d.get(item_type)(**kwargs)
    return item
