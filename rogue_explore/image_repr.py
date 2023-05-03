import numpy as np

# from src.envs.rogueExplore.dungeon import Symbols

from rogue_explore.dungeon import Symbols


class ImageRepr(object):
    def __init__(self, style, player_center, enable_history, simply_terrains):
        assert not (style == 'gray_scale' and enable_history), 'do not use history with gray style'
        self.style = style
        self.player_center = player_center
        self.enable_history = enable_history
        self.simply_terrains = simply_terrains
        if self.style == 'gray_scale':
            self.repr_func = self._gray_scale
        elif self.style == 'symbols':
            self.repr_func = self._symbols
        else:
            assert False, 'style has illegal value'

    def __call__(self, dungeon):
        if self.simply_terrains:
            layers: np.ndarray = dungeon.simple_symbol_map(self.enable_history)
            layers[..., [0, 1]] *= 1 - np.sum(layers[..., [2,3,4]], axis=2, keepdims=True)
        else:
            layers: np.ndarray = dungeon.symbol_map(self.enable_history)
            layers[..., Symbols.terrain_values()] *= 1 - np.sum(layers[..., Symbols.object_values()], axis=2, keepdims=True)
        if self.player_center:
            size_y, size_x = dungeon.image_shape
            player_pos = dungeon.player_pos
            padding = (
                (size_y - 1 - player_pos[0], player_pos[0]),
                (size_x - 1 - player_pos[1], player_pos[1]),
            )
            layers = np.dstack(
                [
                    np.pad(layers[..., 0], padding, mode='constant', constant_values=1),
                    np.pad(layers[..., 1:], padding + ((0, 0), ), mode='constant', constant_values=0)
                ]
            )
        return self.repr_func(layers)

    @staticmethod
    def _gray_scale(layers):
        c = layers.shape[-1] - 1
        # return np.argmax(layers, axis=2) / c
        return np.divide(np.argmax(layers, axis=2), c, dtype=np.float32)[..., np.newaxis]

    @staticmethod
    def _symbols(layers):
        return layers.astype(np.float32)
