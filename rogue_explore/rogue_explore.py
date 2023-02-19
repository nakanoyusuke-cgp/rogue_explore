import numpy as np
import tkinter as tk
import random

from rogue_explore.dungeon_generator import DungeonGenerator
from rogue_explore.image_repr import ImageRepr
from rogue_explore.reward_func import RewardFunc
from rogue_explore.dungeon import Symbols

# SEED = 0
DEFAULT_CONFIG = {
    'enable_rations_and_hunger': True,
    'simply_terrains': False,
    'enable_history': False,
    'style': 'symbols',
    'player_center': False,
    'depth': 10,
    'seed_range': [0, 40],
    'max_hunger': 100,
    'max_num_rations': 5,
    'default_num_rations': 0,
    'max_steps': 3000,
    'rewards': {
        "clear": 100,
        "down_stair": 100,
        "success_eat": 0,
        "failure_eat": 0,
        "get_ration": 1,
        "reach_unreachable": 0.05,
        "stuck": -0.005,
        "move": 0
    },
    'dungeon_params': {
        'MAP_SIZE_X': 32,
        'MAP_SIZE_Y': 16,
        'MAX_NUM_SECTIONS': 5,
        'MIN_NUM_SECTIONS': 3,
        'MAX_NUM_ROOMS': 4,
        'MIN_NUM_ROOMS': 3,

        'MIN_SECTION_SIZE': 7,
        'ROOM_PADDING': 1,
        'MIN_ROOM_FLOOR_SIZE': 3,

        'MIN_NUM_RATION': 1,
        'MAX_NUM_RATION': 3,
    }
}


class RogueExplore(object):
    def __init__(self, dungeon_generator, config, render=True):
        self.dungeon_generator = dungeon_generator
        self.config = config

        self.enable_rations_and_hunger = self.config['enable_rations_and_hunger']
        self.simply_terrains = self.config['simply_terrains']
        self.enable_history = self.config['enable_history']
        self.style = self.config['style']
        self.player_center = self.config['player_center']

        self.depth = self.config['depth']
        self.seed_range = self.config['seed_range']
        self.max_hunger = self.config['max_hunger']
        self.max_num_rations = self.config['max_num_rations']
        self.default_num_rations = self.config['default_num_rations']
        self.max_steps = self.config['max_steps']
        self.rewards = self.config['rewards']
        self.dungeon_params = self.config['dungeon_params']
        init_dungeon_params(self.dungeon_params)

        self.image_repr = ImageRepr(
            style=self.style,
            player_center=self.player_center,
            enable_history=self.enable_history,
            simply_terrains=self.simply_terrains,
        )
        self.reward_func = RewardFunc(self.rewards)

        self.dungeon = None
        self.steps = None
        self.num_rations = None
        self.hunger = None
        self.level = None
        self.last_reward_info = None

        self.seed = None
        self.initialized = False

        self.enable_render = render
        self.bg = None
        self.sv = None
        if self.enable_render:
            self.open_renderer()

    def observation_shape(self):
        size_y = self.config['dungeon_params']['MAP_SIZE_Y']
        size_x = self.config['dungeon_params']['MAP_SIZE_X']
        if self.player_center:
            img_shape = (size_y * 2 - 1, size_x * 2 - 1)
        else:
            img_shape = (size_y, size_x)

        if self.style == 'gray_scale':
            obs_shape = img_shape
        elif self.style == 'symbols':
            obs_shape = img_shape + (len(Symbols) + (1 if self.enable_history else 0),)
        else:
            assert False

        return (obs_shape, 2)

    def sample(self):
        return random.randint(0, self.n_actions-1)

    @property
    def n_actions(self):
        return 5

    @property
    def reward_classes(self):
        return self.rewards.keys()

    def open_renderer(self):
        self.bg = tk.Tk()
        self.bg.title("Rogue Explore")

        self.sv = tk.StringVar()
        label = tk.Label(textvariable=self.sv, justify="left", font="courier", foreground="white",
                              background='black')
        label.pack()
        self.last_reward_info = "None"
        self.enable_render = True

    def close_renderer(self):
        self.bg.destroy()

    def close(self):
        self.close_renderer()

    def render(self):
        assert self.enable_render, 'render is not enabled'
        assert self.initialized, 'call "reset()" before call "render()"'
        self.sv.set(self.dungeon.result +
                    f"\nseed:{self.seed}|level:{self.level}|steps:{self.steps}\n"
                    f"hunger:{self.hunger}|rations:{self.num_rations}\n"
                    f"reward:{self.last_reward_info}")
        self.bg.update()

    def reset(self):
        self.seed = random.randint(self.seed_range[0], self.seed_range[1] - 1)
        self.dungeon_generator.set_seed(self.seed)
        self.dungeon = self.dungeon_generator.make_dungeon()
        self.steps = 0
        self.num_rations = self.default_num_rations
        self.hunger = self.max_hunger
        self.level = 1
        self.last_reward_info = 'None'
        self.initialized = True

        if self.enable_rations_and_hunger:
            scaled_hunger = self.hunger / self.max_hunger
            scaled_num_rations = self.num_rations / self.max_num_rations
        else:
            scaled_hunger = 0
            scaled_num_rations = 0

        return (self.image_repr(self.dungeon), np.array([scaled_hunger, scaled_num_rations]))

    def step(self, action):
        assert self.initialized, 'call "reset()" before call "step()"'

        success_eat = False
        failure_eat = False
        moved = False
        get_ration = False
        reach_unreachable = False
        clear = False
        down_stair = False
        stuck = False

        self.steps += 1
        if self.enable_rations_and_hunger:
            self.hunger -= 1
        if action == 0:
            if self.enable_rations_and_hunger:
                success_eat = self.eat_ration()
                failure_eat = not success_eat
            else:
                failure_eat = True
        else:
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            moved, picked, reach_unreachable = self.dungeon.move(directions[action - 1])
            if picked == Symbols.RATION:
                self.num_rations = min(self.num_rations + 1, self.max_num_rations)
                get_ration = True
                moved = reach_unreachable = False
            elif picked == Symbols.STAIR:
                # 次の階層へ
                if self.level < self.depth:
                    self.next_floor()
                    down_stair = True
                else:
                    clear = True
                moved = reach_unreachable = False
            else:
                stuck = not moved
                moved = moved and not reach_unreachable

        reward, reward_info = self.reward_func(
            success_eat=success_eat, failure_eat=failure_eat, get_ration=get_ration, down_stair=down_stair,
            clear=clear, stuck=stuck, reach_unreachable=reach_unreachable, move=moved
        )

        if self.enable_rations_and_hunger:
            scaled_hunger = self.hunger / self.max_hunger
            scaled_num_rations = self.num_rations / self.max_num_rations
        else:
            scaled_hunger = 0
            scaled_num_rations = 0

        state = (self.image_repr(self.dungeon), np.array([scaled_hunger, scaled_num_rations]))

        done = (reward_info == 'clear') or (self.hunger == 0) or (self.steps == self.max_steps)

        info = {
            'reward_info': reward_info,
            'hunger': self.hunger,
            'num_rations': self.num_rations,
            'player_pos': self.dungeon.player_pos,
            'steps': self.steps,
            'dungeon_level': self.level
        }

        self.last_reward_info = reward_info
        return state, reward, done, info

    def next_floor(self):
        self.dungeon = self.dungeon_generator.make_dungeon()
        self.level += 1

    def eat_ration(self):
        if self.num_rations >= 1:
            self.hunger = self.max_hunger
            self.num_rations -= 1
            return True
        else:
            return False


def init_dungeon_params(config=DEFAULT_CONFIG['dungeon_params']):
    # from src.envs.rogueExplore import dungeonParams as dp
    from rogue_explore import dungeon_params as dp
    dp.MAP_SIZE_X = config['MAP_SIZE_X']
    dp.MAP_SIZE_Y = config['MAP_SIZE_Y']
    dp.MAX_NUM_SECTIONS = config['MAX_NUM_SECTIONS']
    dp.MIN_NUM_SECTIONS = config['MIN_NUM_SECTIONS']
    dp.MAX_NUM_ROOMS = config['MAX_NUM_ROOMS']
    dp.MIN_NUM_ROOMS = config['MIN_NUM_ROOMS']

    dp.MIN_SECTION_SIZE = config['MIN_SECTION_SIZE']
    dp.ROOM_PADDING = config['ROOM_PADDING']
    dp.MIN_ROOM_FLOOR_SIZE = config['MIN_ROOM_FLOOR_SIZE']

    dp.MIN_NUM_RATION = config['MIN_NUM_RATION']
    dp.MAX_NUM_RATION = config['MAX_NUM_RATION']


if __name__ == "__main__":
    conf = {
        'enable_rations_and_hunger': True,
        'simply_terrains': True,
        'enable_history': True,
        'style': 'symbols',
        'player_center': True,
        'depth': 10,
        'seed_range': [0, 1],
        'max_hunger': 100,
        'max_num_rations': 5,
        'default_num_rations': 0,
        'max_steps': 3000,
        'rewards': {
            "clear": 1,
            "down_stair": 2,
            "success_eat": 3,
            "failure_eat": 4,
            "get_ration": 5,
            "reach_unreachable": 6,
            "stuck": 7,
            "move": 8,
        },
        'dungeon_params': {
            'MAP_SIZE_X': 32,
            'MAP_SIZE_Y': 16,
            'MAX_NUM_SECTIONS': 5,
            'MIN_NUM_SECTIONS': 3,
            'MAX_NUM_ROOMS': 4,
            'MIN_NUM_ROOMS': 3,

            'MIN_SECTION_SIZE': 7,
            'ROOM_PADDING': 1,
            'MIN_ROOM_FLOOR_SIZE': 3,

            'MIN_NUM_RATION': 1,
            'MAX_NUM_RATION': 3,
        }
    }

    _dungeon_generator = DungeonGenerator(conf['enable_rations_and_hunger'], pooling=True, depth=10, seed_range=conf['seed_range'])
    _rogue_explore = RogueExplore(_dungeon_generator, config=conf, render=True)
