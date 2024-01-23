import copy
import re
from enum import Enum


class MoveMappings(Enum):

    UR = [[0, 1, 1,
          0, 1, 1,
          0, 0, 0],

          [-1, 0, 0,
          0, 0, 0,
          0, 0, 0]
          ]

    DR = [[0, 0, 0,
          0, 1, 1,
          0, 1, 1],

          [0, 0, 0,
          0, 0, 0,
          -1, 0, 0]
          ]

    DL = [[0, 0, 0,
          1, 1, 0,
          1, 1, 0],

          [0, 0, 0,
          0, 0, 0,
          0, 0, -1]
          ]

    UL = [[1, 1, 0,
          1, 1, 0,
          0, 0, 0],

          [0, 0, -1,
          0, 0, 0,
          0, 0, 0]
          ]

    U = [[1, 1, 1,
         1, 1, 1,
         0, 0, 0],

         [-1, 0, -1,
         0, 0, 0,
         0, 0, 0]
         ]

    R = [[0, 1, 1,
         0, 1, 1,
         0, 1, 1],

         [-1, 0, 0,
         0, 0, 0,
         -1, 0, 0]
         ]

    D = [[0, 0, 0,
         1, 1, 1,
         1, 1, 1],

         [0, 0, 0,
         0, 0, 0,
         -1, 0, -1]
         ]

    L = [[1, 1, 0,
         1, 1, 0,
         1, 1, 0],

         [0, 0, -1,
         0, 0, 0,
         0, 0, -1]
         ]

    ALL = [[1, 1, 1,
           1, 1, 1,
           1, 1, 1],

           [-1, 0, -1,
           0, 0, 0,
           -1, 0, -1]
           ]

    BACKSLASH = [[1, 1, 0,
             1, 1, 1,
             0, 1, 1],

             [0, 0, -1,
             0, 0, 0,
             -1, 0, 0]
             ]

    SLASH = [[0, 1, 1,
              1, 1, 1,
              1, 1, 0],

             [-1, 0, 0,
              0, 0, 0,
              0, 0, -1]
             ]

    ur = [[1, 1, 0,
          1, 1, 1,
          1, 1, 1],

          [0, 0, -1,
          0, 0, 0,
          -1, 0, -1]]

    dr = [[1, 1, 1,
          1, 1, 1,
          1, 1, 0],

          [-1, 0, -1,
          0, 0, 0,
          0, 0, -1]]

    dl = [[1, 1, 1,
          1, 1, 1,
          0, 1, 1],

          [-1, 0, -1,
          0, 0, 0,
          -1, 0, 0]]

    ul = [[0, 1, 1,
          1, 1, 1,
          1, 1, 1],

          [-1, 0, 0,
          0, 0, 0,
          -1, 0, -1]]


class PinMappings(Enum):

    UR = [0, 1,
          0, 0]

    DR = [0, 0,
          0, 1]

    DL = [0, 0,
          1, 0]

    UL = [1, 0,
          0, 0]

    U = [1, 1,
         0, 0]

    R = [0, 1,
         0, 1]

    D = [0, 0,
         1, 1]

    L = [1, 0,
         1, 0]

    ALL = [1, 1,
           1, 1]

    BACKSLASH = [1, 0,
                 0, 1]

    SLASH = [0, 1,
             1, 0]

    ur = [1, 0,
          1, 1]

    dr = [1, 1,
          1, 0]

    dl = [1, 1,
          0, 1]

    ul = [0, 1,
          1, 1]


class ClockEmulator:

    class Side:
        def __init__(self, front: bool):
            self.front: bool = front
            self.states = [0, 0, 0,
                           0, 0, 0,
                           0, 0, 0]


    def __init__(self):

        self.pins = [True, True,
                     True, True]


        self.front = ClockEmulator.Side(True)
        self.back = ClockEmulator.Side(False)

        self.rotation = 0 # 0 = 0d, 1 = 45d, 2 = 90d, 3 = 135d (clockwise) (works glitchy) # TODO: fix this
        self.side = 0 # 0 = front, 1 = back

    def reset(self) -> None:

        self.front.states = [0, 0, 0,
                             0, 0, 0,
                             0, 0, 0]

        self.back.states = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0]

        self.pins = [True, True,
                     True, True]

        self.rotation = 0

    def convert_scramble(self, scramble: str) -> None:

        blocks = scramble.split(" ")

        for block in blocks:

            match = re.match(r'''([A-Z\/\\]+)([\d\.\d]+)([+-])''', str(block), re.I)  # split scramble block

            if match:

                items = match.groups()

                # print(items)

                pin = items[0]  # pin, e.g. UR
                amount = float(items[1])  # amount, e.g. 5
                direction = int(items[2] + "1")  # indicates its direction that clock moves, +1 / -1

                if pin == "/":
                    pin = "SLASH"
                elif pin == "\\":
                    pin = "BACKSLASH"

                self.pins = [False, False,
                             False, False]
                self.set_pins(self.side, PinMappings[pin].value)
                self.move_with(amount * direction, self.side, MoveMappings[pin].value)

                # print(self.side, self.front.states, self.back.states)


            else:  # special cases

                pin = str(block)

                if pin == "z":

                    if self.side == 0:
                        self.rotation += 1
                    elif self.side == 1:
                        self.rotation -= 1

                    self.rotation %= 4

                elif pin == "z'":

                    if self.side == 0:
                        self.rotation -= 1
                    elif self.side == 1:
                        self.rotation += 1

                    self.rotation %= 4

                elif pin == "z2":

                    self.rotation += 2
                    self.rotation %= 4

                elif pin == "x2":

                    self.rotation += 2
                    self.rotation %= 4
                    self.side = 0 if self.side == 1 else 1

                elif pin == "y2":

                    self.y2()

                else:

                    print(f"Don't know how to handle {pin}, assuming its a pin instruction.")

                    self.set_pins(self.side, PinMappings[pin].value)


    def set_pins(self, side, method):

        if side == 0:

            self.pins = method

            for _ in range(self.rotation):
                self.pins = self.rotate_pins(self.pins, True)
            print("fin", self.pins)

        elif side == 1:

            self.pins = _invert_pins(method)

            for _ in range(self.rotation):
                self.pins = _invert_pins(self.rotate_pins(self.pins, False))


    def move_with(self, amount, side, method):  # this code sucks ngl

        relative_front = method[0]
        relative_back = method[1]

        for _ in range(self.rotation):
            relative_front = self.rotate_clock(relative_front, side == 1) # super weird that clockwise get switched here but idc it works
            relative_back = self.rotate_clock(relative_back, side == 0)

        print(relative_front)

        for j, rule in enumerate(relative_front):

            if side == 0:

                if rule == 1:
                    self.front.states[j] += amount
                elif rule == -1:
                    assert False

            elif side == 1:

                if rule == 1:
                    self.back.states[j] += amount
                elif rule == -1:
                    assert False

            self.front.states[j] %= 12
            self.back.states[j] %= 12

        for k, rule in enumerate(relative_back):

            if side == 0:

                if rule == -1:
                    self.back.states[k] -= amount
                elif rule == 1:
                    assert False

            elif side == 1:

                if rule == -1:
                    self.front.states[k] -= amount
                elif rule == 1:
                    assert False

            self.front.states[k] %= 12
            self.back.states[k] %= 12

        # print(self.front.states, self.back.states)

    def get_piece(self, side: int, piece: int, rotated: bool) -> int:

        if rotated:

            if side == 0:

                k = self.front.states

                for _ in range(self.rotation):
                    k = self.rotate_clock(k, True)

            elif side == 1:

                k = self.back.states

                for _ in range(self.rotation):
                    k = self.rotate_clock(k, False)

            else:

                raise ValueError("Side must be 0 or 1")
        else:

            if side == 0:
                k = self.front.states
            elif side == 1:
                k = self.back.states
            else:
                raise ValueError("Side must be 0 or 1")

        return k[piece]


    def rotate_clock(self, matrix, clockwise: bool):

        if matrix.__len__() != 9:
            raise ValueError(f"Length {matrix.__len__()} is not supported, the length should be 9")

        w = copy.deepcopy(matrix)

        print("before", w)

        if clockwise:
            res = [w[6], w[3], w[0], w[7], w[4], w[1], w[8], w[5], w[2]]
        else:
            res = [w[2], w[5], w[8], w[1], w[4], w[7], w[0], w[3], w[6]]

        print("after", res)

        return res

    def rotate_pins(self, matrix, clockwise: bool):

        if matrix.__len__() != 4:
            raise ValueError(f"Length {matrix.__len__()} is not supported, the length should be 9")

        w = copy.deepcopy(matrix)

        if clockwise:
            res = [w[1], w[3], w[0], w[2]]
        else:
            res = [w[2], w[0], w[3], w[1]]

        return res

    def y2(self):

        if self.side == 0:
            self.side = 1

        elif self.side == 1:
            self.side = 0

def _invert_pins(pins):
    return [not pins[1], not pins[0], not pins[3], not pins[2]]