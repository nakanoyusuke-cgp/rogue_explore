import time
from rogue_explore import RogueExplore, DEFAULT_CONFIG, DungeonGenerator

import gymnasium as gym
import rogue_explore


if __name__ == "__main__":
    # create env
    env = gym.make("RogueExplore-v0")

    # # RogueExplore interface
    # dg = DungeonGenerator(
    #     place_rations=DEFAULT_CONFIG['enable_rations_and_hunger'],
    #     pooling=True,
    #     depth=DEFAULT_CONFIG['depth'],
    #     seed_range=DEFAULT_CONFIG['seed_range']
    # )
    # env = RogueExplore(dungeon_generator=dg, config=DEFAULT_CONFIG, render=True)

    # loop
    for i in range(5):
        env.reset()
        done = False
        while not done:
            action = env.action_space.sample()

            # # RogueExplore interface
            # action = env.sample()

            state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # # if you are using old version of gym package or use RogueExplore interface,
            # # please use this "step" method instead.
            # state, reward, done, info = env.step(action)

            env.render()
            time.sleep(.1)

    env.close()
