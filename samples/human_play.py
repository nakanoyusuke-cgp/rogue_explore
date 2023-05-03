import readchar
from rogue_explore import RogueExplore, DEFAULT_CONFIG, DungeonGenerator

import gym
import rogue_explore

"""
このプログラムを実行するためには「readchar」というPythonパッケージをインストールする必要があります。
また、キー入力はGUIではなくコンソールに対して行うようにしてください。

キーとアクションの対応：
- w: 上に移動
- a: 左に移動
- s: 下に移動
- d: 右に移動
- e: 食料を使用
- q: プログラムを終了


This program requires to install the python package "readchar".
Keystrokes must be made to the console, not to the GUI.

Key to Action Mapping:
- w: Move up
- a: Move left
- s: Move down
- d: Move right
- e: eat ration
- q: quit the process
"""

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
    env.reset()
    env.render()
    done = False
    while not done:
        key_map = {"w": 3, "a": 4, "s": 1, "d": 2, "e": 0, "q": 5}
        try:
            action = key_map[readchar.readkey()]
        except KeyError:
            continue

        if action == 5:
            break

        state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        # # if you are using old version of gym package or use RogueExplore interface,
        # # please use this "step" method instead.
        # state, reward, done, info = env.step(action)

        env.render()

    env.close()
