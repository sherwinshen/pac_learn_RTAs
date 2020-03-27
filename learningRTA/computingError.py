import copy
import random
import math
import common.timeInterval_upper as timeInterval_upper
from common.timedWord import TimedWord
from learningRTA.hypothesis import RTA, RTATran


class ConnectRTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState


class ComplementRTA(object):
    def __init__(self, inputs, states, trans, initState, acceptStates, sinkState, errorState):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates
        self.sinkState = sinkState
        self.errorState = errorState


class State(object):
    def __init__(self, stateName, firstId, secondId):
        self.stateName = stateName
        self.firstId = firstId
        self.secondId = secondId


# Step1 补全targetSys
def buildCanonicalRTA(targetSys, upperGuard):
    inputs = targetSys.inputs
    states = targetSys.states
    trans = targetSys.trans
    initState = targetSys.initState
    acceptStates = targetSys.acceptStates

    sinkFlag = False
    newTrans = []
    sinkState = None
    tranNumber = len(targetSys.trans)

    for state in targetSys.states:
        guardDict = {}
        for input in inputs:
            guardDict[input] = []
        for tran in trans:
            if tran.source == state:
                for input in inputs:
                    if tran.input == input:
                        for guard in tran.guards:
                            guardDict[input].append(guard)
        for key, value in guardDict.items():
            if len(value) > 0:
                addGuards = complementIntervals(value, upperGuard)
            else:
                addGuards = [timeInterval_upper.Guard('[0,' + str(upperGuard) + ')')]
            if len(addGuards) > 0:
                sinkState = str(len(targetSys.states))
                sinkFlag = True
                tempTran = RTATran(tranNumber, state, key, addGuards, 0, sinkState)
                tranNumber = tranNumber + 1
                newTrans.append(tempTran)
    if sinkFlag:
        states.append(sinkState)
        for tran in newTrans:
            trans.append(tran)
        for input in inputs:
            guards = [timeInterval_upper.Guard('[0,' + str(upperGuard) + ')')]
            tempTran = RTATran(tranNumber, sinkState, input, guards, 0, sinkState)
            tranNumber = tranNumber + 1
            trans.append(tempTran)
    newRTA = RTA(inputs, states, trans, initState, acceptStates, sinkState)
    return newRTA


# Step2 计算合并自动机
def buildMergeRTA(hypRTA, targetRTA):
    inputs = hypRTA.inputs
    states = []
    trans = []
    initStateName = str(hypRTA.initState) + '_' + str(targetRTA.initState)
    acceptStates = []
    transNum = 0
    sinkState = None
    tempStates = []
    finalStates = []
    initState = State(initStateName, hypRTA.initState, targetRTA.initState)
    if hypRTA.initState in hypRTA.acceptStates and targetRTA.initState in targetRTA.acceptStates:
        acceptStates.append(initStateName)
    states.append(initState)
    tempStates.append(initState)
    while len(tempStates) != 0:
        state1 = tempStates[0].firstId
        state2 = tempStates[0].secondId
        temp1 = []  # [input,guard,target,output]
        temp2 = []
        for tran in hypRTA.trans:
            if tran.source == state1:
                if tran.target == hypRTA.sinkState:
                    output = -1
                elif tran.target in hypRTA.acceptStates:
                    output = 1
                else:
                    output = 0
                temp1.append([tran.input, tran.guards, tran.target, output])
        for tran in targetRTA.trans:
            if tran.source == state2:
                if tran.target == targetRTA.sinkState:
                    output = -1
                elif tran.target in targetRTA.acceptStates:
                    output = 1
                else:
                    output = 0
                temp2.append([tran.input, tran.guards, tran.target, output])
        for i in range(len(temp1)):
            for j in range(len(temp2)):
                if temp1[i][0] == temp2[j][0] and temp1[i][3] == temp2[j][3]:
                    guards1 = temp1[i][1]
                    guards2 = temp2[j][1]
                    guards, flag = intersectionGuard(guards1, guards2)
                    if flag:
                        source = tempStates[0].stateName
                        target = str(temp1[i][2]) + '_' + str(temp2[j][2])
                        tempTran = RTATran(transNum, source, temp1[i][0], guards, 0, target)
                        trans.append(tempTran)
                        transNum += 1
                        if not alreadyHas(target, tempStates, finalStates):
                            newState = State(target, temp1[i][2], temp2[j][2])
                            if temp1[i][3] == 1:
                                acceptStates.append(newState.stateName)
                            elif temp1[i][3] == -1:
                                sinkState = newState.stateName
                            states.append(newState)
                            tempStates.append(newState)
        finalStates.append(tempStates[0])
        tempStates.remove(tempStates[0])

    mergeRTA = ConnectRTA(inputs, states, trans, initStateName, acceptStates, sinkState)
    return mergeRTA


# Step3 计算RTA的补
def buildComplementRTA(mergeRTA, upperGuard):
    tempRTA = copy.deepcopy(mergeRTA)
    inputs = tempRTA.inputs
    states = tempRTA.states
    trans = tempRTA.trans
    initState = tempRTA.initState
    acceptStates = tempRTA.acceptStates
    sinkState = tempRTA.sinkState
    tranId = len(trans)
    stateId = len(states)
    flag = False
    errorState = State(stateId, 'Null', "Null")
    for state in states:
        need = {}
        exist = {}
        for input in inputs:
            need[input] = []
            exist[input] = []
        for tran in trans:
            if tran.source == state.stateName:
                exist[tran.input] += tran.guards
        for key, i in exist.items():
            guards = complementIntervals(i, upperGuard)
            if len(guards) > 0:
                flag = True
                for j in range(len(guards)):
                    if guards[j] not in i:
                        need[key].append(guards[j])
        for key, value in need.items():
            if len(value) > 0:
                newTran = RTATran(tranId, state.stateName, key, value, 0, errorState.stateName)
                trans.append(newTran)
    if flag:
        states.append(errorState)
    else:
        errorState = State('Null', 'Null', 'Null')
    complementRTA = ComplementRTA(inputs, states, trans, initState, acceptStates, sinkState, errorState.stateName)
    return complementRTA


# Step4 计算最短反例
def getMinCtxList(complementRTA, upperGuard):
    # 获得每个状态对应的连接状态 {"0":["0","1","2"]}
    stateDict = {}
    for s in complementRTA.states:
        stateDict[s.stateName] = []
        for t in complementRTA.trans:
            if t.source == s.stateName:
                if t.target not in stateDict[s.stateName]:
                    stateDict[s.stateName].append(t.target)
    # 获得最短反例路径
    ctxList = []
    shortestPath = findShortestPath(stateDict, complementRTA.initState, complementRTA.errorState)
    if len(shortestPath) == 0:
        pass
    else:
        # 计算最短反例
        compareTrace = []
        compareTrace += getStateTrace(complementRTA, shortestPath)
        firstState = shortestPath[-1]
        secondState = shortestPath[-2]
        for tran in complementRTA.trans:
            if tran.source == secondState and tran.target == firstState:
                timeList = getTimeList(tran.guards, upperGuard)
                # timeList = [getRandomTime(tran.guards, upperGuard, precision)]
                for time in timeList:
                    tiw = TimedWord(tran.input, time)
                    tempTrace = compareTrace + [tiw]
                    ctxList.append(tempTrace)
                break
    return ctxList


# Step5 计算距离度量
def distanceMetric(complementRTA):
    # 获得每个状态对应的连接状态 {"0":["0","1","2"]}
    stateDict = {}
    for s in complementRTA.states:
        stateDict[s.stateName] = []
        for t in complementRTA.trans:
            if t.source == s.stateName:
                if t.target not in stateDict[s.stateName]:
                    stateDict[s.stateName].append(t.target)
    # 获得最短反例路径
    shortestPath = findShortestPath(stateDict, complementRTA.initState, complementRTA.errorState)
    # 计算距离度量
    if len(shortestPath) == 0:
        return 0
    else:
        ctxLength = len(shortestPath) - 1
        metric = math.pow(2, -ctxLength)
        return metric


# --------------------------------- 辅助函数 ---------------------------------

# 补全区间
def complementIntervals(guards, upperGuard):
    partitions = []
    key = []
    floor_bn = timeInterval_upper.BracketNum('0', timeInterval_upper.Bracket.LC)
    ceil_bn = timeInterval_upper.BracketNum(str(upperGuard), timeInterval_upper.Bracket.RO)
    for guard in guards:
        min_bn = guard.min_bn
        max_bn = guard.max_bn
        if min_bn not in key:
            key.append(min_bn)
        if max_bn not in key:
            key.append(max_bn)
    copyKey = copy.deepcopy(key)
    for bn in copyKey:
        complement = bn.complement(upperGuard)
        if complement not in copyKey:
            copyKey.append(complement)
    if floor_bn not in copyKey:
        copyKey.insert(0, floor_bn)
    if ceil_bn not in copyKey:
        copyKey.append(ceil_bn)
    copyKey.sort()
    for index in range(len(copyKey)):
        if index % 2 == 0:
            tempGuard = timeInterval_upper.Guard(copyKey[index].getBN() + ',' + copyKey[index + 1].getBN())
            partitions.append(tempGuard)
    for g in guards:
        if g in partitions:
            partitions.remove(g)
    return partitions


# target是否在tempStates, finalStates中存在
def alreadyHas(target, tempStates, finalStates):
    for i in tempStates:
        if i.stateName == target:
            return True
    for j in finalStates:
        if j.stateName == target:
            return True
    return False


# 区间求交集
def intersectionGuard(guards1, guards2):
    guards = []
    flag = False
    for i in range(len(guards1)):
        for j in range(len(guards2)):
            minType1, maxType1 = guards1[i].guard.split(',')
            minType2, maxType2 = guards2[j].guard.split(',')
            minNum1 = float(minType1[1:])
            minNum2 = float(minType2[1:])
            maxNum1 = float(maxType1[:-1])
            maxNum2 = float(maxType2[:-1])
            if maxNum2 < minNum1:
                pass
            elif minNum2 > maxNum1:
                pass
            elif minNum1 > minNum2 and maxNum1 < maxNum2:
                flag = True
                guards.append(guards1[i])
            elif minNum1 < minNum2 and maxNum1 > maxNum2:
                flag = True
                guards.append(guards2[j])
            elif minNum1 < minNum2 < maxNum1 < maxNum2:
                flag = True
                guards.append(timeInterval_upper.Guard(minType2 + ',' + maxType1))
            elif minNum2 < minNum1 < maxNum2 < maxNum1:
                flag = True
                guards.append(timeInterval_upper.Guard(minType1 + ',' + maxType2))
            elif minNum1 == minNum2 and maxNum1 != maxNum2:
                flag = True
                if minType1[0] == '(' or minType2[0] == '(':
                    leftType = '('
                else:
                    leftType = '['
                if maxNum1 >= maxNum2:
                    guards.append(timeInterval_upper.Guard(leftType + str(minNum1) + ',' + maxType2))
                else:
                    guards.append(timeInterval_upper.Guard(leftType + str(minNum1) + ',' + maxType1))
            elif minNum1 == maxNum2:
                if minType1[0] == '[' and maxType2[-1] == ']':
                    flag = True
                    guards.append(timeInterval_upper.Guard('[' + str(minNum1) + ',' + str(minNum1) + ']'))
            elif minNum2 == maxNum1:
                if minType2[0] == '[' and maxType1[-1] == ']':
                    flag = True
                    guards.append(timeInterval_upper.Guard('[' + str(minNum2) + ',' + str(minNum2) + ']'))
            elif maxNum1 == maxNum2 and minNum1 != minNum2:
                flag = True
                if maxType1[-1] == ')' or maxType2[-1] == ')':
                    rightType = ')'
                else:
                    rightType = ']'
                if minNum1 >= minNum2:
                    guards.append(timeInterval_upper.Guard(minType1 + ',' + str(maxNum1) + rightType))
                else:
                    guards.append(timeInterval_upper.Guard(minType2 + ',' + str(maxNum1) + rightType))
            elif minNum1 == minNum2 and maxNum1 == maxNum2:
                if maxType1[-1] == ')' or maxType2[-1] == ')':
                    rightType = ')'
                else:
                    rightType = ']'
                if minType1[0] == '(' or minType2[0] == '(':
                    leftType = '('
                else:
                    leftType = '['
                if leftType == '(' and rightType == ')':
                    pass
                else:
                    flag = True
                    guards.append(timeInterval_upper.Guard(leftType + str(minNum1) + ',' + str(maxNum1) + rightType))
    return guards, flag


# 找到一条从start到end的最短路径
def findShortestPath(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return path
    shortestPath = []
    for node in graph[start]:
        if node not in path:
            newPath = findShortestPath(graph, node, end, path)
            if newPath:
                if not shortestPath or len(newPath) < len(shortestPath):
                    shortestPath = newPath
    return shortestPath


# 获得状态到达集
def getStateTrace(complementRTA, shortestPath):
    trace = []
    tempPath = shortestPath[:-1]
    if len(tempPath) == 1:
        return trace
    else:
        i = 0
        while i < len(tempPath) - 1:
            for tran in complementRTA.trans:
                if tran.source == tempPath[i] and tran.target == tempPath[i + 1]:
                    time = getRandomTime(tran.guards)
                    tiw = TimedWord(tran.input, time)
                    trace.append(tiw)
                    break
            i += 1
        return trace


# 获得随机时间
def getRandomTime(guards):
    length = len(guards)
    index = random.randint(0, length - 1)
    guard = guards[index]
    minNum = guard.get_min()
    maxNum = guard.get_max()
    time = random.randint(minNum, maxNum * 2 - 1) / 2
    return time


# 获得区间三个时间点，头、尾、中间
def getTimeList(guards, upperGuard):
    time = []
    for guard in guards:
        minNum = guard.get_min()
        maxNum = guard.get_max()
        # closed_min = guard.get_closed_min()
        # closed_max = guard.get_closed_max()
        # if closed_min:
        #     time.append(minNum)
        # else:
        #     time.append(minNum + math.pow(10, -precision))
        # if closed_max:
        #     time.append(maxNum)
        # else:
        #     time.append(maxNum - math.pow(10, -precision))
        time.append((minNum + maxNum) / 2)
    return time
