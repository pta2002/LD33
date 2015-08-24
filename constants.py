import random

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (127, 127, 127)

SCREEN_SIZE = (800, 600)
TITLE = "LD33"


def random_colour():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)