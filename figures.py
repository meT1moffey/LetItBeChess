from PIL import ImageTk, Image


class EmptyTile:
    def __init__(self, color, x_pos, y_pos, size):
        self.color = color
        self.sprite = None
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.size = size
        self.tile = None
        self.has_moved = False

        self.tile_color = (lambda: 'white' if (self.x_pos + self.y_pos) % 2 == 0 else 'green')

    def render(self, client):
        self.destroy(client)
        self.tile = client.canvas.create_rectangle(self.x_pos * self.size, self.y_pos * self.size,
                                                   (self.x_pos + 1) * self.size, (self.y_pos + 1) * self.size,
                                                   fill=self.tile_color()
                                                   )

        if textures[type(self)]:
            raw_image = Image.open(textures[type(self)] % self.color).convert('RGBA')
            raw_image = raw_image.resize((self.size, self.size))

            client.root.images.append(None)
            client.root.images[-1] = image = ImageTk.PhotoImage(raw_image)

            self.sprite = client.canvas.create_image((self.x_pos + 0.5) * self.size, (self.y_pos + 0.5) * self.size,
                                                     image=image)

    def destroy(self, client):
        client.canvas.delete(self.tile)
        client.canvas.delete(self.sprite)

    def move_to(self, x_pos, y_pos, client, render=True):

        prev_x, prev_y = self.x_pos, self.y_pos
        client.board[prev_y][prev_x] = EmptyTile(None, prev_x, prev_y, self.size)
        client.board[y_pos][x_pos] = self

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.has_moved = True

        if render:
            client.board[prev_y][prev_x].render(client)
            self.render(client)

    def possible_tiles(self, client, ignore_safety=False):
        return list()

    def opposite_color(self):
        if self.color == 'white':
            return 'black'
        else:
            return 'white'

    def is_move_safe(self, client, pos):
        after_b = [[type(f)(f.color, f.x_pos, f.y_pos, f.size) for f in r] for r in client.board]
        after_c = type(client)(after_b, client.size, enabled=False)

        # else function checks current situation
        if pos:
            x_pos, y_pos = pos
            after_b[self.y_pos][self.x_pos].move_to(x_pos, y_pos, after_c, render=False)

        for row in after_b:
            for tile in row:
                if tile.color != self.opposite_color():
                    continue

                if King in [type(t) for t in tile.possible_tiles(after_c, ignore_safety=True)]:
                    return False

        return True

    def point_possible(self, client, rel_poses, ignore_safety, possibility='a'):
        # c - capture only; m - move only; a - any
        tiles = list()

        for rel_pos in rel_poses:
            x_pos = self.x_pos + rel_pos[0]
            y_pos = self.y_pos + rel_pos[1]
            if (x_pos in range(len(client.board[0]))) and (y_pos in range(len(client.board))):
                if (type(client.board[y_pos][x_pos]) == EmptyTile and possibility != 'c') \
                        or (client.board[y_pos][x_pos].color == self.opposite_color() and possibility != 'm'):
                    if ignore_safety or self.is_move_safe(client, (x_pos, y_pos)):
                        tiles.append(client.board[y_pos][x_pos])

        return tiles

    def ray_possible(self, client, rays, ignore_safety):
        # u - up; d - down; r - right; l - left
        # diagonal set by 2, for example ur (or ru) is right & up
        x_add = {'u': 0, 'd': 0, 'r': 1, 'l': -1}
        y_add = {'u': -1, 'd': 1, 'r': 0, 'l': 0}
        tiles = list()

        for ray in rays:
            x_pos = self.x_pos
            y_pos = self.y_pos

            for d in ray:
                x_pos += x_add[d]
                y_pos += y_add[d]

            while x_pos in range(len(client.board[0])) and y_pos in range(len(client.board)):
                if client.board[y_pos][x_pos].color == self.color:
                    break

                if ignore_safety or self.is_move_safe(client, (x_pos, y_pos)):
                    tiles.append(client.board[y_pos][x_pos])

                if type(client.board[y_pos][x_pos]) != EmptyTile:
                    break

                for d in ray:
                    x_pos += x_add[d]
                    y_pos += y_add[d]

        return tiles


class Pawn(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        tiles = list()
        if self.color == 'white':
            direction = -1
        else:
            direction = 1

        # forward
        tiles += self.point_possible(client, [(0, direction)], ignore_safety, possibility='m')
        # forward by 2
        if not self.has_moved:
            tiles += self.point_possible(client, [(0, 2 * direction)], ignore_safety, possibility='m')

        # forward & left/right capture
        tiles += self.point_possible(client, [(-1, direction), (1, direction)], ignore_safety, possibility='c')

        return tiles

    def transform(self, selected_id, client, win):
        selected = list(textures.keys())[selected_id + 2]
        client.board[self.y_pos][self.x_pos] = selected(self.color, self.x_pos, self.y_pos, self.size)
        client.board[self.y_pos][self.x_pos].render(client)
        win.destroy()

    def show_transforms(self, client):
        import tkinter as tk
        from tkinter import ttk
        from functools import partial

        win = tk.Toplevel()
        win.geometry('%dx%d' % (self.size * (len(textures.keys()) - 2), self.size * 1.25))

        selection_buttons = dict()

        for fig_id, fig in enumerate(list(textures.keys())[2:-1]):
            raw_image = Image.open(textures[fig] % self.color).convert('RGBA')
            raw_image = raw_image.resize((self.size, self.size))

            image = ImageTk.PhotoImage(raw_image)

            selection_buttons[fig] = ttk.Button(win, image=image, command=
                                                partial(self.transform, fig_id, client, win))
            selection_buttons[fig].image = image

            selection_buttons[fig].grid(column=fig_id, row=0)

        win.grab_set()

    def move_to(self, x_pos, y_pos, client, render=True):
        super(Pawn, self).move_to(x_pos, y_pos, client, render)

        if render:
            if self.color == 'white' and y_pos == 0\
                    or self.color == 'black' and y_pos == len(client.board[0]) - 1:
                self.show_transforms(client)


class Rook(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        return self.ray_possible(client, ['u', 'd', 'r', 'l'], ignore_safety)


class Knight(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        return self.point_possible(client, [
            (1, -2),
            (2, -1),
            (2, 1),
            (1, 2),
            (-1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
        ], ignore_safety)


class Bishop(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        return self.ray_possible(client, ['ur', 'ul', 'dr', 'dl'], ignore_safety)


class Queen(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        return self.ray_possible(client, ['u', 'd', 'r', 'l', 'ur', 'ul', 'dr', 'dl'], ignore_safety)


class King(EmptyTile):
    def possible_tiles(self, client, ignore_safety=False):
        tiles = list()

        # roque
        if not self.has_moved and not ignore_safety and self.is_move_safe(client, None):
            rook = client.board[self.y_pos][0]
            if type(rook) == Rook and not rook.has_moved\
                    and not (False in [type(fig) == EmptyTile for fig in client.board[self.y_pos][1:self.x_pos]]) \
                    and not (False in [self.is_move_safe(client, (x + self.x_pos, self.y_pos)) for x in range(-2, 0)]):
                # figure is rook, it hasn't moved, path is clear, doesn't give/take check
                tiles += self.point_possible(client, [(-2, 0)], ignore_safety)

            rook = client.board[self.y_pos][-1]
            if type(rook) == Rook and not rook.has_moved\
                    and not (False in [type(fig) == EmptyTile for fig in client.board[self.y_pos][self.x_pos + 1:-1]])\
                    and not (False in [self.is_move_safe(client, (x + self.x_pos, self.y_pos)) for x in range(1, 3)]):
                # figure is rook, it hasn't moved, path is clear, doesn't give/take check
                tiles += self.point_possible(client, [(2, 0)], ignore_safety)

        tiles += self.point_possible(client, [
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
        ], ignore_safety)

        return tiles

    def move_to(self, x_pos, y_pos, client, render=True):
        if self.x_pos - x_pos == 2:
            client.board[y_pos][0].move_to(x_pos + 1, y_pos, client, render)

        if self.x_pos - x_pos == -2:
            client.board[y_pos][-1].move_to(x_pos - 1, y_pos, client, render)

        super(King, self).move_to(x_pos, y_pos, client, render)


textures = {
    EmptyTile: None,
    Pawn: 'figure_textures/%s_pawn.png',
    Rook: 'figure_textures/%s_rook.png',
    Knight: 'figure_textures/%s_knight.png',
    Bishop: 'figure_textures/%s_bishop.png',
    Queen: 'figure_textures/%s_queen.png',
    King: 'figure_textures/%s_king.png',
}
