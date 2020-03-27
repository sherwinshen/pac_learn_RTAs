from common.timedWord import TimedWord
from learningRTA.teacher import TQs


class ObsTable(object):
    def __init__(self, S, R, E):
        self.S = S
        self.R = R
        self.E = E

    def show(self):
        print("new_E:" + str(len(self.E)))
        for e in self.E:
            print([tw.show() for tw in e])
        print("new_S:" + str(len(self.S)))
        for s in self.S:
            print([tw.show() for tw in s.tws], s.valueList)
        print("new_R:" + str(len(self.R)))
        for r in self.R:
            print([tw.show() for tw in r.tws], r.valueList)


class Element(object):
    def __init__(self, tws, valueList):
        self.tws = tws
        self.valueList = valueList


# 初始化观察表
def initTable(inputs, system, mqNum):
    # 处理E
    E = [[]]
    # 处理S
    S = []
    element, mqNum = fillTableRow([], E, system, mqNum)
    S.append(element)
    # 处理R
    R = []
    newR, mqNum = extendR(system, S[0], inputs, E, mqNum)
    R = R + newR
    return ObsTable(S, R, E), mqNum


# 根据s扩充成一行,返回Element
def fillTableRow(tracesTW, table_E, targetSys, mqNum):
    tempElement = Element(tracesTW, [])
    for e in table_E:
        if not e:
            if not tracesTW:
                tempTWs = []
            else:
                tempTWs = tracesTW
        else:
            if not tracesTW:
                tempTWs = e
            else:
                tempTWs = tracesTW + e
        tempValue = TQs(tempTWs, targetSys)
        mqNum += 1
        tempElement.valueList.append(tempValue)
    return tempElement, mqNum


# S添加s,扩展R区域
def extendR(targetSys, s, inputs, E, mqNum):
    newRList = []
    for i in range(len(inputs)):
        newTrace = s.tws + [TimedWord(inputs[i], 0)]
        element, mqNum = fillTableRow(newTrace, E, targetSys, mqNum)
        newRList.append(element)
    return newRList, mqNum


# 观察表是否满足全部性质
def isPrepared(table):
    flagClosed, closedMove = isClosed(table)
    flagConsistent, consistentAdd = isConsistent(table)
    if flagClosed and flagConsistent:
        return True
    else:
        return False


# 是否closed
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


# 是否consistent
def isConsistent(table):
    flag = True
    consistentAdd = []
    tableElement = [s for s in table.S] + [r for r in table.R]
    for i in range(0, len(tableElement) - 1):
        for j in range(i + 1, len(tableElement)):
            if tableElement[i].valueList == tableElement[j].valueList:
                tempElements1 = []
                tempElements2 = []
                for element in tableElement:
                    if isPrefix(element.tws, tableElement[i].tws):
                        tempElements1.append(element)
                    if isPrefix(element.tws, tableElement[j].tws):
                        tempElements2.append(element)
                for e1 in tempElements1:
                    for e2 in tempElements2:
                        new_tws1 = deletePrefix(e1.tws, tableElement[i].tws)
                        new_tws2 = deletePrefix(e2.tws, tableElement[j].tws)
                        if len(new_tws1) == 1 and len(new_tws2) == 1 and new_tws1 == new_tws2:
                            if e1.valueList == e2.valueList:
                                pass
                            else:
                                flag = False
                                for k in range(0, len(e1.valueList)):
                                    if e1.valueList[k] != e2.valueList[k]:
                                        new_e_index = k
                                        consistentAdd = new_tws1 + table.E[new_e_index]
                                        return flag, consistentAdd
    return flag, consistentAdd


# 调整至closed
def makeClosed(table, inputs, closedMove, targetSys, mqNum):
    # close_move将其从R移至S
    for r in closedMove:
        table.S.append(r)
        table.R.remove(r)
    # 处理R
    tableTrace = [s.tws for s in table.S] + [r.tws for r in table.R]
    for i in closedMove:
        newRList, mqNum = extendR(targetSys, i, inputs, table.E, mqNum)
        for j in newRList:
            if j.tws not in tableTrace:
                table.R.append(j)
    return table, mqNum


# 调整至consistent
def makeConsistent(table, consistentAdd, targetSys, mqNum):
    table.E.append(consistentAdd)
    for i in range(0, len(table.S)):
        twsTemp1 = table.S[i].tws + consistentAdd
        valueTemp1 = TQs(twsTemp1, targetSys)
        table.S[i].valueList.append(valueTemp1)
        mqNum += 1
    for j in range(0, len(table.R)):
        twsTemp2 = table.R[j].tws + consistentAdd
        valueTemp1 = TQs(twsTemp2, targetSys)
        table.R[j].valueList.append(valueTemp1)
        mqNum += 1
    return table, mqNum


# 处理反例1 - 添加反例的所有前缀集 - 缺点：很难找到状态识别集
def dealCtx(table, ctx, hypothesisRTA, targetRTA, mqNum):
    pref = prefixes(ctx.tws)
    S_Rtws = [s.tws for s in table.S] + [r.tws for r in table.R]
    for tws in pref:
        needAdd = True
        for stws in S_Rtws:
            if tws == stws:
                needAdd = False
        if needAdd:
            temp_element, mqNum = fillTableRow(tws, table.E, targetRTA, mqNum)
            table.R.append(temp_element)
    return table, mqNum


# --------------------------------- 辅助函数 ---------------------------------

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


# pre是否是tws的前缀
def isPrefix(tws, pre):
    if len(pre) == 0:
        return True
    else:
        if len(tws) < len(pre):
            return False
        else:
            for i in range(0, len(pre)):
                if tws[i] == pre[i]:
                    pass
                else:
                    return False
            return True


# tws删除前缀pre
def deletePrefix(tws, pre):
    if len(pre) == 0:
        return tws
    else:
        new_tws = tws[len(pre):]
        return new_tws


# valueList改为str
def makeStr(valueList):
    valueStr = ''
    for v in valueList:
        valueStr = valueStr + str(v)
    return valueStr


# tws的前缀集
def prefixes(tws):
    newPrefixes = []
    for i in range(1, len(tws) + 1):
        temp_tws = tws[:i]
        newPrefixes.append(temp_tws)
    return newPrefixes


# 给定source和target获得目标迁移TW
def getTwsConnection(source, target, a, hypothesisRTA):
    tw = None
    for tran in hypothesisRTA.trans:
        if tran.source == source and tran.target == target and tran.isPass(a):
            tw = TimedWord(tran.input, tran.evidence)
            break
    return tw
