import common.timeInterval_upper as timeInterval_upper


# RTA
class RTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState

    def show(self):
        print("Input: " + str(self.inputs))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.initState))
        print("AcceptStates: {}".format(self.acceptStates))
        print("SinkState: {}".format(self.sinkState))
        print("Transitions: ")
        for t in self.trans:
            print("  " + str(t.tranId), 'S_' + str(t.source), t.input, t.showGuards(), 'S_' + str(t.target), end="\n")


# RTATran
class RTATran(object):
    def __init__(self, tranId, source, input, guards, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.guards = guards
        self.target = target

    def isPass(self, tw):
        if tw.input == self.input:
            for guard in self.guards:
                if guard.isInInterval(tw.time):
                    return True
        else:
            return False
        return False

    def showGuards(self):
        length = len(self.guards)
        if length == 0:
            return "[0,+)"
        else:
            temp = self.guards[0].guard
            for i in range(1, length):
                temp = temp + 'U' + self.guards[i].guard
            return temp


def structHypothesisRTA(table, inputs):
    symbolList = table.symbolList
    # input处理
    inputs = inputs
    # states/initState/acceptStates处理
    states = []
    initState = None
    sinkState = None
    acceptStates = []
    valueList_name_dict = {}
    for s, i in zip(table.S, range(len(table.S))):
        stateName = str(i)
        valueList_name_dict[makeStr(s.valueList)] = stateName
        states.append(stateName)
        if not s.stws:
            initState = stateName
        if s.valueList[0] == 1:
            acceptStates.append(stateName)
        if s.valueList[0] == -1:
            sinkState = stateName
    # 迁移处理
    trans = []
    transNum = 0
    tableElements = [s for s in table.S] + [r for r in table.R]
    for r in tableElements:
        if not r.stws:
            continue
        symbolTimedWords = [stw for stw in r.stws]
        w = symbolTimedWords[:-1]
        a = symbolTimedWords[len(symbolTimedWords) - 1]
        source = None
        target = None
        for element in tableElements:
            if w == element.stws:
                source = valueList_name_dict[makeStr(element.valueList)]
            if symbolTimedWords == element.stws:
                target = valueList_name_dict[makeStr(element.valueList)]
        # 确认迁移input和guard
        input = symbolList[a].input
        guard = symbolList[a].guard
        # 迁移添加
        needNewTran = True
        for tran in trans:
            if source == tran.source and input == tran.input and target == tran.target:
                tran.guards.append(guard)
                needNewTran = False
                break
        if needNewTran:
            tempTran = RTATran(transNum, source, input, [guard], target)
            trans.append(tempTran)
            transNum = transNum + 1
    for tran in trans:
        if len(tran.guards) > 0:
            tran.guards = simpleGuards(tran.guards)
    hypothesisRTA = RTA(inputs, states, trans, initState, acceptStates, sinkState)
    return hypothesisRTA


# --------------------------------- 辅助函数 ---------------------------------

# valueList改为str
def makeStr(valueList):
    valueStr = ''
    for v in valueList:
        valueStr = valueStr + str(v)
    return valueStr


# Guards合并
def simpleGuards(guards):
    newGuards = []
    minList = []
    maxList = []
    for i in guards:
        minNum, maxNum = i.guard[1:-1].split(',')
        minList.append(float(minNum))
        maxList.append(float(maxNum))
    minList.sort()
    maxList.sort()
    intersection = list(set(minList).intersection(set(maxList)))
    for m in intersection:
        if m in minList:
            minList.remove(m)
        if m in maxList:
            maxList.remove(m)
    for n in range(len(minList)):
        tempGuard = timeInterval_upper.Guard("[" + str(minList[n]) + "," + str(maxList[n]) + ")")
        newGuards.append(tempGuard)
    return newGuards
