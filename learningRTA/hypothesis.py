import math
import common.timeInterval_upper as timeInterval_upper


class RTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState

    def showDiscreteRTA(self):
        print("Input: " + str(self.inputs))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.initState))
        print("AcceptStates: {}".format(self.acceptStates))
        print("SinkState: {}".format(self.sinkState))
        print("Transitions: ")
        for t in self.trans:
            print(' ' + str(t.tranId), 'S_' + str(t.source), t.input, str(t.timeList), 'S_' + str(t.target), end="\n")

    def showRTA(self):
        print("Input: " + str(self.inputs))
        print("States: " + str(self.states))
        print("InitState: {}".format(self.initState))
        print("AcceptStates: {}".format(self.acceptStates))
        print("SinkState: {}".format(self.sinkState))
        print("Transitions: ")
        for t in self.trans:
            print("  " + str(t.tranId), 'S_' + str(t.source), t.input, t.showGuards(), 'S_' + str(t.target), end="\n")


class DiscreteRTATran(object):
    def __init__(self, tranId, source, input, timeList, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.timeList = timeList
        self.target = target


class RTATran(object):
    def __init__(self, tranId, source, input, guards, evidence, target):
        self.tranId = tranId
        self.source = source
        self.input = input
        self.guards = guards
        self.evidence = evidence
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
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


# 离散RTA构建
def structDiscreteRTA(table, inputs):
    # input处理
    inputs = inputs
    # states/initState/acceptStates处理
    states = []
    initState = None
    sinkState = None
    acceptStates = []
    valueList_name_dict = {}
    for s, i in zip(table.S, range(0, len(table.S))):
        stateName = i
        valueList_name_dict[makeStr(s.valueList)] = stateName
        states.append(stateName)
        if not s.tws:
            initState = stateName
        if s.valueList[0] == 1:
            acceptStates.append(stateName)
        if s.valueList[0] == -1:
            sinkState = stateName
    # trans处理
    trans = []
    transNum = 0
    tableElements = [s for s in table.S] + [r for r in table.R]
    source = None
    target = None
    for r in tableElements:
        if not r.tws:
            continue
        timedWords = [tw for tw in r.tws]
        w = timedWords[:-1]
        a = timedWords[len(timedWords) - 1]
        for element in tableElements:
            if isTwsEqual(w, element.tws):
                source = valueList_name_dict[makeStr(element.valueList)]
            if isTwsEqual(timedWords, element.tws):
                target = valueList_name_dict[makeStr(element.valueList)]
        # 确认迁移input
        input = a.input
        timeList = [a.time]
        # 添加新迁移还是添加时间点
        needNewTran = True
        for tran in trans:
            if source == tran.source and input == tran.input and target == tran.target:
                if timeList[0] not in tran.timeList:
                    tran.timeList.append(timeList[0])
                    needNewTran = False
                else:
                    needNewTran = False
        if needNewTran:
            tempTran = DiscreteRTATran(transNum, source, input, timeList, target)
            trans.append(tempTran)
            transNum = transNum + 1
    discreteRTA = RTA(inputs, states, trans, initState, acceptStates, sinkState)
    return discreteRTA


# 猜测RTA构建1 - 边界值为具体测试过的值
def structHypothesisRTA(discreteRTA, upperGuard):
    inputs = discreteRTA.inputs
    states = discreteRTA.states
    initState = discreteRTA.initState
    acceptStates = discreteRTA.acceptStates
    sinkState = discreteRTA.sinkState
    # 迁移处理
    trans = []
    for s in discreteRTA.states:
        s_dict = {}
        for key in discreteRTA.inputs:
            s_dict[key] = [0]
        for tran in discreteRTA.trans:
            if tran.source == s:
                for input in discreteRTA.inputs:
                    if tran.input == input:
                        tempList = s_dict[input]
                        for i in tran.timeList:
                            if i not in tempList:
                                tempList.append(i)
                        s_dict[input] = tempList
        for tran in discreteRTA.trans:
            if tran.source == s:
                timePoints = s_dict[tran.input]
                timePoints.sort()
                guards = []
                evidence = tran.timeList[0]
                for tw in tran.timeList:
                    index = timePoints.index(tw)
                    if index + 1 < len(timePoints):
                        if isInt(tw) and isInt(timePoints[index + 1]):
                            tempGuard = timeInterval_upper.Guard("[" + str(tw) + "," + str(timePoints[index + 1]) + ")")
                        elif isInt(tw) and not isInt(timePoints[index + 1]):
                            tempGuard = timeInterval_upper.Guard("[" + str(tw) + "," + str(math.modf(timePoints[index + 1])[1]) + "]")
                        elif not isInt(tw) and isInt(timePoints[index + 1]):
                            tempGuard = timeInterval_upper.Guard("(" + str(math.modf(tw)[1]) + "," + str(timePoints[index + 1]) + ")")
                        else:
                            tempGuard = timeInterval_upper.Guard("(" + str(math.modf(tw)[1]) + "," + str(math.modf(timePoints[index + 1])[1]) + "]")
                        guards.append(tempGuard)
                    else:
                        if tw == upperGuard:
                            pass
                        else:
                            if isInt(tw):
                                tempGuard = timeInterval_upper.Guard("[" + str(tw) + "," + str(upperGuard) + ")")
                            else:
                                tempGuard = timeInterval_upper.Guard("(" + str(math.modf(tw)[1]) + "," + str(upperGuard) + ")")
                            guards.append(tempGuard)
                guards = simpleGuards(guards)
                temp_tran = RTATran(tran.tranId, tran.source, tran.input, guards, evidence, tran.target)
                trans.append(temp_tran)
    hypothesisRTA = RTA(inputs, states, trans, initState, acceptStates, sinkState)
    return hypothesisRTA


# --------------------------------- 辅助函数 ---------------------------------

# valueList改为str
def makeStr(valueList):
    valueStr = ''
    for v in valueList:
        valueStr = valueStr + str(v)
    return valueStr


# 判断两个tws是否相同
def isTwsEqual(tws1, tws2):
    if len(tws1) != len(tws2):
        return False
    else:
        flag = True
        for i in range(len(tws1)):
            if tws1[i] != tws2[i]:
                flag = False
                break
        if flag:
            return True
        else:
            return False


# 判断是否整数
def isInt(num):
    x, y = math.modf(num)
    if x == 0:
        return True
    else:
        return False


# Guards排序
def sortGuards(guards):
    for i in range(len(guards) - 1):
        for j in range(len(guards) - i - 1):
            if guards[j].max_bn > guards[j + 1].max_bn:
                guards[j], guards[j + 1] = guards[j + 1], guards[j]
    return guards


# Guards合并
def simpleGuards(guards):
    if len(guards) == 1 or len(guards) == 0:
        return guards
    else:
        sortedGuards = sortGuards(guards)
        result = []
        tempGuard = sortedGuards[0]
        for i in range(1, len(sortedGuards)):
            firstRight = tempGuard.max_bn
            secondLeft = sortedGuards[i].min_bn
            if firstRight.value == secondLeft.value:
                if (firstRight.bracket == 1 and secondLeft.bracket == 2) or (firstRight.bracket == 3 and secondLeft.bracket == 4):
                    left = tempGuard.guard.split(',')[0]
                    right = sortedGuards[i].guard.split(',')[1]
                    guard = timeInterval_upper.Guard(left + ',' + right)
                    tempGuard = guard
                elif firstRight.bracket == 1 and secondLeft.bracket == 3:
                    result.append(tempGuard)
                    tempGuard = sortedGuards[i]
            else:
                result.append(tempGuard)
                tempGuard = sortedGuards[i]
        result.append(tempGuard)
        return result
