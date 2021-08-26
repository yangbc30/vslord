import re
import utils


##########
# vslord #
##########

@utils.timing
def is_valid(cards, current_cards=None):  # feature_dict {5:4, 6:3}
    feature_str = cards.feature_str
    feature_dict = cards.feature_dict
    curr_pattern = current_cards.pattern if current_cards else None
    curr_value = current_cards.value if current_cards else None

    value = None
    valid = False

    def then(pattern, value):
        if curr_pattern:
            if curr_pattern != "4" and curr_pattern != "11" and (pattern == "4" or pattern == "11"):
                return set_true(pattern, value)
            elif value > curr_value:
                return set_true(pattern, value)
            else:
                return set_false()
        else:
            return set_true(pattern, value)

    def set_true(pattern, value):
        cards.pattern = pattern
        cards.value = value
        cards.valid = True
        return True

    def set_false():
        cards.pattern = None
        cards.value = None
        cards.valid = False
        return False

    # 单张
    pattern = "1"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "1":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    # 一对
    pattern = "2"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "2":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    # 三张
    pattern = "3"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "3":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    # 三张带一张
    pattern = "31"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "31":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    # 三张带一对
    pattern = "32"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "32":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    # 顺子
    pattern = r"^1{5,}$"
    if not curr_pattern or curr_pattern == pattern:
        if re.match(pattern, feature_str) is not None:
            length = len(feature_str)
            keys = list(feature_dict.keys())
            if keys[0] <= 12 and keys[0] - keys[length - 1] == length - 1:
                pattern = pattern
                value = keys[0]
                return then(pattern, value)

    # 连对
    pattern = r"^2{3,}$"
    if not curr_pattern or curr_pattern == pattern:
        if re.match(pattern, feature_str) is not None:
            length = len(feature_str)
            keys = list(feature_dict.keys())
            if keys[0] <= 12 and keys[0] - keys[length - 1] == length - 1:
                pattern = pattern
                value = keys[0]
                return then(pattern, value)

    # 三张的顺子
    pattern = r"^3{2,}$"
    if not curr_pattern or curr_pattern == pattern:
        if re.match(pattern, feature_str) is not None:
            length = len(feature_str)
            keys = list(feature_dict.keys())
            if keys[0] <= 12 and keys[0] - keys[length - 1] == length - 1:
                pattern = pattern
                value = keys[0]
                return then(pattern, value)

    # 三张带一张的顺子
    pattern = r"^(3{2,})(1{2,})$"
    if not curr_pattern or curr_pattern == pattern:
        match_result = re.match(pattern, feature_str)
        if match_result is not None:
            length_3 = len(match_result.group(1))
            length_1 = len(match_result.group(2))
            if length_3 == length_1:
                keys = list(feature_dict.keys())
                if keys[0] <= 12 and keys[0] - keys[length_3 - 1] == length_3 - 1:
                    pattern = pattern
                    value = keys[0]
                    return then(pattern, value)

    # 三张带两张的顺子
    pattern = r"^(3{2,})(2{2,})$"
    if not curr_pattern or curr_pattern == pattern:
        match_result = re.match(pattern, feature_str)
        if match_result is not None:
            length_3 = len(match_result.group(1))
            length_1 = len(match_result.group(2))
            if length_3 == length_1:
                keys = list(feature_dict.keys())
                if keys[0] <= 12 and keys[0] - keys[length_3 - 1] == length_3 - 1:
                    pattern = pattern
                    value = keys[0]
                    return then(pattern, value)

    # 炸弹
    pattern = "4"
    if feature_str == "4":
        value = list(feature_dict.keys())[0]
        return then(pattern, value)

    # 火箭
    pattern = "11"
    if feature_str == "11":
        keys = list(feature_dict.keys())
        if keys[0] == 15 and keys[1] == 14:
            value = keys[0]
            return then(pattern, value)

    # 四带二
    pattern = "42"
    if not curr_pattern or curr_pattern == pattern:
        if feature_str == "42":
            value = list(feature_dict.keys())[0]
            return then(pattern, value)

    return set_false()
