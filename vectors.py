from copy import copy

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.initial = (x, y)


    def reset(self, x=True, y=True):
        if x:
            self.x, _ = self.initial
        if y:
            self.y, _ = self.initial

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __add__(self, other):
        obj = copy(self)
        obj.x = self.x + other.x
        obj.y = self.y + other.y
        return obj

    def __sub__(self, other):
        obj = copy(self)
        obj.x = self.x - other.x
        obj.y = self.y - other.y
        return obj

    def __mul__(self, other):
        obj = copy(self)
        obj.x = self.x * other.x
        obj.y = self.y * other.y
        return obj

class Position(Vector):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __repr__(self):
        return f"Position[{self.x}; {self.y}]"



class Velocity(Vector):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __repr__(self):
        return f"Velocity[{self.x}; {self.y}]"

    def change_magnitude(self):
        multiplier = 1.1
        self.x *= multiplier
        self.y /= multiplier

    def change_x_direction(self):
        self.x *= -1

    def change_y_direction(self):
        self.y *= -1
