import itertools

# from src.envs.rogueExplore.room import Room
# from src.envs.rogueExplore.dungeonParams import *

from rogue_explore.room import Room
from rogue_explore.dungeon_params import *

# MIN_SECTION_SIZE = 7
# ROOM_PADDING = 1
# MIN_ROOM_FLOOR_SIZE = 3


class Section(object):
    def __init__(self, size_y, size_x, pos_y, pos_x):
        self.size_y = size_y
        self.size_x = size_x
        self.pos1_y = pos_y
        self.pos1_x = pos_x

        self.has_children = False
        self.divider = None
        self.divider_axis = None
        self.left_section = None
        self.right_section = None

        self.has_room = False
        self.room = None
        self.routes = []
        self.aisles = []

    @property
    def pos2_y(self):
        return self.pos1_y + self.size_y - 1

    @property
    def pos2_x(self):
        return self.pos1_x + self.size_x - 1

    def _can_divide_y(self):
        return self.size_y >= MIN_SECTION_SIZE * 2 + 1

    def _can_divide_x(self):
        return self.size_x >= MIN_SECTION_SIZE * 2 + 1

    def can_divide(self):
        if self.has_children:
            return self.left_section.can_divide() or self.right_section.can_divide()
        else:
            return self._can_divide_x() or self._can_divide_y()

    def divide(self, rng):
        if self.has_children:
            left_can_divide = self.left_section.can_divide()
            right_can_divide = self.right_section.can_divide()
            assert left_can_divide or right_can_divide, "child sections can not divide"
            if left_can_divide and right_can_divide:  # left and right True
                divide_section = rng.choice([self.right_section, self.left_section])
            elif left_can_divide:  # left True
                divide_section = self.left_section
            elif right_can_divide:  # right True
                divide_section = self.right_section
            else:
                assert False, "child sections can not divide"

            divide_section.divide(rng)

        else:
            can_divide_y = self._can_divide_y()
            can_divide_x = self._can_divide_x()
            assert can_divide_y or can_divide_x, "this section can not divide"
            if can_divide_y and can_divide_x:  # y and x True
                self.divider_axis = rng.randint(0, 1)
            elif can_divide_y:  # y True
                self.divider_axis = 0
            elif can_divide_x:  # x True
                self.divider_axis = 1
            else:
                assert False, "this section can not divide"

            divider_range = [self.size_y, self.size_x][self.divider_axis] - 1 - MIN_SECTION_SIZE * 2
            self.divider = rng.randint(0, divider_range)

            left_params, right_params = self.calc_children_transforms()

            self.left_section = Section(*left_params)
            self.right_section = Section(*right_params)

            self.has_children = True

    def enumerate_dividers(self):
        if self.has_children:
            return self.left_section.enumerate_dividers() + self.right_section.enumerate_dividers() + [self]
        else:
            return []

    def enumerate_leaf_sections(self):
        if self.has_children:
            return self.left_section.enumerate_leaf_sections() + self.right_section.enumerate_leaf_sections()
        else:
            return [self]

    def make_room(self, rng):
        # size: 壁も含めた大きさ
        room_size_y = rng.randint(MIN_ROOM_FLOOR_SIZE + 2, self.size_y - ROOM_PADDING * 2)
        room_size_x = rng.randint(MIN_ROOM_FLOOR_SIZE + 2, self.size_x - ROOM_PADDING * 2)
        pos_range_y = self.size_y - room_size_y
        pos_range_x = self.size_x - room_size_x
        assert pos_range_y >= 0, f"pos_range_y={pos_range_y}"
        assert pos_range_x >= 0, f"pos_range_x={pos_range_x}"
        room_pos_y = rng.randint(ROOM_PADDING, pos_range_y - ROOM_PADDING) + self.pos1_y
        room_pos_x = rng.randint(ROOM_PADDING, pos_range_x - ROOM_PADDING) + self.pos1_x
        self.room = Room(size_y=room_size_y, size_x=room_size_x, pos_y=room_pos_y, pos_x=room_pos_x)
        self.has_room = True

    def recalculate_transform(self):
        if self.has_children:
            left_params, right_params = self.calc_children_transforms()
            self.left_section.apply_transform(*left_params)
            self.right_section.apply_transform(*right_params)
            self.left_section.recalculate_transform()
            self.right_section.recalculate_transform()

    def apply_transform(self, size_y, size_x, pos_y, pos_x):
        assert self.size_y <= size_y
        assert self.size_x <= size_x
        assert self.pos1_y >= pos_y
        assert self.pos1_x >= pos_x
        if self.divider_axis == 0 and not pos_y == self.pos1_y:
            self.divider += self.pos1_y - pos_y
        if self.divider_axis == 1 and not pos_x == self.pos1_x:
            self.divider += self.pos1_x - pos_x

        self.size_y = size_y
        self.size_x = size_x
        self.pos1_y = pos_y
        self.pos1_x = pos_x

    def calc_children_transforms(self):
        if self.divider_axis == 0:
            left_size_y = MIN_SECTION_SIZE + self.divider
            left_size_x = self.size_x
            left_pos_y = self.pos1_y
            left_pos_x = self.pos1_x
            right_size_y = self.size_y - 1 - left_size_y
            right_size_x = self.size_x
            right_pos_y = self.pos1_y + 1 + left_size_y
            right_pos_x = self.pos1_x
        elif self.divider_axis == 1:
            left_size_y = self.size_y
            left_size_x = MIN_SECTION_SIZE + self.divider
            left_pos_y = self.pos1_y
            left_pos_x = self.pos1_x
            right_size_y = self.size_y
            right_size_x = self.size_x - 1 - left_size_x
            right_pos_y = self.pos1_y
            right_pos_x = self.pos1_x + 1 + left_size_x
        else:
            assert False, "divider_axis has illegal value."
        return (left_size_y, left_size_x, left_pos_y, left_pos_x), (
            right_size_y, right_size_x, right_pos_y, right_pos_x)

    def reduce_sections_not_contains_any_rooms(self):
        if self.has_children:
            self.left_section = self.left_section.reduce_sections_not_contains_any_rooms()
            self.right_section = self.right_section.reduce_sections_not_contains_any_rooms()

            if (self.left_section is None) and (self.right_section is None):  # 両方部屋無し
                return None
            elif self.right_section is None:  # 左部屋あり
                alt_section = self.left_section
            elif self.left_section is None:  # 右部屋あり
                alt_section = self.right_section
            else:  # 両部屋あり
                return self

            # 片部屋の場合の処理
            alt_section.apply_transform(self.size_y, self.size_x, self.pos1_y, self.pos1_x)
            return alt_section

        else:
            if self.has_room:
                return self
            else:
                return None

    def find_candidate_routes(self):
        if not self.has_children:
            return {'': self}
        else:
            axis = ["V", "H"][self.divider_axis]
            left_tag = axis + "l"
            right_tag = axis + "r"

            lefts = self.left_section.find_candidate_routes()
            rights = self.right_section.find_candidate_routes()

            # tagが含まれないkeyを持つ部屋持ちセクションを取り出し
            left_candidate_sections = [v for (k, v) in lefts.items() if left_tag not in k]
            right_candidate_sections = [v for (k, v) in rights.items() if right_tag not in k]

            self.routes = []
            # 分割線左右の部屋持ちセクションすべての組み合わせを列挙
            candidate_routes = itertools.product(left_candidate_sections, right_candidate_sections)
            for left, right in candidate_routes:
                if self.divider_axis == 0:
                    cond_rrls1 = right.room.pos2_x - 1 - left.pos1_x >= 0
                    cond_rrls2 = left.pos2_x - 1 - right.room.pos1_x >= 0
                    cond_rslr1 = left.room.pos2_x - 1 - right.pos1_x >= 0
                    cond_rslr2 = right.pos2_x - 1 - left.room.pos1_x >= 0
                elif self.divider_axis == 1:
                    cond_rrls1 = right.room.pos2_y - 1 - left.pos1_y >= 0
                    cond_rrls2 = left.pos2_y - 1 - right.room.pos1_y >= 0
                    cond_rslr1 = left.room.pos2_y - 1 - right.pos1_y >= 0
                    cond_rslr2 = right.pos2_y - 1 - left.room.pos1_y >= 0
                else:
                    assert False, "divider axis is illegal" + self.divider_axis

                # この分割線上に通路を作ることができる条件を満たしたセクションの組み合わせを格納
                if cond_rrls1 and cond_rrls2 and cond_rslr1 and cond_rslr2:
                    self.routes.append((left, right))

            assert len(self.routes) >= 1, "available route not found"

            res_left = {axis + "l" + l_key: l_value for l_key, l_value in lefts.items()}
            res_right = {axis + "r" + r_key: r_value for r_key, r_value in rights.items()}
            return {**res_left, **res_right}

    def make_route(self, rng):
        assert self.has_children, "this section does not have children"
        assert len(self.routes) >= 1, "this section does not have any routes"

        t = rng.choice(self.routes)
        left, right = t
        self.routes.remove(t)

        if self.divider_axis == 0:
            part_div_start = max(left.pos1_x, right.pos1_x)
            part_div_end = min(left.pos2_x, right.pos2_x)
            left_range_1 = max(part_div_start, left.room.pos1_x + 1)
            left_range_2 = min(part_div_end, left.room.pos2_x - 1)
            right_range_1 = max(part_div_start, right.room.pos1_x + 1)
            right_range_2 = min(part_div_end, right.room.pos2_x - 1)
            left_pos = rng.randint(left_range_1, left_range_2)
            right_pos = rng.randint(right_range_1, right_range_2)
            x0 = left_pos
            x1 = right_pos
            y0 = left.room.pos2_y
            y1 = left.pos2_y + 1
            y2 = right.room.pos1_y
            aisle = [
                (y0, x0), (y1, x0), (y1, x1), (y2, x1)
            ]
        elif self.divider_axis == 1:
            part_div_start = max(left.pos1_y, right.pos1_y)
            part_div_end = min(left.pos2_y, right.pos2_y)
            left_range_1 = max(part_div_start, left.room.pos1_y + 1)
            left_range_2 = min(part_div_end, left.room.pos2_y - 1)
            right_range_1 = max(part_div_start, right.room.pos1_y + 1)
            right_range_2 = min(part_div_end, right.room.pos2_y - 1)
            left_pos = rng.randint(left_range_1, left_range_2)
            right_pos = rng.randint(right_range_1, right_range_2)
            x0 = left.room.pos2_x
            x1 = left.pos2_x + 1
            x2 = right.room.pos1_x
            y0 = left_pos
            y1 = right_pos
            aisle = [
                (y0, x0), (y0, x1), (y1, x1), (y1, x2)
            ]
        else:
            assert False, "divider axis is illegal" + self.divider_axis

        self.aisles.append(aisle)


if __name__ == "__main__":
    pass
