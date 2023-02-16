from rogue_explore.rogue_explore import RogueExplore, DEFAULT_CONFIG, init_dungeon_params, human_play
from rogue_explore.dungeon_generator import DungeonGenerator
from rogue_explore.dungeon import Symbols, directions, characters, Dungeon

from gym.envs.registration import register


register(
    id='RogueExplore-v0',
    entry_point="rogue_explore.rogue_explore:RogueExploreWrapper"
)
