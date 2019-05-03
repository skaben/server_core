from django import forms
from . import models

class PermissionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Permission
        fields = ['state_id']

class LogRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Log
        fields = ['timestamp','message']


class StateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.State
        fields = ['name', 'descr']


class ValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Value
        fields = ['value', 'comment']


class LockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Lock
        fields = ['descr', 'sound', 'blocked', 'opened', 'override', 'term_id']


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