import gym
from gym.spaces import Tuple, Discrete, Box
import numpy as np

from rogue_explore.rogue_explore import RogueExplore, DEFAULT_CONFIG
from rogue_explore.dungeon_generator import DungeonGenerator


class RogueExploreWrapper(gym.Env):
    def __init__(self, config=None, enable_renderer=True, enable_map_pooling=True):
        if config is None:
            self.config = DEFAULT_CONFIG
        else:
            self.config = config

        self.enable_renderer = enable_renderer
        self.enable_map_pooling = enable_map_pooling

        self.dg = DungeonGenerator(
            place_rations=config['enable_rations_and_hunger'],
            pooling=enable_map_pooling,
            depth=DEFAULT_CONFIG['depth'],
            seed_range=DEFAULT_CONFIG['seed_range']
        )

        self.env = RogueExplore(dungeon_generator=self.dg, config=config, render=enable_renderer)

        self.action_space = Discrete(self.env.n_actions)
        obs_shape = self.env.observation_shape()
        self.observation_space = Tuple((
            Box(0, 1, obs_shape[0], np.float32),
            Box(0, 1, (obs_shape[1],), np.float32),
        ))

    def reset(self, **kwargs):
        return self.env.reset()

    def step(self, action):
        return self.env.step(action)

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
