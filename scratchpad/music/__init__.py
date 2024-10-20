durations = {
    'a': '2:50',
    'b': '3:12',
    'c': '4:0'
}
ranks = {
    'a': {
        'b': 0,
        'c': 0
    },
    'b': {
        'a': 0,
        'c': 0
    },
    'c': {
        'b': 0,
        'a': 0
    }
}

#--
from .music import Music
from .player import Player

#--
def create_app():
    app = Music()
    # -- initialize player
    Player(app)
    return app

