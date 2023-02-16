import time
from rogue_explore import RogueExplore, DEFAULT_CONFIG, DungeonGenerator


if __name__ == "__main__":
    # create env
    dg = DungeonGenerator(
        place_rations=DEFAULT_CONFIG['enable_rations_and_hunger'],
        pooling=True,
        depth=DEFAULT_CONFIG['depth'],
        seed_range=DEFAULT_CONFIG['seed_range']
    )
    env = RogueExplore(dungeon_generator=dg, config=DEFAULT_CONFIG, render=True)

    # loop
    for i in range(10):
        env.reset()
        done = False
        while not done:
            action = env.sample()
            state, reward, done, _ = env.step(action)
            env.render()
            time.sleep(.1)
