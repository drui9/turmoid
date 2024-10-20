from .music import Music

# --
class Player:
    def __init__(self, app: Music) -> None:
        self.app = app
        self.app.on('start')
        return self.setup()


    # <> setup
    def setup(self):
        # --
        def started():
            # todo: load songs & rankings
            self.app.emiter.on('play', song=self.app.next())
        # --
        def play(song):
            name, time = song
            self.app.playing = name
            self.app.duration = time
            print(f'playing: {name}, duration: {time}')
            self.app.emiter.on('shutdown')
        # --
        def ended():
            curr = self.app.playing
            print(f'[ended] name: {curr}')
        # --
        def pause():
            curr = self.app.playing
            time = self.app.duration
            print(f'[paused] curr: {curr}, at: {time}')
        # --
        def next():
            curr = self.app.playing
            time = self.app.duration
            print(f'[next] prev: {curr}, at: {time}')
        # --
        def prev():
            curr = self.app.playing
            time = self.app.duration
            print(f'[prev] curr: {curr}, at: {time}')
        # --
        def shutdown():
            print(self.app.played)
            print(self.app.ranks)
            self.app.terminate.set()
        # --
        self.app.emiter.link(shutdown, 'shutdown')
        self.app.emiter.link(started, 'start')
        self.app.emiter.link(pause, 'pause')
        self.app.emiter.link(ended, 'ended')
        self.app.emiter.link(play, 'play')
        self.app.emiter.link(prev, 'prev')
        self.app.emiter.link(next, 'next')
    # </>

