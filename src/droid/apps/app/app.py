from .base import AppBase


class App(AppBase):
    def on(self, event :str):
        """Capture a one-shot event"""
        self.logger.debug(event)

    def action(self, act :str):
        """Execute action <act>"""
        self.logger.debug(act)
