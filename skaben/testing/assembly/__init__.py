class Assembly:
    """Assembly abstract class"""

    fields = list()
    payload = dict()

    def __init__(self, **kwargs):
        for key in self.fields:
            val = kwargs.get(key)
            if val:
                self.payload[key] = val

        self.__dict__.update(self.payload)

    def get_payload(self, field_list=None):
        """ Return JSON-compatible payload """
        if not field_list:
            return self.payload
        else:
            return {k: v for k, v in self.payload.items() if k in field_list}
