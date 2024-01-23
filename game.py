import re
import pygame
import math
from pygame import gfxdraw
from clock import ClockEmulator

class Move:


    def __init__(self, start: int, end: int, side: int, move: str):
        self.start = start
        self.end = end
        self.side = side
        self.move = move


    def to_string(self):
        return f"{self.start}-{self.end}:{self.side}={self.move}\n"

class ReconstructFileHandler:


    def __init__(self):
        self.filename = "0.crd"
        self.state = "playing"
        self.moves = []

        # self.reset()

    def reset(self):
        self.write_header()


    def write_header(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(f"scramble:UR5+\n")
            f.write(f"start_side:0\n")
            f.write(f"rotation:0\n")
            f.close()

    def read(self, clock: ClockEmulator):

        with open(self.filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

            print(lines)

        for i, line in enumerate(lines):

            line: str

            if i == 0:
                clock.reset()
                clock.convert_scramble(line.split(":")[1].replace("\n", ""))
                continue

            if i == 1:
                clock.side = int(line.split(":")[1].replace("\n", ""))
                continue

            if i == 2:
                clock.rotation = int(line.split(":")[1].replace("\n", ""))
                continue

            start = int(line.split("-")[0])
            end = int((line.split("-")[1]).split(":")[0])
            side = int((line.split("=")[0]).split(":")[1])
            move = (line.split("=")[1]).replace("\n", "")

            print(start, end, side, move)

            self.moves.append(Move(start, end, side, move))



    def write(self, move: Move):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(move.to_string())
            f.close()


class Game:

    def __init__(self):

        _ = pygame.display.set_mode((0, 0))

        self.run = True
        self.display = pygame.display.set_mode((890, 500), pygame.RESIZABLE) # 490, 300

        self.font = pygame.font.Font("assets/fonts/font1.ttf", 25)

        self.clock = ClockEmulator()

        self.frame = 1900

        self.r = ReconstructFileHandler()
        self.r.read(self.clock)


    def blit_text(self, text: str, pos, color=(255, 255, 255)):
        self.display.blit(self.font.render(text, True, color), pos)

    def draw_clock(self):

        fx = 45 # :flushed:
        fy = 44

        # clocks
        clock_radius = 23
        dot_radius = 2

        white_clock_surface = pygame.Surface((200, 200))
        black_clock_surface = pygame.Surface((200, 200))

        pygame.draw.rect(white_clock_surface, (255, 255, 255), (0, 0, 200, 200)) # draw bg
        pygame.draw.rect(black_clock_surface, (0, 0, 0), (0, 0, 200, 200))

        for i in range(self.clock.front.states.__len__() + self.clock.back.states.__len__()): # clock states

            state = self.clock.get_piece(int(i >= 9), i - 9 if i >= 9 else i, False)

            state += 6
            state = -state
            state = state % 12

            x, y = (i % 3 * 55 + fx), i // 3 * 55 + fy
            color = (0, 0, 0)

            surface = white_clock_surface

            if i >= 9:
                # x += 195
                surface = black_clock_surface
                y -= 55 * 3
                color = (255, 255, 255)

            for j in range(12):

                if j == 6:
                    continue

                pointer_color = tuple(min(color[i] + 30, 255) for i in range(3))
                draw_antialias_circle(surface, pointer_color,
                                           x + math.sin(j * (math.pi / 6)) * (clock_radius + dot_radius * 0),
                                           y + math.cos(j * (math.pi / 6)) * (clock_radius + dot_radius * 0),
                                           dot_radius)

            draw_antialias_circle(surface, color, x, y, clock_radius)

            draw_aa_pie(surface, (255, 255, 255) if i < 9 else (0, 0, 0), (x, y),
                             (x + math.sin(state * (math.pi / 6)) * clock_radius,
                              y + math.cos(state * (math.pi / 6)) * clock_radius), 3)

            draw_polygon(surface,
                             [(x, y - clock_radius - 2 + 1), (x - 2, y - 5 - clock_radius + 1), (x + 2, y - 5 - clock_radius + 1)],
                             (255, 0, 0))


        for j in range(2): # draw pins

            pins = self.clock.pins
            surface = white_clock_surface

            if j == 1:
                pins = _invert_pins(pins)
                surface = black_clock_surface

            for k in range(pins.__len__()):

                color = (80, 80, 80)

                if pins[k]:
                    color = (255, 255, 0)

                draw_antialias_circle(surface, color, k % 2 * 55 + fx + 28, k // 2 * 55 + fy + 28, 9)

        white_clock_surface = pygame.transform.rotate(white_clock_surface, 90 * self.clock.rotation)
        black_clock_surface = pygame.transform.rotate(black_clock_surface, -90 * self.clock.rotation)

        self.display.blit(white_clock_surface, (0, 100))
        self.display.blit(black_clock_surface, (200, 100))


    def draw(self):

        display = self.display
        display.fill((50, 50, 50))

        self.blit_text("Clock Reconstructor", (5, 5))

        self.draw_clock()
        self.blit_text(f"{self.frame}", (5, 45))

        pygame.display.update()



    def update(self, events: list[pygame.event.Event]) -> bool:

        for event in events:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.r.state = "paused"
                    self.frame = 0
                    self.clock.reset()
                    self.r.read(self.clock)

                if event.key == pygame.K_SPACE:
                    if self.r.state == "paused":
                        self.r.state = "playing"
                    elif self.r.state == "playing":
                        self.r.state = "paused"

        if self.r.state == "playing":

            for move in self.r.moves:

                if move.start <= self.frame < move.end:

                    match = re.match(r'([A-Z\/\\]+)(\d+)([+-])', str(move.move), re.I)  # split scramble block

                    if match:
                        items = match.groups()

                        pin = items[0]
                        amount = int(items[1])
                        direction = items[2]

                        amount /= (move.end - move.start)

                        if move.side == 1: # todo: do this more efficiently
                            self.clock.y2()

                        # print(f"{pin}{amount}{direction}")

                        self.clock.convert_scramble(f"{pin}{amount}{direction}")

                        if move.side == 1:
                            self.clock.y2()

                    else: # if it's not a move or a amount that has to be divided

                        # print(f"Unexpected move {move.move} found, assuming it's a rotation or pin instruction.")
                        self.clock.convert_scramble(move.move)

            self.frame += 1

        return self.run

def draw_antialias_circle(surface, color, x, y, radius):
    pygame.gfxdraw.aacircle(surface, round(x), round(y), radius, color)
    pygame.gfxdraw.filled_circle(surface, round(x), round(y), radius, color)


def draw_aa_pie(surface, color, from_, to, radius):
    draw_antialias_circle(surface, color, from_[0], from_[1], radius)

    direction = math.atan2(from_[0] - to[0], from_[1] - to[1])

    args = [
        surface,
        round(from_[0] + math.sin(direction + math.pi / 2) * radius),
        round(from_[1] + math.cos(direction + math.pi / 2) * radius),

        round(from_[0] + math.sin(direction - math.pi / 2) * radius),
        round(from_[1] + math.cos(direction - math.pi / 2) * radius),

        round(to[0]), round(to[1]), color
    ]
    pygame.gfxdraw.filled_trigon(*args)
    pygame.gfxdraw.aatrigon(*args)

def draw_polygon(surface, points, color):

    args = [
        surface,
        points,
        color
    ]

    pygame.gfxdraw.filled_polygon(*args)
    pygame.gfxdraw.aapolygon(*args)


def _invert_pins(pins):
    return [not pins[1], not pins[0], not pins[3], not pins[2]]