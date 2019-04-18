from django import forms
from sk_rest import models

from sk_rest.models import Lock
from sk_rest.serializers import LockSerializer

class LockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Lock
        fields = ['descr', 'sound', 'opened', 'override', 'term_id']


class TerminalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Terminal
        fields = ['descr',
                  'hacked',
                  'blocked',
                  'powered',
                  'hack_attempts',
                  'hack_wordcount',
                  'hack_length',
                  'menu_list',
                  'msg_body',
                  'msg_header',
                  'override']
