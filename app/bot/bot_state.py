from enum import Enum, auto

class BotState(Enum):
    MAIN_MENU = auto()
    ASKING_LOCATION = auto()
    ASKING_RADIUS = auto()
    CHOOSING_CATEGORIES = auto()
    ENTERING_DATE_FROM = auto()
    ENTERING_DATE_TO = auto()