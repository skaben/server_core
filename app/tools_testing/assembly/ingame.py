from tools_testing.helpers import gen_random_str
from tools_testing.assembly import Assembly


class MenuItem(Assembly):
    """Generate payload for Menu Item objects"""

    payload = dict()

    def __init__(self, **kwargs):
        self.payload['descr'] = kwargs.get('descr', gen_random_str())
        self.payload['action'] = kwargs.get('action', gen_random_str())
        self.payload['callback'] = kwargs.get('callback', gen_random_str())

    def get_payload(self, *args):
        """Call to super"""
        return super().get_payload(*args)


def ingame_assembly(item_type, **kwargs):
    """Assembling ingame items"""
    _d = {
        'menu_item': MenuItem,
        'menu': MenuItem,
    }

    item = _d.get(item_type)(**kwargs)
    return item
