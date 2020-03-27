import numpy as np
import common.timeInterval_upper as timeInterval_upper
from common.timedWord import TimedWord, SymbolTimedWord
from learningRTA_Symbol.teacher import TQs


class ObsTable(object):
    def __init__(self, S, R, E, symbolList):
        self.S = S
        self.R = R
        self.E = E
        self.symbolList = symbolList  # {symbolId:Symbol}

    def show(self):
        print("new_E:" + str(len(self.E)))
        temp = ""
        for e in self.E:
            temp = temp + str([tw.show() for tw in e]) + " "
        print(temp)

        print("new_S:" + str(len(self.S)))
        for s in self.S:
            traceStr = []
            outputStr = []
            for i in s.stws:
                traceStr.append(self.symbolList[i].show())
            for j in s.valueList:
                outputStr.append(j)
            print(traceStr, outputStr, s.symbols)

        print("new_R:" + str(len(self.R)))
        for r in self.R:
            traceStr = []
            outputStr = []
            for i in r.stws:
                traceStr.append(self.symbolList[i].show())
            for j in r.valueList:
                outputStr.append(j)
            print(traceStr, outputStr)


class Element(object):
    elementId = 0

    def __init__(self, stws, valueList, symbols):
        self.elementId = Element.elementId  # 1
        self.stws = stws  # [SymbolId]
        self.valueList = valueList  # [0,1,-1] 0不接收，1接收，-1错误
        self.symbols = symbols  # [SymbolId]
        Element.elementId += 1


# 初始化观察表
def initTable(inputs, upperGuard, sampleNum, targetSys, mqNum):
    table = ObsTable([], [], [], {})
    ### 处理E
    table.E.append([])
    ### 处理S
    stws = []
    tempValue = TQs([], targetSys)
    mqNum += 1
    valueList = [tempValue]
    symbols = []
    newElement = Element(stws, valueList, symbols)
    elementId = newElement.elementId
    table.S.append(newElement)
    # 初始化符号-包含兼容性处理
    table, mqNum = initSymbolList(elementId, table, inputs, upperGuard, sampleNum, targetSys, mqNum)
    ### 处理R
    table, mqNum = extendR(elementId, table, targetSys, mqNum)
    return table, mqNum


# 由S扩展R区域
def extendR(elementId, table, targetSys, mqNum):
    # 获得对应要处理的element
    element = None
    for s in table.S:
        if s.elementId == elementId:
            element = s
            break
    for i in element.symbols:
        newTrace = element.stws + [i]
        valueList = []
        for e in table.E:
            tempTrace = stwsTOtws(newTrace, table.symbolList) + e
            tempValue = TQs(tempTrace, targetSys)
            mqNum += 1
            valueList.append(tempValue)
        symbols = []
        newElement = Element(newTrace, valueList, symbols)
        table.R.append(newElement)
    return table, mqNum


# S区域添加element时，初始化符号List
def initSymbolList(elementId, table, inputs, upperGuard, sampleNum, targetSys, mqNum):
    # 获得对应要处理的element
    element = None
    for s in table.S:
        if s.elementId == elementId:
            element = s
            break
    # 生成符号
    tws = stwsTOtws(element.stws, table.symbolList)
    for input in inputs:
        newSymbol, mqNum = initSymbol(tws, input, upperGuard, sampleNum, targetSys, mqNum)
        table.symbolList[newSymbol.symbolId] = newSymbol
        element.symbols.append(newSymbol.symbolId)
    # 兼容性处理
    while not isEvComp(elementId, table):
        table = makeEvComp(elementId, table, inputs)
    return table, mqNum


# 初始化符号
def initSymbol(tws, input, upperGuard, sampleNum, targetSys, mqNum):
    guard = timeInterval_upper.Guard("[0," + str(upperGuard) + ")")
    evidences = {}
    evidencesNum = list(set(np.random.uniform(0, upperGuard, sampleNum)))
    for i in range(len(evidencesNum)):
        evidencesNum[i] = evidencesNum[i]
    evidencesNum.sort()
    for i in evidencesNum:
        trace = tws + [TimedWord(input, i)]
        tempValue = TQs(trace, targetSys)
        mqNum += 1
        evidences[i] = tempValue
    representation = np.random.choice(evidencesNum)
    return SymbolTimedWord(input, guard, evidences, representation), mqNum


# closed判断
def isClosed(table):
    closedMove = []
    for r in table.R:
        flag = False
        for s in table.S:
            if r.valueList == s.valueList:
                flag = True
                break
        if not flag:
            if elementNotInList(r.valueList, closedMove):
                closedMove.append(r)
    if len(closedMove) > 0:
        return False, closedMove
    else:
        return True, closedMove


# closed处理
def makeClosed(table, closedMove, inputs, upperGuard, sampleNum, targetSys, mqNum):
    # close_move将其从R移至S
    for r in closedMove:
        elementId = r.elementId
        table.S.append(r)
        table.R.remove(r)
        # 处理symbols
        table, mqNum = initSymbolList(elementId, table, inputs, upperGuard, sampleNum, targetSys, mqNum)
        ### 处理R
        table, mqNum = extendR(elementId, table, targetSys, mqNum)
    return table, mqNum


# 判断是否兼容
def isEvComp(elementId, table):
    # 获得对应要处理的element
    element = None
    for s in table.S:
        if s.elementId == elementId:
            element = s
            break
    # 判断是否evidence对应的值存在不一致
    symbols = element.symbols
    for symbolId in symbols:
        evidences = table.symbolList[symbolId].evidences
        value = evidences[table.symbolList[symbolId].representation]
        for tempValue in evidences.values():
            if tempValue != value:
                return False
    return True


# 处理兼容
def makeEvComp(elementId, table, inputs):
    # 获得对应要处理的element
    element = None
    for s in table.S:
        if s.elementId == elementId:
            element = s
            break
    # 获得每个input对应的symbol {input:[realSymbol]}
    tempSymbolList = {}
    for i in inputs:
        tempSymbolList[i] = []
    for symbol in element.symbols:
        tempSymbolList[table.symbolList[symbol].input].append(table.symbolList[symbol])
    # 寻找错误之处
    index = None
    errorSymbolId = None
    p = None
    errorInput = None
    evList = []
    for key, symList in tempSymbolList.items():
        evList = []  # [(time,symbolId,value)]
        for sym in symList:
            for time, value in sym.evidences.items():
                evList.append((time, sym.symbolId, value))
        evList.sort(key=takeFirst)  # 指定第一个元素排序
        hasError = False
        # 判断该符号是否有错误
        for i in range(0, len(evList) - 1):
            if evList[i][1] == evList[i + 1][1] and evList[i][2] != evList[i + 1][2]:
                hasError = True
                index = i
                errorInput = key
                errorSymbolId = evList[i][1]
                p = round(((evList[i][0] + evList[i + 1][0]) / 2), 1)
                break
        if hasError:
            break
    # 处理错误
    if len(tempSymbolList[errorInput]) == 1:
        table = evCompAddSymbol(errorSymbolId, p, elementId, table)
    else:
        flagRight = False
        rightSymbolId = None
        flagLeft = False
        leftSymbolId = None
        realRightValue = evList[index + 1][2]
        realLeftValue = evList[index][2]
        tempSymbolId = evList[index + 1][1]
        # 判断右边相同
        for i in range(index + 2, len(evList)):
            if evList[i][1] == tempSymbolId and evList[i][2] == realRightValue:
                continue
            if evList[i][1] == tempSymbolId and evList[i][2] != realRightValue:
                break
            if evList[i][1] != tempSymbolId and evList[i][2] == realRightValue:
                flagRight = True
                rightSymbolId = evList[i][1]
                break
            else:
                break
        # 判断左边相同
        if not flagRight:
            for i in range(index - 1, -1, -1):
                if evList[i][1] == tempSymbolId and evList[i][2] == realLeftValue:
                    continue
                if evList[i][1] == tempSymbolId and evList[i][2] != realLeftValue:
                    break
                if evList[i][1] != tempSymbolId and evList[i][2] == realLeftValue:
                    flagLeft = True
                    leftSymbolId = evList[i][1]
                    break
                else:
                    break
        # 处理区间
        if flagRight:
            # 处理guard
            minNum1, maxNum1 = table.symbolList[rightSymbolId].guard.guard[1:-1].split(',')
            minNum2, maxNum2 = table.symbolList[errorSymbolId].guard.guard[1:-1].split(',')
            table.symbolList[rightSymbolId].guard = timeInterval_upper.Guard('[' + str(p) + ',' + str(maxNum1) + ')')
            table.symbolList[errorSymbolId].guard = timeInterval_upper.Guard('[' + str(minNum2) + ',' + str(p) + ')')
            # 处理evidences
            for key, value in list(table.symbolList[errorSymbolId].evidences.items()):
                if key >= p:
                    table.symbolList[errorSymbolId].evidences.pop(key)
                    table.symbolList[rightSymbolId].evidences[key] = value
        elif flagLeft:
            # 处理guard
            minNum1, maxNum1 = table.symbolList[leftSymbolId].guard.guard[1:-1].split(',')
            minNum2, maxNum2 = table.symbolList[errorSymbolId].guard.guard[1:-1].split(',')
            table.symbolList[leftSymbolId].guard = timeInterval_upper.Guard('[' + str(minNum1) + ',' + str(p) + ')')
            table.symbolList[errorSymbolId].guard = timeInterval_upper.Guard('[' + str(p) + ',' + str(maxNum2) + ')')
            # 处理evidences
            for key, value in list(table.symbolList[errorSymbolId].evidences.items()):
                if key < p:
                    table.symbolList[errorSymbolId].evidences.pop(key)
                    table.symbolList[leftSymbolId].evidences[key] = value
        else:
            table = evCompAddSymbol(errorSymbolId, p, elementId, table)
    return table


# 兼容性处理时添加符号
def evCompAddSymbol(errorSymbolId, p, elementId, table):
    repre = table.symbolList[errorSymbolId].representation
    if repre <= p:
        # 处理guard
        minNum, maxNum = table.symbolList[errorSymbolId].guard.guard[1:-1].split(',')
        table.symbolList[errorSymbolId].guard = timeInterval_upper.Guard('[' + str(minNum) + ',' + str(p) + ')')
        guard = timeInterval_upper.Guard('[' + str(p) + ',' + str(maxNum) + ')')
        # 处理evidences
        evidences = {}
        for key, value in list(table.symbolList[errorSymbolId].evidences.items()):
            if key >= p:
                table.symbolList[errorSymbolId].evidences.pop(key)
                evidences[key] = value
    else:
        # 处理guard
        minNum, maxNum = table.symbolList[errorSymbolId].guard.guard[1:-1].split(',')
        table.symbolList[errorSymbolId].guard = timeInterval_upper.Guard('[' + str(p) + ',' + str(maxNum) + ')')
        guard = timeInterval_upper.Guard('[' + str(minNum) + ',' + str(p) + ')')
        # 处理evidences
        evidences = {}
        for key, value in list(table.symbolList[errorSymbolId].evidences.items()):
            if key < p:
                table.symbolList[errorSymbolId].evidences.pop(key)
                evidences[key] = value
    # 处理representation
    evidencesNum = []
    for time in evidences.keys():
        evidencesNum.append(time)
    representation = np.random.choice(evidencesNum)
    newSymbol = SymbolTimedWord(table.symbolList[errorSymbolId].input, guard, evidences, representation)
    table.symbolList[newSymbol.symbolId] = newSymbol
    # 获得对应要处理的element
    element = None
    for s in table.S:
        if s.elementId == elementId:
            element = s
            break
    element.symbols.append(newSymbol.symbolId)
    return table


# 处理反例
def dealCtx(table, ctx, inputs, targetSys, mqNum):
    tws = ctx.tws
    # 处理每个状态对应的最小tw序列
    stateDict = {}  # {elementId:repreList}
    for s in table.S:
        stateDict[s.elementId] = stwsTOtws(s.stws, table.symbolList)
    # 处理table的所有element {elementId: realElement}
    tableElement = {}
    for s in table.S:
        tableElement[s.elementId] = s
    for r in table.R:
        tableElement[r.elementId] = r
    # 处理valueList对应的状态名ElementId
    valueList_name_dict = {}
    for s in table.S:
        stateName = s.elementId
        valueList_name_dict[makeStr(s.valueList)] = stateName
    # 处理反例tw对应的符号和状态
    symbolTups = []  # [(symbolId, elementId)]
    elementId = 0
    for i in tws:
        symbols = tableElement[elementId].symbols
        for symbol in symbols:
            realSymbol = table.symbolList[symbol]
            if realSymbol.input == i.input and realSymbol.guard.isInInterval(i.time):
                symbolId = symbol
                # 找到elementId
                stws = tableElement[elementId].stws + [symbolId]
                for key, value in tableElement.items():
                    if value.stws == stws:
                        elementId = key
                        break
                elementId = valueList_name_dict[makeStr(tableElement[elementId].valueList)]
                symbolTups.append((symbolId, elementId))
                break
    # 获得flag
    state = symbolTups[-1][1]
    tempTws = stateDict[state]
    flag = TQs(tempTws, targetSys)
    mqNum += 1
    # breakPoint处理，即找到出错处
    for i in range(len(tws) - 1, -1, -1):
        # u = tws[:i]
        a = tws[i]
        v = tws[i + 1:]
        repA = table.symbolList[symbolTups[i][0]]
        twA = TimedWord(repA.input, repA.representation)
        if i == 0:
            tws1 = [] + [twA] + v
            tws2 = [] + [a] + v
        else:
            tws1 = stateDict[symbolTups[i - 1][1]] + [twA] + v
            tws2 = stateDict[symbolTups[i - 1][1]] + [a] + v
        if TQs(tws1, targetSys) != flag:
            mqNum += 1
            table, mqNum = addE(v, table, targetSys, mqNum)
            break
        elif TQs(tws2, targetSys) != flag:
            mqNum += 2
            aSymbolId = symbolTups[i][0]
            if i == 0:
                trace = [] + [a] + v
            else:
                trace = stateDict[symbolTups[i - 1][1]] + [a] + v
            value = TQs(trace, targetSys)
            table.symbolList[aSymbolId].evidences[a.time] = value
            ### 处理兼容
            # 获得对应要处理的elementId
            if i == 0:
                targetId = 0
            else:
                targetId = symbolTups[i - 1][1]
            # 开始处理兼容性
            if isEvComp(targetId, table):
                table, mqNum = addE(v, table, targetSys, mqNum)
            else:
                while not isEvComp(targetId, table):
                    table = makeEvComp(targetId, table, inputs)
                table, mqNum = addR(targetId, table, targetSys, mqNum)
            break
    return table, mqNum


# E区域添加v
def addE(v, table, targetSys, mqNum):
    table.E.append(v)
    for i in range(0, len(table.S)):
        tws = stwsTOtws(table.S[i].stws, table.symbolList) + v
        tempValue = TQs(tws, targetSys)
        table.S[i].valueList.append(tempValue)
        mqNum += 1
    for j in range(0, len(table.R)):
        tws = stwsTOtws(table.R[j].stws, table.symbolList) + v
        tempValue = TQs(tws, targetSys)
        table.R[j].valueList.append(tempValue)
        mqNum += 1
    return table, mqNum


# 兼容性处理后添加R
def addR(targetId, table, targetSys, mqNum):
    # 获得element字典 - {elementId:realElement}
    tableElement = {}
    for s in table.S:
        tableElement[s.elementId] = s
    for r in table.R:
        tableElement[r.elementId] = r
    # 获得对应element
    element = tableElement[targetId]
    # 开始处理
    for i in element.symbols:
        newTrace = element.stws + [i]
        hasInR = False
        for key, value in tableElement.items():
            if value.stws == newTrace:
                hasInR = True
                break
        if hasInR:
            continue
        else:
            valueList = []
            for e in table.E:
                tempTrace = stwsTOtws(newTrace, table.symbolList) + e
                tempValue = TQs(tempTrace, targetSys)
                mqNum += 1
                valueList.append(tempValue)
            symbols = []
            newElement = Element(newTrace, valueList, symbols)
            table.R.append(newElement)
    return table, mqNum


# --------------------------------- 辅助函数 ---------------------------------

# stws转变为代表的tws
def stwsTOtws(stws, symbolList):
    tws = []
    if not stws:
        return []
    else:
        for stw in stws:
            tw = TimedWord(symbolList[stw].input, symbolList[stw].representation)
            tws.append(tw)
        return tws


# 判断Element的List中是否已有相同valueList的元素，若存在返回False，不存在则返回True
def elementNotInList(valueList, elementList):
    if len(elementList) == 0:
        return True
    else:
        flag = True
        for i in range(len(elementList)):
            if valueList == elementList[i].valueList:
                flag = False
                break
        if flag:
            return True
        else:
            return False


# 用于sort函数，返回第一个元素
def takeFirst(elem):
    return elem[0]


# valueList改为str
def makeStr(valueList):
    valueStr = ''
    for v in valueList:
        valueStr = valueStr + str(v)
    return valueStr
