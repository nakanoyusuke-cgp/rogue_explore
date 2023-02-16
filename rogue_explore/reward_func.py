import numpy as np


class RewardFunc(object):
    def __init__(self, reward_dict):
        self.rewards = reward_dict

    def __call__(self, *args, **kwargs):
        reward_cand = [(self.rewards[k], k) for k, v in kwargs.items() if v == 1]
        assert len(reward_cand) == 1, "rewards is not onehot"
        return reward_cand[0]


if __name__ == '__main__':
    pass
