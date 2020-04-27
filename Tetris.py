import random
import pygame
from pygame import mixer
import numpy as np

# Variable to create window
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((610, 670))
pygame.display.set_caption('Tetris_assets/Tetris')
icon = pygame.image.load('Tetris_assets/tetris.png')
pygame.display.set_icon(icon)
mixer.music.load('Tetris_assets/tetris-gameboy-02.mp3')
mixer.music.play(-1)
line_clear_sound = mixer.Sound('Tetris_assets/line.wav')
game_over_sound = mixer.Sound('Tetris_assets/gameover.wav')
fall_sound = mixer.Sound('Tetris_assets/fall.wav')



# Variables for drawing the game area
wall_area = []
block_size = 30
rows = 21
columns = 12

# Variables for piece logic
fall_time = 0
key_up = True
locked_squares = []

# Variables to handle the scoring, and ramping difficulty
difficulty = 0
score = 0
lines_cleared = 0
endgame = False


class colour:
    white = (255, 255, 255)
    black = (0, 0, 0)
    light_gray = (128, 128, 128)
    red = (255, 0, 0)
    pink = (255, 96, 208)
    light_blue = (80, 208, 255)
    blue = (0, 32, 255)
    green = (0, 192, 0)
    yellow = (255, 224, 32)
    orange = (255, 160, 16)


class locked_square:
    def __init__(self, location, colour):
        self.i = location[0]
        self.j = location[1]
        self.location = [self.i, self.j]
        self.colour = colour


class piece:
    T = [(0, 1), (0, 2), (0, 0), (1, 1)]
    I = [(0, 0), (-1, 0), (1, 0), (2, 0)]
    S = [(0, 0), (0, 1), (1, 1), (-1, 0)]
    Z = [(0, 1), (0, 0), (1, 0), (-1, 1)]
    O = [(0, 0), (0, 1), (1, 1), (1, 0)]
    L = [(0, 0), (-1, 1), (-1, 0), (1, 0)]
    J = [(0, 0), (1, 1), (-1, 0), (1, 0)]
    shapes = [T, I, S, Z, O, L, J]
    shape_colours = [colour.pink, colour.light_blue, colour.green, colour.red, colour.yellow, colour.orange,
                     colour.blue]

    def __init__(self, shape):
        self.shape = shape
        self.colour = self.shape_colours[self.shapes.index(shape)]

    def map_block(self):
        mapped_piece = []
        for section in self:
            map1 = np.array(section)
            map2 = np.array((5, 0))
            mapped_piece.append(map1 + map2)
        return np.array(mapped_piece).tolist()


def get_piece():
    global shapes
    var = piece(random.choice(piece.shapes))
    var.location = piece.map_block(var.shape)
    return var


def move_piece(piece_to_move, direction):
    if direction == 'left':
        for i in piece_to_move.location:
            i[0] -= 1
    if direction == 'right':
        for i in piece_to_move.location:
            i[0] += 1
    if direction == 'up':
        for i in piece_to_move.location:
            i[1] -= 1
    if direction == 'down':
        for i in piece_to_move.location:
            i[1] += 1


def turn_piece(piece_to_turn, direction):
    result, output, mid = [], [], []
    for section in piece_to_turn.location:
        map1 = np.array(section)
        map2 = np.array((piece_to_turn.location[0]))
        mid.append(map1 - map2)
    for x, y in mid:
        if direction == 'left':
            result.append((y, -x))
        if direction == 'right':
            result.append((-y, x))
    for section in result:
        map1 = np.array(section)
        map2 = np.array(piece_to_turn.location[0])
        output.append(map1 + map2)
    piece_to_turn.location = output


def game_area():
    game_space = pygame.Surface((columns * block_size + 1, rows * block_size + 1))
    game_space.fill(colour.black)
    x = 0
    y = 0
    for row in range(rows + 1):
        pygame.draw.line(game_space, colour.white, (x, 0), (x, block_size * rows))
        pygame.draw.line(game_space, colour.white, (0, y), (block_size * rows, y))
        x += block_size
        y += block_size

    for i in wall_area:
        draw_wall = pygame.Rect(block_size * i[0] + 1, block_size * i[1] + 1, block_size - 1, block_size - 1)
        pygame.draw.rect(game_space, colour.light_gray, draw_wall)

    return game_space


def game_wall():
    for y in range(20):
        wall_area.append([0, y])
        wall_area.append([11, y])
    for x in range(12):
        wall_area.append([x, 20])


def render(piece_to_render):
    for i in piece_to_render.location:
        current_segments = pygame.Rect(block_size * i[0] + 1 + 20, block_size * i[1] + 1 + 20, block_size - 1,
                                       block_size - 1)
        pygame.draw.rect(screen, piece_to_render.colour, current_segments)
    for square in locked_squares:
        current_segments = pygame.Rect(block_size * square.i + 1 + 20, block_size * square.j + 1 + 20, block_size - 1,
                                       block_size - 1)
        pygame.draw.rect(screen, square.colour, current_segments)


def check_valid_move(piece_to_check):
    segment_list = []
    for i in piece_to_check.location:
        segment_list.append(np.array(i).tolist())
    if any(segment in segment_list for segment in wall_area) or any(
            segment in segment_list for segment in ([x.i, x.j] for x in locked_squares)):
        return True
    else:
        return False


def lock_active(piece_to_lock):
    for i in np.array(piece_to_lock.location):
        for _ in i:
            square = locked_square([i[0], i[1]], piece_to_lock.colour)
        locked_squares.append(square)


def piece_logic():
    global fall_time, key_up, piece1, piece2, piece3, piece4

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        move_piece(piece1, 'left')
        if check_valid_move(piece1):
            move_piece(piece1, 'right')

    if keys[pygame.K_RIGHT]:
        move_piece(piece1, 'right')
        if check_valid_move(piece1):
            move_piece(piece1, 'left')

    if keys[pygame.K_DOWN]:
        move_piece(piece1, 'down')
        if check_valid_move(piece1):
            move_piece(piece1, 'up')

    if keys[pygame.K_UP] and key_up:
        turn_piece(piece1, 'left')
        # Note, the O piece centre was the middle of the 4 blocks, so it rotated weirdly, the below logic unrotates
        # the piece if the rotated piece is a O piece
        if check_valid_move(piece1) or piece1.colour == colour.yellow:
            turn_piece(piece1, 'right')
        key_up = False

    clock.tick(18)
    fall_time += clock.get_rawtime()
    if fall_time > 300 - 21 * difficulty:
        fall_time = 0
        move_piece(piece1, 'down')
        if check_valid_move(piece1):
            fall_sound.play()
            move_piece(piece1, 'up')
            lock_active(piece1)
            piece1 = piece2
            piece2 = piece3
            piece3 = piece4
            piece4 = get_piece()


def clear_line(row):
    global lines_cleared, difficulty
    row_check = []
    for j in range(1, 11):
        row_check.append([j, row])
    if all(elem in list([[x.i, x.j] for x in locked_squares]) for elem in row_check):
        for elem in row_check:
            for index, var in enumerate(locked_squares):
                if elem == [var.i, var.j]:
                    locked_squares.pop(index)
        for var in locked_squares:
            if var.j < row:
                var.j += 1
        lines_cleared += 1
        if lines_cleared % 10 == 0 and not lines_cleared == 0:
            difficulty += 1


def display_score():
    global score
    score_font = pygame.font.Font('freesansbold.ttf', 20)
    scoredisplay = score_font.render("Score: %s" % score, True, colour.white)
    screen.blit(scoredisplay, (580 - scoredisplay.get_width(), 30))


def draw_next():
    for i in piece2.location:
        current_segments = pygame.Rect(block_size * i[0] + 330, block_size * i[1] + 280, block_size - 1,
                                       block_size - 1)
        pygame.draw.rect(screen, piece2.colour, current_segments)
    for i in piece3.location:
        current_segments = pygame.Rect(block_size * i[0] + 330, block_size * i[1] + 380, block_size - 1,
                                       block_size - 1)
        pygame.draw.rect(screen, piece3.colour, current_segments)
    for i in piece4.location:
        current_segments = pygame.Rect(block_size * i[0] + 330, block_size * i[1] + 480, block_size - 1,
                                       block_size - 1)
        pygame.draw.rect(screen, piece4.colour, current_segments)
    next_piece_font = pygame.font.Font('freesansbold.ttf', 20)
    next_piece_text = next_piece_font.render("Next pieces:", True, colour.white)
    screen.blit(next_piece_text, (440, 230))


def game_over():
    global endgame
    game_over_area = []
    for i in range(3, 8):
        game_over_area.append([i, 0])
        game_over_area.append([i, 1])
    if any(segment in game_over_area for segment in ([x.i, x.j] for x in locked_squares)):
        locked_squares.clear()
        piece1.location = [[100, 100]]
        piece2.location = [[100, 100]]
        piece3.location = [[100, 100]]
        piece4.location = [[100, 100]]
        endgame = True
        pygame.mixer.music.stop()
        game_over_sound.play()
    game_over_area.clear()
    if endgame:
        game_over_font = pygame.font.Font('freesansbold.ttf', 40)
        endgame = game_over_font.render("Game Over", True, (255, 255, 255))
        endgame2 = game_over_font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(endgame, (85, 250))
        screen.blit(endgame2, (35, 285))


piece1 = get_piece()
piece2 = get_piece()
piece3 = get_piece()
piece4 = get_piece()
game_wall()


def __main__():
    global key_up, score, endgame, piece1, piece2, piece3, piece4
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    key_up = True

            if event.type == pygame.KEYUP and endgame:
                if event.key == pygame.K_r:
                    endgame = False
                    pygame.mixer.music.play(-1)
                    piece1 = get_piece()
                    piece2 = get_piece()
                    piece3 = get_piece()
                    piece4 = get_piece()

        screen.fill(colour.black)
        screen.blit(game_area(), (20, 20))
        piece_logic()
        render(piece1)
        draw_next()

        onBoardCount = len(locked_squares)
        for row in range(20):
            clear_line(row)
        if onBoardCount - len(locked_squares) == 10:
            score += 40 * (difficulty + 1)
            line_clear_sound.play()
        elif onBoardCount - len(locked_squares) == 20:
            score += 100 * (difficulty + 1)
            line_clear_sound.play()
        elif onBoardCount - len(locked_squares) == 30:
            score += 300 * (difficulty + 1)
            line_clear_sound.play()
        elif onBoardCount - len(locked_squares) == 40:
            score += 1200 * (difficulty + 1)
            line_clear_sound.play()
        display_score()
        game_over()

        pygame.display.flip()


__main__()
