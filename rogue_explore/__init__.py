from rogue_explore.rogue_explore import RogueExplore, DEFAULT_CONFIG, init_dungeon_params
from rogue_explore.dungeon_generator import DungeonGenerator
from rogue_explore.dungeon import Symbols, directions, characters, Dungeon

from gym.envs.registration import register
from rogue_explore.wrapper import RogueExploreWrapper


register(
    id='RogueExplore-v0',
    entry_point="rogue_explore.wrapper:RogueExploreWrapper"
)
