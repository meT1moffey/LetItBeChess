from client import Controller
import random


class RandomTurnController(Controller):
    def enable(self):
        if not self.all_moves():
            print("I'm lost :(")
            return

        selected_tile, possible_tiles = random.choice(self.all_moves())
        move_tile = random.choice(possible_tiles)

        self.win.make_turn(selected_tile, move_tile.x_pos, move_tile.y_pos)


class AiController(RandomTurnController):
    def enable(self):
        # Doing smth very smart
        pass