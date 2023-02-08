from copy import deepcopy


class Tetromino:
    def __init__(self, color):
        # color must be one of the following: 'Y', 'L', 'G', 'R', 'P', 'B', 'O'
        self.color = color
        self.y_pos = 0
        self.x_pos = 4
        self.rotation = 0

    def down(self):
        self.y_pos += 1

    def up(self):
        self.y_pos -= 1

    def left(self):
        self.x_pos -= 1

    def right(self):
        self.x_pos += 1

    # rotates the tetromino 90 degrees
    def rotate90(self):
        if self.color == 'Y':
            return
        elif self.color == 'L':
            if self.rotation == 0:
                self.x_pos += 2
                self.y_pos -= 1
            elif self.rotation == 1:
                self.x_pos -= 2
                self.y_pos += 2
            elif self.rotation == 2:
                self.x_pos += 1
                self.y_pos -= 2
            elif self.rotation == 3:
                self.x_pos -= 1
                self.y_pos += 1
        else:
            if self.rotation == 0:
                self.x_pos += 1
            elif self.rotation == 1:
                self.x_pos -= 1
                self.y_pos += 1
            elif self.rotation == 2:
                self.y_pos -= 1
            elif self.rotation == 3:
                pass

        # sets the new rotation
        self.rotation = (self.rotation + 1) % 4

    # returns the skeleton array of the piece for collision checking
    def skeleton(self):
        if self.color == 'Y':
            return [[1, 1],
                    [1, 1]]
        elif self.color == 'L':
            if self.rotation in [0, 2]:
                return [[1, 1, 1, 1]]
            elif self.rotation in [1, 3]:
                return [[1],
                        [1],
                        [1],
                        [1]]
        elif self.color == 'G':
            if self.rotation in [0, 2]:
                return [[0, 1, 1],
                        [1, 1, 0]]
            elif self.rotation in [1, 3]:
                return [[1, 0],
                        [1, 1],
                        [0, 1]]
        elif self.color == 'R':
            if self.rotation in [0, 2]:
                return [[1, 1, 0],
                        [0, 1, 1]]
            elif self.rotation in [1, 3]:
                return [[0, 1],
                        [1, 1],
                        [1, 0]]
        elif self.color == 'P':
            if self.rotation == 0:
                return [[0, 1, 0],
                        [1, 1, 1]]
            elif self.rotation == 1:
                return [[1, 0],
                        [1, 1],
                        [1, 0]]
            elif self.rotation == 2:
                return [[1, 1, 1],
                        [0, 1, 0]]
            elif self.rotation == 3:
                return [[0, 1],
                        [1, 1],
                        [0, 1]]
        elif self.color == 'B':
            if self.rotation == 0:
                return [[1, 0, 0],
                        [1, 1, 1]]
            elif self.rotation == 1:
                return [[1, 1],
                        [1, 0],
                        [1, 0]]
            elif self.rotation == 2:
                return [[1, 1, 1],
                        [0, 0, 1]]
            elif self.rotation == 3:
                return [[0, 1],
                        [0, 1],
                        [1, 1]]
        elif self.color == 'O':
            if self.rotation == 0:
                return [[0, 0, 1],
                        [1, 1, 1]]
            elif self.rotation == 1:
                return [[1, 0],
                        [1, 0],
                        [1, 1]]
            elif self.rotation == 2:
                return [[1, 1, 1],
                        [1, 0, 0]]
            elif self.rotation == 3:
                return [[1, 1],
                        [0, 1],
                        [0, 1]]


class Board:
    def __init__(self, board=None, lowest_y=None, lines_cleared=None):

        # generates the board
        if board is None:
            self.board = []
            for y in range(21):
                self.board.append([])
                for x in range(10):
                    if y == 20:
                        self.board[y].append(1)
                    else:
                        self.board[y].append(0)
        else:
            self.board = board

        self.lowest_y = 19 if lowest_y is None else lowest_y
        self.lines_cleared = 0 if lines_cleared is None else lines_cleared

    def __str__(self):
        out = ""
        for line in self.board:
            out += '\n'
            for var in line:
                out += f"{var} "
        return out

    # gets the value at the given pos. Returns None if out of bounds
    def __getitem__(self, pos):
        i, j = pos
        if i > 20 or i < 0 or j > 9 or j < 0:
            return None

        return self.board[i][j]

    # returns True if the board overlaps the tetromino. Otherwise returns False
    def is_overlapping_tetromino(self, tetromino: Tetromino):
        skeleton = tetromino.skeleton()
        for y in range(len(skeleton)):
            for x in range(len(skeleton[0])):
                pos = self[tetromino.y_pos + y, tetromino.x_pos + x]
                if pos is not None and pos != 0 and skeleton[y][x] != 0:
                    return True
        return False

    # joins the tetromino into the board
    def join(self, tetromino: Tetromino):
        skeleton = tetromino.skeleton()
        for y in range(len(skeleton)):
            for x in range(len(skeleton[0])):
                pos = self[tetromino.y_pos + y, tetromino.x_pos + x]
                if pos is not None and skeleton[y][x] != 0:
                    if tetromino.y_pos < self.lowest_y:
                        self.lowest_y = tetromino.y_pos
                    if self.board[tetromino.y_pos + y][tetromino.x_pos + x] == 0:
                        self.board[tetromino.y_pos + y][tetromino.x_pos + x] = tetromino.color

    # gets a list of full lines
    def full_lines(self):
        lines = []
        for y in range(self.lowest_y, 20):
            if 0 not in self.board[y]:
                lines.append(y)
        return lines

    # removes the given line index from the board
    def remove(self, lines: list):
        for line_index in lines:
            self.lowest_y += 1
            del self.board[line_index]
            self.board.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    # drops the given tetromino onto the board and returns a COPY of the new board (for evaluation)
    def drop(self, tetromino: Tetromino):

        newBoard = deepcopy(self)
        newTetromino = Tetromino(tetromino.color)
        newTetromino.rotation = tetromino.rotation
        newTetromino.x_pos = tetromino.x_pos

        while True:
            if newBoard.is_overlapping_tetromino(newTetromino):
                newTetromino.y_pos -= 1
                newBoard.join(newTetromino)
                break
            else:
                newTetromino.y_pos += 1

        return newBoard, newTetromino
