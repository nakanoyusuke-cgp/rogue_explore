import numpy as np
import random
import zlib
import pickle
from tqdm import tqdm

from rogue_explore.section import Section
from rogue_explore.dungeon import Symbols, Dungeon
from rogue_explore.dungeon_params import *


class DungeonGenerator(object):
    def __init__(self, place_rations, pooling=False, depth=None, seed_range=None):
        self.place_rations = place_rations
        self.root_section = None
        self.terrains = None
        self.rng = random.Random()
        self.seed = None
        self.make_count = None
        self.pooling = pooling
        self.depth = depth
        self.seed_range = seed_range
        self.pool = {}
        if self.pooling:
            assert (depth is not None) and (seed_range is not None), 'depth or seed_range is not assigned'
            self.pool_terrains()
        # 1階から最深部までダンジョンはstateを引き継いで生成される
        # -> poolingは最初にすべてする必要がある。
        # -> depth, seed_range を最初に取得する必要がある

    def set_seed(self, seed):
        self.rng.seed(seed)
        self.seed = seed
        self.make_count = 0

    def pool_terrains(self):
        self.pool = {}
        for seed in range(self.seed_range[0], self.seed_range[1]):
            self.pool[seed] = []
            self.set_seed(seed)
            seed_idx = seed - self.seed_range[0]
            num_seeds = self.seed_range[1] - self.seed_range[0]
            for _ in tqdm(range(self.depth), desc=f'Seed-{seed} ({seed_idx}/{num_seeds})'):
                self.generate_terrains()
                self.pool[seed].append(zlib.compress(pickle.dumps(self.terrains)))
        self.seed = 0
        self.rng.seed(0)

    def get_terrains_from_pool(self):
        self.terrains = pickle.loads(zlib.decompress(self.pool[self.seed][self.make_count]))

    def generate_terrains(self):
        self.make_sections()
        self.make_rooms()
        self.reduce_sections_not_contains_any_rooms()
        self.make_routes()
        self.generate_layers()
        self.put_objects()

    def make_dungeon(self):
        if self.pooling:
            assert self.make_count < self.depth, 'overflow pool'
            assert (self.seed >= self.seed_range[0]) and (self.seed < self.seed_range[1]), 'seed overflow'
            self.get_terrains_from_pool()
        else:
            self.generate_terrains()
        self.make_count += 1
        dungeon = Dungeon(self.terrains)
        if not self.place_rations:
            dungeon.remove_all_items()
        return dungeon

    def put_objects(self):
        pos = np.argwhere(self.terrains[..., Symbols.FLOOR.value])
        num = self.rng.randint(MIN_NUM_RATION, MAX_NUM_RATION) + 2
        pos = self.rng.sample(pos.tolist(), k=num)
        self.terrains[pos[0][0], pos[0][1], Symbols.PLAYER.value] = 1
        self.terrains[pos[1][0], pos[1][1], Symbols.STAIR.value] = 1
        for py, px in pos[2:]:
            self.terrains[py, px, Symbols.RATION.value] = 1

    def generate_layers(self):
        res = np.zeros((MAP_SIZE_Y, MAP_SIZE_X, len(Symbols)), dtype=np.int8)
        divs = self.root_section.enumerate_dividers()
        aisles = []
        for div in divs:
            aisles += div.aisles

        rooms = [s.room for s in self.root_section.enumerate_leaf_sections()]
        for room in rooms:
            res[room.pos1_y:room.pos2_y+1, room.pos1_x:room.pos2_x+1, Symbols.WALL.value] = 1
            res[room.pos1_y+1:room.pos2_y, room.pos1_x+1:room.pos2_x, Symbols.WALL.value] = 0
            res[room.pos1_y+1:room.pos2_y, room.pos1_x+1:room.pos2_x, Symbols.FLOOR.value] = 1
        for wp1, wp2, wp3, wp4 in aisles:
            aisle = [
                (wp1, wp2), (wp2, wp3), (wp3, wp4)
            ]
            for wp_b, wp_a in aisle:
                y_max = max(wp_b[0], wp_a[0])
                y_min = min(wp_b[0], wp_a[0])
                x_max = max(wp_b[1], wp_a[1])
                x_min = min(wp_b[1], wp_a[1])
                res[y_min:y_max+1, x_min:x_max+1, Symbols.AISLE.value] = 1
            res[tuple(wp1) + ([Symbols.AISLE.value, Symbols.WALL.value], )] = 0
            res[tuple(wp1) + (Symbols.GATE.value, )] = 1
            res[tuple(wp4) + ([Symbols.AISLE.value, Symbols.WALL.value], )] = 0
            res[tuple(wp4) + (Symbols.GATE.value, )] = 1
        res[..., 0] = 1 - res.sum(axis=2)
        self.terrains = res

    def make_sections(self):
        root = Section(size_y=MAP_SIZE_Y, size_x=MAP_SIZE_X, pos_y=0, pos_x=0)
        num_sections = self.rng.randint(MIN_NUM_SECTIONS, MAX_NUM_SECTIONS)
        for i in range(num_sections):
            if not root.can_divide():
                break

            root.divide(rng=self.rng)

        self.root_section = root

    def make_rooms(self):
        leaf_sections = self.root_section.enumerate_leaf_sections()
        num_rooms = self.rng.randint(MIN_NUM_ROOMS, min(MAX_NUM_ROOMS, len(leaf_sections)))

        selected = self.rng.sample(leaf_sections, k=num_rooms)
        for section in selected:
            section.make_room(rng=self.rng)

    def reduce_sections_not_contains_any_rooms(self):
        self.root_section = self.root_section.reduce_sections_not_contains_any_rooms()
        self.root_section.recalculate_transform()

    def make_routes(self):
        self.root_section.find_candidate_routes()
        divs = self.root_section.enumerate_dividers()
        num_route_candidates = 0
        route_candidates = []
        for div in divs:
            num_route_candidates += len(div.routes) - 1
            route_candidates += [div] * (len(div.routes) - 1)
            div.make_route(rng=self.rng)

        num_extra_routes = self.rng.randint(0, len(route_candidates))
        divs_make_route = self.rng.sample(route_candidates, k=num_extra_routes)
        for div in divs_make_route:
            div.make_route(rng=self.rng)

    def debug_preview(self):
        a = np.full((MAP_SIZE_Y, MAP_SIZE_X), ' ')
        leafs = self.root_section.enumerate_leaf_sections()
        divs = self.root_section.enumerate_dividers()
        for i, section in enumerate(leafs):
            a[section.pos1_y: section.pos2_y + 1, section.pos1_x: section.pos2_x + 1] = str(i + 1)
            if section.has_room:
                room = section.room
                a[room.pos1_y: room.pos2_y + 1, room.pos1_x: room.pos2_x + 1] = '#'
                a[room.pos1_y + 1: room.pos2_y, room.pos1_x + 1: room.pos2_x] = '.'
        res = '\n'.join([''.join(line) for line in a])
        print('=== debug ===')
        print(res)


if __name__ == "__main__":
    dg = DungeonGenerator(pooling=True, depth=10, seed_range=[0, 40])
    dg.set_seed(10)
    d = dg.make_dungeon()
    print(d.symbol_map(False).shape)
