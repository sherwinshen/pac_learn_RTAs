class TimedWord(object):
    def __init__(self, action, time):
        self.input = action
        self.time = time

    def __eq__(self, tw):
        if self.input == tw.input and self.time == tw.time:
            return True
        else:
            return False

    def show(self):
        return "(" + self.input + "," + str(self.time) + ")"


class SymbolTimedWord(object):
    symbolId = 0

    def __init__(self, input, guard, evidences, representation):
        self.input = input
        self.symbolId = SymbolTimedWord.symbolId
        self.guard = guard  # guard类
        self.evidences = evidences  # {timePoint:value}
        self.representation = representation  # timePoint
        SymbolTimedWord.symbolId += 1

    def show(self):
        return "(" + self.input + "," + str(self.representation) + ")"
