from game import *
from numpy import e


class AI:
    def __init__(self):
        pass

    @staticmethod
    def evaluate(board: Board):

        line_heights = []
        holes = 0

        # search from top to bottom, left to right
        for x in range(10):
            top = False
            for y in range(board.lowest_y, 20):

                value = board[y, x]

                # if there is a block and we haven't hit a block yet...
                if value != 0 and not top:
                    top = True
                    line_heights.append(20 - y)

                # if there is no block and we have hit a block
                elif value == 0 and top:
                    holes += 1

            # if we hit no blocks the line height is 0
            if not top:
                line_heights.append(0)

        max_height = 20 - board.lowest_y
        aggregate_height = sum(line_heights)

        bumpiness = 0
        for i in range(9):
            bumpiness += abs(line_heights[i] - line_heights[i+1])

        return (AI.eval_holes(holes) * 0.2
                + AI.eval_aggregate_height(aggregate_height) * 0.35
                + AI.eval_bumpiness(bumpiness) * 0.1
                + AI.eval_max_height(max_height) * 0.35)

    @staticmethod
    def eval_holes(holes):

        if holes == 0:
            return 1

        return 1 / (1 + e ** ((0.5 * holes) - 4))

    @staticmethod
    def eval_aggregate_height(aggregate_height):

        if aggregate_height == 0:
            return 1

        return 1 / (1 + e ** ((0.05 * aggregate_height) - 5))

    @staticmethod
    def eval_bumpiness(bumpiness):

        if bumpiness == 0:
            return 1

        return 1 / (1 + e ** ((0.5 * bumpiness) - 4))

    @staticmethod
    def eval_max_height(height):

        if height <= 1:
            return 1
        if height >= 20:
            return 0

        return 2 / (e ** (height * 0.0346)) - 1

    @staticmethod
    def best_move(board: Board, tetromino: Tetromino):

        highest_score = 0
        best_move = Move(None, None, None)

        newTetromino = Tetromino(tetromino.color)
        for r in range(4 if tetromino.color in ['B', 'O', 'P'] else (1 if tetromino.color == 'Y' else 2)):
            newTetromino.rotation = r
            skeleton = newTetromino.skeleton()
            for x in range(10):
                if x + len(skeleton[0]) - 1 < 10:
                    newTetromino.x_pos = x

                    newBoard, newTetromino = board.drop(newTetromino)
                    newBoard.remove(newBoard.full_lines())

                    score = AI.evaluate(newBoard)

                    if highest_score < score:
                        highest_score = score
                        best_move = Move(r, x, newTetromino.y_pos)

        return best_move


class Move:
    def __init__(self, rotation, x_pos, y_pos):
        self.rotation = rotation
        self.x_pos = x_pos
        self.y_pos = y_pos

    def __str__(self):
        return f"rotation: {self.rotation}, x_pos: {self.x_pos}, y_pos: {self.y_pos}"

    def convert_to_actions(self, tetromino: Tetromino):

        actions = []

        temp_tetromino = Tetromino(tetromino.color)
        temp_tetromino.rotation = tetromino.rotation
        while temp_tetromino.rotation != self.rotation:
            temp_tetromino.rotate90()  # increase our rotation by 1 (4 goes to 0)
            actions.append('r')

        delta_x = self.x_pos - temp_tetromino.x_pos
        for x in range(abs(delta_x)):
            if delta_x < 0:
                actions.append('L')
            elif delta_x > 0:
                actions.append('R')

        return actions


class Square:
    def __init__(self, i, j):
        self.i, self.j = i, j

    def look_up(self, board):
        return board[self.i - 1, self.j]

    def look_down(self, board):
        return board[self.i + 1, self.j]

    def look_left(self, board):
        return board[self.i, self.j - 1]

    def look_right(self, board):
        return board[self.i, self.j + 1]
