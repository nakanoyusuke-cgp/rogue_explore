from enum import Enum
import numpy as np


class Symbols(Enum):
    VOID = 0
    WALL = 1
    FLOOR = 2
    GATE = 3
    AISLE = 4
    RATION = 5
    STAIR = 6
    PLAYER = 7

    @property
    def character(self):
        return characters[self]

    @staticmethod
    def terrains():
        return [Symbols.VOID, Symbols.WALL, Symbols.FLOOR, Symbols.GATE, Symbols.AISLE]

    @staticmethod
    def terrain_values():
        return [n.value for n in Symbols.terrains()]

    @staticmethod
    def objects():
        return [Symbols.RATION, Symbols.STAIR, Symbols.PLAYER]

    @staticmethod
    def object_values():
        return [n.value for n in Symbols.objects()]

    @staticmethod
    def items():
        return [Symbols.RATION, Symbols.STAIR]

    @staticmethod
    def item_values():
        return [n.value for n in Symbols.items()]

    @staticmethod
    def obstacles():
        return [Symbols.VOID, Symbols.WALL]

    @staticmethod
    def obstacle_values():
        return [n.value for n in Symbols.obstacles()]

    @staticmethod
    def passable_cells():
        return [Symbols.FLOOR, Symbols.GATE, Symbols.AISLE]

    @staticmethod
    def passable_cell_values():
        return [n.value for n in Symbols.passable_cells()]


directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

characters = {
    Symbols.VOID: ' ',
    Symbols.WALL: '#',
    Symbols.FLOOR: '.',
    Symbols.GATE: '*',
    Symbols.AISLE: '+',
    Symbols.RATION: 'R',
    Symbols.STAIR: 'S',
    Symbols.PLAYER: 'P'
}


class Dungeon(object):
    def __init__(self, terrains):
        assert terrains.shape[-1] == len(Symbols), "num symbols is not same"
        self._terrains = terrains[..., Symbols.terrain_values()]
        self._objects = {}
        for s in Symbols.items():
            self._objects.update({tuple(pos): s for pos in np.argwhere(terrains[..., s.value])})
        # print(self._objects)
        self.history = np.zeros((terrains.shape[:-1]), dtype=np.int8)
        self.player_pos = tuple(np.argwhere(terrains[..., Symbols.PLAYER.value])[0])
        self.history[self.player_pos] = 1

    def remove_all_items(self):
        self._objects = {k:v for k, v in self._objects.items() if v != Symbols.RATION}

    def move(self, to):
        next_pos = (self.player_pos[0] + to[0], self.player_pos[1] + to[1])
        moved = self.can_move_to(next_pos)
        picked = None
        reach_unreachable = False

        if moved:
            if next_pos in self._objects.keys():
                picked = self._objects.pop(next_pos)
            # picked = Symbols.items()[np.argmax(self._terrains[next_pos + (Symbols.item_values(),)])]
            # self.pick_item(next_pos, picked)
            # self._terrains[self.player_pos + (Symbols.PLAYER.value,)] = 0
            # self._terrains[next_pos + (Symbols.PLAYER.value,)] = 1
            self.player_pos = next_pos
            reach_unreachable = self.history[self.player_pos] == 0
            self.history[self.player_pos] = 1

        # assert np.sum(self._layers[..., Symbols.terrain_values()]) == (self.image_shape[0] * self.image_shape[1])
        # print(f"{np.sum(self._terrains[..., Symbols.terrain_values()])} {(self.image_shape[0] * self.image_shape[1])} ")
        # assert picked != Symbols.PLAYER, "cannot pick Player"
        return moved, picked, reach_unreachable

    def can_move_to(self, pos):
        return self._terrains[pos + (Symbols.obstacle_values(), )].sum() == 0

    def symbol_map(self, enable_history):
        object_map = np.zeros(self.image_shape + (len(Symbols.objects()),), dtype=np.int8)
        if enable_history:
            res = np.dstack([self._terrains, object_map, self.history[..., np.newaxis]])
        else:
            res = np.dstack([self._terrains, object_map])
        indices = [p + (s.value, ) for p, s in list(self._objects.items()) + [(self.player_pos, Symbols.PLAYER)]]
        # print(list(zip(*indices)))
        res[tuple(zip(*indices))] = 1
        return res

    def simple_symbol_map(self, enable_history):
        object_map = np.zeros(self.image_shape + (len(Symbols.objects()),), dtype=np.int8)
        indices = [p + (s.value - len(Symbols.terrains()), ) for p, s in list(self._objects.items()) + [(self.player_pos, Symbols.PLAYER)]]
        object_map[tuple(zip(*indices))] = 1

        obs = np.sum(self._terrains[..., Symbols.obstacle_values()], axis=2, keepdims=True)
        pas = np.sum(self._terrains[..., Symbols.passable_cell_values()], axis=2, keepdims=True)
        if enable_history:
            res = np.dstack([obs, pas, object_map, self.history[..., np.newaxis]])
        else:
            res = np.dstack([obs, pas, object_map])
        return res

    @property
    def result(self):
        vect = np.vectorize(lambda x: Symbols(x).character)
        a = vect(np.argmax(self._terrains, axis=2))
        positions, symbols = zip(*(list(self._objects.items()) + [(self.player_pos, Symbols.PLAYER)]))
        # print(tuple(zip(*positions)))
        a[tuple(zip(*positions))] = [s.character for s in symbols]
        return '\n'.join([''.join(line) for line in a])

        # symbols = Symbols.objects() + Symbols.terrains()
        # symbol_values = Symbols.object_values() + Symbols.terrain_values()
        # vect = np.vectorize(lambda x: symbols[x].character)
        # a = vect(np.argmax(self._terrains[..., symbol_values], axis=2))
        # return '\n'.join([''.join(line) for line in a])

    @property
    def image_shape(self):
        return self._terrains.shape[:-1]
