import gym
from gym.spaces import Tuple, Discrete, Box
import numpy as np

from rogue_explore.rogue_explore import RogueExplore, DEFAULT_CONFIG
from rogue_explore.dungeon_generator import DungeonGenerator


class RogueExploreWrapper(gym.Env):
    def __init__(self, config=None, enable_renderer=True, enable_map_pooling=True):
        if config is None:
            config = DEFAULT_CONFIG

        self.config = config
        self.enable_renderer = enable_renderer
        self.enable_map_pooling = enable_map_pooling

        self.dg = DungeonGenerator(
            place_rations=config['enable_rations_and_hunger'],
            pooling=enable_map_pooling,
            depth=config['depth'],
            seed_range=config['seed_range']
        )

        self.env = RogueExplore(dungeon_generator=self.dg, config=config, render=enable_renderer)

        self.action_space = Discrete(self.env.n_actions)
        obs_shape = self.env.observation_shape()
        self.observation_space = Box(0, 255, obs_shape[0], np.uint8)

    def reset(self, **kwargs):
        s = self.env.reset()[0]
        info = {
            'reward_info': "None",
            'hunger': self.hunger,
            'num_rations': self.num_rations,
            'player_pos': self.env.dungeon.player_pos,
            'steps': self.env.steps,
            'dungeon_level': self.env.level
        }
        return self.discrete_image(s), info

    def step(self, action):
        s, r, d, i = self.env.step(action)
        terminated = d and (i["reward_info"] == "clear")
        truncated = d and (i["reward_info"] != "clear")
        return self.discrete_image(s[0]), r, terminated, truncated, i

    def render(self):
        return self.env.render()

    def close(self):
        return self.env.close_renderer()

    def seed(self, seed=None):
        """
        ダンジョン生成器のシードを指定する。
        "enable_map_pooling"が"False"の場合のみ動作する。
        "seed=None"の場合何も処理を行わない。
        :param seed: 生成されるダンジョンのseed
        """
        if (seed is not None) and (not self.enable_map_pooling):
            self.dg.set_seed(seed)

    def sample(self):
        self.env.sample()

    @property
    def num_rations(self):
        return self.env.num_rations

    @property
    def max_num_rations(self):
        return self.env.max_num_rations

    @property
    def hunger(self):
        return self.env.hunger

    @property
    def max_hunger(self):
        return self.env.max_hunger

    @staticmethod
    def discrete_image(img):
        return (img * 256).astype(np.uint8)
