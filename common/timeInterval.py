from enum import IntEnum


class Bracket(IntEnum):
    RO = 1
    LC = 2
    RC = 3
    LO = 4


class BracketNum:
    def __init__(self, value, bracket):
        self.value = value
        self.bracket = bracket

    def __eq__(self, bn):
        if self.value == '+' and bn.value == '+':
            return True
        elif self.value == '+' and bn.value != '+':
            return False
        elif self.value != '+' and bn.value == '+':
            return False
        elif float(self.value) == float(bn.value) and self.bracket == bn.bracket:
            return True
        else:
            return False

    def complement(self):
        if self.value == '+':
            return BracketNum('+', Bracket.RO)  # ceil
        if float(self.value) == 0 and self.bracket == Bracket.LC:
            return BracketNum('0', Bracket.LC)  # floor
        tempValue = self.value
        tempBracket = None
        if self.bracket == Bracket.LC:
            tempBracket = Bracket.RO
        if self.bracket == Bracket.RC:
            tempBracket = Bracket.LO
        if self.bracket == Bracket.LO:
            tempBracket = Bracket.RC
        if self.bracket == Bracket.RO:
            tempBracket = Bracket.LC
        return BracketNum(tempValue, tempBracket)

    def __lt__(self, bn):
        if self.value == '+':
            return False
        elif bn.value == '+':
            return True
        elif float(self.value) > float(bn.value):
            return False
        elif float(self.value) < float(bn.value):
            return True
        else:
            if self.bracket < bn.bracket:
                return True
            else:
                return False

    def getBN(self):
        if self.bracket == Bracket.LC:
            return '[' + self.value
        if self.bracket == Bracket.LO:
            return '(' + self.value
        if self.bracket == Bracket.RC:
            return self.value + ']'
        if self.bracket == Bracket.RO:
            return self.value + ')'


# time guard类
class Guard:
    def __init__(self, guard):
        self.guard = guard
        self.__build()

    def __build(self):
        min_type, max_type = self.guard.split(',')

        # 处理左边
        if min_type[0] == '[':
            self.closed_min = True
            min_bn_bracket = Bracket.LC
        else:
            self.closed_min = False
            min_bn_bracket = Bracket.LO
        self.min_value = min_type[1:].strip()
        self.min_bn = BracketNum(self.min_value, min_bn_bracket)

        # 处理右边
        if max_type[-1] == ']':
            self.closed_max = True
            max_bn_bracket = Bracket.RC
        else:
            self.closed_max = False
            max_bn_bracket = Bracket.RO
        self.max_value = max_type[:-1].strip()
        self.max_bn = BracketNum(self.max_value, max_bn_bracket)

    def __eq__(self, constraint):
        if self.min_value == constraint.min_value and self.closed_min == constraint.closed_min and self.max_value == constraint.max_value and self.closed_max == constraint.closed_max:
            return True
        else:
            return False

    def isInInterval(self, num):
        if num < self.get_min():
            return False
        elif num == self.get_min():
            if self.closed_min:
                return True
            else:
                return False
        elif self.get_min() < num < self.get_max():
            return True
        elif num == self.get_max():
            if self.closed_max:
                return True
            else:
                return False
        else:
            return False

    def get_min(self):
        return float(self.min_value)

    def get_closed_min(self):
        return self.closed_min

    def get_max(self):
        if self.max_value == '+':
            return float("inf")
        else:
            return float(self.max_value)

    def get_closed_max(self):
        return self.closed_max

    def show(self):
        return self.guard
