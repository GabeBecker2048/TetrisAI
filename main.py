import pygame
import time
import random
from game import *
import ai
from threading import Thread

# sets up pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()
BlockletterBig = pygame.font.SysFont('Blockletter', 48)
BlockletterSmall = pygame.font.SysFont('Blockletter', 32)
screen = pygame.display.set_mode((320, 640))
pygame.display.set_caption("Tetris AI")
pygame.display.set_icon(pygame.image.load("./assets/blue_piece.png"))
game_background = pygame.image.load("./assets/background.png")
title_screen1 = pygame.image.load("./assets/titlescreen1.png")
title_screen2 = pygame.image.load("./assets/titlescreen2.png")
pygame.mixer.music.load("./assets/Tetris_theme.mp3")
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(loops=-1)


class AiThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


# function for pasting a tetromino onto the screen
def tetromino_paste(tetromino):
    skeleton = tetromino.skeleton()
    for y in range(len(skeleton)):
        for x in range(len(skeleton[0])):
            if skeleton[y][x] == 1:
                screen.blit(pygame.image.load(f"./assets/{tetromino.color}_block.png"),
                            ((tetromino.x_pos + x) * 32, (tetromino.y_pos + y) * 32))


# function for pasting the board onto the screen
def board_paste(board):

    for y in range(board.lowest_y, 21):
        for x in range(10):
            color = board[y, x]
            if color in colors:
                screen.blit(pygame.image.load(f"./assets/{color}_block.png"), (x * 32, y * 32))


# function for pasting the losing text on the screen
def loser_paste(board):
    screen.blit(BlockletterBig.render("YOU LOSE!", False, (255, 255, 255)), (70, 220))
    screen.blit(BlockletterSmall.render(f"You cleared {board.lines_cleared} lines" if board.lines_cleared != 1 else
                                        "You cleared 1 line",
                                        False, (255, 255, 255)), (60, 320))
    screen.blit(BlockletterSmall.render(f"Hit space to restart", False, (255, 255, 255)), (60, 620))


# game variables
colors = ['Y', 'L', 'G', 'R', 'P', 'B', 'O']
actions = []
falling_piece = None
last_update = time.time()
s_hold = False
last_s_hold = time.time()
board = Board()
screenstate = 1

# game loop
state = "start"
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if on the titlescreen and the player clicks, the game starts
        if event.type == pygame.MOUSEBUTTONDOWN and state == "start":
            last_update = time.time()
            state = "running"
            screen.blit(game_background, (0, 0))
            board = Board()
            falling_piece = Tetromino(colors[random.randrange(7)])
            ai_thread = AiThread(target=ai.AI.best_move, args=(board, falling_piece,))  # generates the first move
            calculated = False
            ai_thread.start()
            pygame.display.update()

        # if the player pushes a button down
        if event.type == pygame.KEYDOWN:

            # moves the tetromino left if pressing a and right if pressing d
            if event.key == pygame.K_a:
                falling_piece.left()
                if board.is_overlapping_tetromino(falling_piece):
                    falling_piece.right()
            elif event.key == pygame.K_d:
                falling_piece.right()
                if board.is_overlapping_tetromino(falling_piece):
                    falling_piece.left()

            # rotates the tetromino if pressing w
            elif event.key == pygame.K_w:
                falling_piece.rotate90()

            # moves the piece down faster if pressing s
            elif event.key == pygame.K_s:
                last_s_hold = time.time()
                s_hold = True

            # restarts the game if pressing space and the game ended
            elif event.key == pygame.K_SPACE:
                if state == "lose":
                    state = "start"

        # for s dropping
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                s_hold = False

    # for s dropping
    if s_hold and last_s_hold + 0.0625 < time.time() and falling_piece.y_pos < 18:
        last_s_hold = time.time()
        falling_piece.down()
        if board.is_overlapping_tetromino(falling_piece):
            falling_piece.up()
            board.join(falling_piece)
            if board.lowest_y == 0:
                state = "lose"
            else:
                full_lines = board.full_lines()
                for line in full_lines:
                    for x in range(10):
                        board.board[line][x] = 0

                    pygame.mixer.find_channel().play(pygame.mixer.Sound("./assets/line_clear.mp3"))

                    cycles = ["green_background", "background"]
                    for i in range(4):
                        board_paste(board)
                        color = cycles[i % 2]
                        for x in range(10):
                            screen.blit(pygame.image.load(f"./assets/{color}_block.png"), (x * 32, line * 32))
                        pygame.display.update()
                        time.sleep(0.25)
                    board.lines_cleared += 1

                board.remove(full_lines)
                pygame.display.update()

                falling_piece = Tetromino(colors[random.randrange(7)])
                ai_thread = AiThread(target=ai.AI.best_move, args=(board, falling_piece,))  # generates a new move
                calculated = False
                ai_thread.start()

    # title screen animation
    if state == "start":
        if time.time() > last_update + 0.25:
            if screenstate == 1:
                screen.blit(title_screen1, (0, 0))
            else:
                screen.blit(title_screen2, (0, 0))
            screenstate = 1 - screenstate
            last_update = time.time()
        pygame.display.update()

    # if the game is started...
    if state == "running":
        # adds the background
        screen.blit(game_background, (0, 0))

        # checks if the thread is done
        if not ai_thread.is_alive() and not calculated:
            best_move = ai_thread.join()
            actions = best_move.convert_to_actions(falling_piece)
            calculated = True

        # this pushes all blocks back in bounds if they are out of bounds
        while falling_piece.x_pos + len(falling_piece.skeleton()[0]) - 1 > 9:
            falling_piece.x_pos -= 1
        while falling_piece.x_pos < 0:
            falling_piece.x_pos += 1
        while falling_piece.y_pos + len(falling_piece.skeleton()) > 20:
            falling_piece.y_pos -= 1

        # The game completes one action per frame
        if actions:
            if actions[0] == 'r':
                falling_piece.rotate90()
            elif actions[0] == 'L':
                falling_piece.left()
            elif actions[0] == 'R':
                falling_piece.right()
            del actions[0]

        # moves the piece down if 0.25 seconds have passed
        if time.time() > last_update + 0.1:
            falling_piece.down()
            last_update = time.time()
            if board.is_overlapping_tetromino(falling_piece):
                falling_piece.up()
                board.join(falling_piece)
                if board.lowest_y == 0:
                    state = "lose"
                else:
                    full_lines = board.full_lines()
                    for line in full_lines:
                        for x in range(10):
                            board.board[line][x] = 0

                        pygame.mixer.find_channel().play(pygame.mixer.Sound("./assets/line_clear.mp3"))

                        cycles = ["green_background", "background"]
                        for i in range(4):
                            board_paste(board)
                            color = cycles[i % 2]
                            for x in range(10):
                                screen.blit(pygame.image.load(f"./assets/{color}_block.png"), (x * 32, line * 32))
                            pygame.display.update()
                            time.sleep(0.25)
                        board.lines_cleared += 1

                    board.remove(full_lines)
                    pygame.display.update()

                    falling_piece = Tetromino(colors[random.randrange(7)])
                    ai_thread = AiThread(target=ai.AI.best_move, args=(board, falling_piece,))  # generates a new move
                    calculated = False
                    ai_thread.start()

        # evaluates the board and puts it on the screen
        evaluation = ai.AI.evaluate(board)
        screen.blit(BlockletterSmall.render(f"{evaluation}", False, (255, 255, 255)), (0, 0))

        # pastes the falling piece
        tetromino_paste(falling_piece)
        board_paste(board)
        if state == "lose":
            loser_paste(board)
        pygame.display.update()
