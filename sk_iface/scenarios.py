import logging
from sk_iface.state_manager import GlobalStateManager
from sk_iface.models import MenuItem

callbacks = MenuItem.objects.filter(callback__isnull=False).values('callback')

def parse_scenario(msg, dev):
    pl = dev.payload

    if not msg:
        return
    else:
        msg = msg.strip()

    if msg == 'passcode':
        return "!magos code activated!"

    if msg == 'alert':
        alert_value = pl.pop('level', None)
        if alert_value == 'reset':
            with GlobalStateManager() as manager:
                # only if in playable mode
                if manager.current in manager.playable:
                    manager.set_state('green', manual=True)
                    return 'ALERT LOWERED'
                else:
                    return 'TRYING TO LOWER ALERT IN NON-PLAYABLE MODE'
        message = pl.pop('comment', 'value changed')
        if not alert_value:
            msg = 'no alert level to change'
            logging.error(msg)
            return msg
        with GlobalStateManager() as manager:
            manager.change_value(alert_value,
                                 message)
        return f'{dev.dev_type}/{dev.uid} {message}'



