from src.com.oscarrtorres.gomokux.model.enums import State


class Player:
    def __init__(self, state):
        self.state = state
        if state == State.EMPTY:
            raise Exception("Invalid player state")
        self.color = state.name.lower()
