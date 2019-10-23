class Assembly:
    """Assembly abstract class"""
    payload = dict()

    def __init__(self):
        pass

    def get_payload(self, *args):
        """ Return JSON-compatible payload """
        if args:
            return [_ for _ in self.payload if _ in args]
        else:
            return self.payload
