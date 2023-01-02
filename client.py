import tkinter as tk


class Window(tk.Frame):
    def __init__(self, board, tile_size, w_controller=None, b_controller=None, record_file=None, enabled=True):
        self.board = board
        self.width = len(board[0])
        self.height = len(board)

        self.color = 'white'
        self.tile_size = tile_size

        if enabled:
            self.root = tk.Tk()
            self.root.geometry("%dx%d" % (self.width * self.tile_size, self.height * self.tile_size))
            self.root.title("Let it be chess")
            self.root.images = []

            self.canvas = None

            self.init_board()
            self.render()

            self.controllers = {'white': w_controller(self, 'white'), 'black': b_controller(self, 'black')}
            self.controllers[self.color].enable()

            self.record_file = None
            if record_file:
                self.record_file = open('game_records/%s.game' % record_file, 'w')

            self.root.mainloop()

    def init_board(self):
        self.canvas = tk.Canvas(self.root, width=self.width * self.tile_size, height=self.height * self.tile_size)
        self.canvas.pack()

    def render(self):
        for y, row in enumerate(self.board):
            for x, figure in enumerate(row):
                figure.render(self)

    def make_turn(self, selected_tile, x_pos, y_pos):
        if self.record_file:
            self.record_file.write('%s%d-%s%d\n' % (
                chr(ord('a') + selected_tile.x_pos),
                8 - selected_tile.y_pos,
                chr(ord('a') + x_pos),
                8 - y_pos,
            ))


        selected_tile.move_to(x_pos, y_pos, self)
        self.color = (lambda: 'white' if self.color == 'black' else 'black')()
        self.controllers[self.color].enable()


class Controller:
    def __init__(self, win, color):
        self.color = color
        self.win = win

    def enable(self):
        pass

    def all_moves(self):
        figures = list()
        for row in self.win.board:
            for tile in row:
                if tile.color == self.color and tile.possible_tiles(self.win):
                    figures.append((tile, tile.possible_tiles(self.win)))

        return figures


class HumanController(Controller):
    def __init__(self, win, color):
        super(HumanController, self).__init__(win, color)

        self.possible_tiles = list()
        self.selected_tile = None

    def enable(self):
        self.win.canvas.bind('<Button-1>', self.show_turns)

    def show_turns(self, event):
        x_pos, y_pos = int(event.x) // self.win.tile_size, int(event.y) // self.win.tile_size

        # if clicked tile is possible
        if self.win.board[y_pos][x_pos] in self.possible_tiles:
            self.win.make_turn(self.selected_tile, x_pos, y_pos)

        # uncolor previous selected
        if self.selected_tile:
            self.win.canvas.itemconfig(self.selected_tile.tile, fill=self.selected_tile.tile_color())

        # uncolor previous possible
        for figure in self.possible_tiles:
            self.win.canvas.itemconfig(figure.tile, fill=figure.tile_color())
        self.possible_tiles.clear()

        if self.color == self.win.color:
            # color selected
            self.selected_tile = self.win.board[y_pos][x_pos]
            self.win.canvas.itemconfig(self.selected_tile.tile, fill='yellow')

            # color possible
            if self.selected_tile.color == self.color:
                self.possible_tiles = self.selected_tile.possible_tiles(self.win)
                for figure in self.possible_tiles:
                    self.win.canvas.itemconfig(figure.tile, fill='yellow')
