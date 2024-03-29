from server.reactions.exceptions import StopReactionPipeline
from server.reactions.powerstate import apply_powerstate


def apply_pipeline(event_type: str, event_data: dict):
    """Базовый пайплайн обработки эвентов"""
    try:
        if event_type == 'device':
            apply_powerstate(event_data)
    except StopReactionPipeline as e:
        print(e)
