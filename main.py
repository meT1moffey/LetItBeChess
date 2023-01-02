from client import *
from figures import *
from ai import *


SIZE = 60

board_layout = open('boards/standart.board', 'r').read().split('\n')
figs = {
    '.': EmptyTile,
    'p': Pawn,
    'r': Rook,
    'k': Knight,
    'b': Bishop,
    'Q': Queen,
    'K': King,
}


def main():
    board = [[figs[board_layout[y][x]](
        (lambda empty: None if empty else 'black' if y < len(board_layout) / 2 else 'white')(figs[tile] == EmptyTile),
        x, y, SIZE) for x, tile in enumerate(row)] for y, row in enumerate(board_layout)]
    Window(board, tile_size=SIZE, w_controller=HumanController, b_controller=RandomTurnController)


if __name__ == '__main__':
    main()
