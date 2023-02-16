import gym

from rogue_explore.rogue_explore import RogueExplore, DEFAULT_CONFIG
from rogue_explore.dungeon_generator import DungeonGenerator


class RogueExploreWrapper(gym.Env):
    def __init__(self, config=None, enable_renderer=True, enable_map_pooling=True):
        if config is None:
            config = DEFAULT_CONFIG

        dg = DungeonGenerator(
            place_rations=config['enable_rations_and_hunger'],
            pooling=enable_map_pooling,
            depth=DEFAULT_CONFIG['depth'],
            seed_range=DEFAULT_CONFIG['seed_range']
        )

        env = RogueExplore(dungeon_generator=dg, config=config, render=enable_renderer)

        action_space = None
        observation_space = None

    def reset(self, **kwargs):
        pass

    def step(self, action):
        pass

    def render(self):
        pass

    def close(self):
        pass

    def seed(self, seed=None):
        pass
