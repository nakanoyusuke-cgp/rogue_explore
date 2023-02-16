class Room(object):
    def __init__(self, size_y, size_x, pos_y, pos_x):
        self.size_y = size_y
        self.size_x = size_x
        self.pos1_y = pos_y
        self.pos1_x = pos_x

    @property
    def pos2_y(self):
        return self.pos1_y + self.size_y - 1

    @property
    def pos2_x(self):
        return self.pos1_x + self.size_x - 1
