import logging
import json

from core.models import Lock, Terminal, Tamed, AlertState
from core.rabbit.main import send_plain

logger = logging.getLogger('skaben.main')

def hex_to_rgb(hex):
    if hex.startswith('#'):
        hex = hex[1:]
    hex = ''.join([h.lower() for h in hex])
    return ",".join([str(i) for i in bytes.fromhex(hex)])


class PolicyManager:
    """
        Reflect dungeon alert state to smart devices
    """

    def __init__(self):
        self.locks = Lock.objects.all()
        self.terms = Terminal.objects.all()
        self.tamed = Tamed.objects.all()

    def apply(self, level):
        """
            Changing global alert state
        """
        color = hex_to_rgb(level.bg_color)
        send_plain("RGB.ce436600", color)
#        try:
#            call = getattr(self, level.name)
#            if call and level.name != 'white':
#                # exclude all manual controlled device from updates
#                self.locks = self.locks.exclude(override=True)
#                self.terms = self.terms.exclude(override=True)
#        except Exception as e:
#            logger.error(f'{self} has no method for {level.name}\n{e}')
#            pass

    def white(self):
        """
            WHITE: dungeon reset to start position
            doors are open, terminals are unlocked, all IED defused
        """
        # self.locks.update(opened=True,
        #                   sound=False,
        #                   override=False,
        #                   blocked=False,
        #                   timer=10)
        # self.terms.update(powered=False,
        #                   override=False,
        #                   blocked=False,
        #                   hacked=False,
        #                   hack_difficulty=6,
        #                   hack_wordcount=16,
        #                   hack_chance=10,
        #                   hack_attempts=4)


    def blue(self):
        """
            BLUE: power-off status

            game starting, most doors are closed, power source disabled
        """
        # self.locks.update(opened=False,
        #                   sound=True,
        #                   blocked=False)
        # self.terms.update(powered=False,
        #                   blocked=False,
        #                   hacked=False)

    def cyan(self):
        """
            CYAN: emergency power mode

            players solving power source quest
        """
        # self.locks.update(opened=False,
        #                   sound=True,
        #                   blocked=False)
        # self.terms.update(powered=False,
        #                   blocked=False,
        #                   hacked=False)

    def green(self):
        """
            GREEN: normal mode

            power source enabled, alert level not increased
        """
        # self.locks.update(
        #     opened=False,
        #     sound=True,
        # )
        # self.terms.update(
        #     powered=True,
        #     blocked=False,
        #     hacked=False,
        #     hack_wordcount=16,
        #     hack_attempts=4,
        #     hack_difficulty=6
        # )

    def yellow(self):
        """
            YELLOW: alert level "warning"

            dungeon difficulty increased
        """
        # self.locks.update(
        #     opened=False,
        #     sound=True,
        # )
        # self.terms.update(
        #     powered=True,
        #     blocked=False,
        #     hacked=False,
        # )

    def red(self):
        """
            RED: alert level "danger"

            dungeon difficulty at maximum, most doors are locked
        """
        # self.locks.update(
        #     opened=False,
        #     sound=True,
        # )
        # self.terms.update(
        #     powered=True,
        #     blocked=False,
        #     hacked=False,
        # )

    def black(self):
        """
            BLACK: game over, manual control
        """
        # self.locks.update(
        #     opened=False,
        #     sound=True,
        #     blocked=True,
        # )
        # self.terms.update(
        #     powered=True,
        #     blocked=True,
        #     hacked=False,
        # )