import json
import common.timeInterval_upper as timeInterval_upper


class System(object):
    def __init__(self, inputs, states, trans, initState, acceptStates):
        self.inputs = inputs
        self.states = states
        self.trans = trans
        self.initState = initState
        self.acceptStates = acceptStates


class SysTran(object):
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
        return False

    def showGuards(self):
        temp = self.guards[0].show()
        for i in range(1, len(self.guards)):
            temp = temp + 'U' + self.guards[i].show()
        return temp


# 构建目标系统
def buildSystem(jsonFile):
    with open(jsonFile, 'r') as f:
        # 文件数据获取
        data = json.load(f)
        inputs = data["inputs"]
        states = data["states"]
        trans = data["trans"]
        initState = data["initState"]
        acceptStates = data["acceptStates"]
    # trans 处理
    transSet = []
    for tran in trans:
        tranId = str(tran)
        source = trans[tran][0]
        target = trans[tran][3]
        input = trans[tran][1]
        # 时间处理 - guard
        intervals = trans[tran][2]
        intervalsList = intervals.split('U')
        guards = []
        for guard in intervalsList:
            newGuard = timeInterval_upper.Guard(guard.strip())
            guards.append(newGuard)
        systemTran = SysTran(tranId, source, input, guards, target)
        transSet += [systemTran]
    transSet.sort(key=lambda x: x.tranId)
    system = System(inputs, states, transSet, initState, acceptStates)
    return system


# 系统交互 - 给定输入观察输出
def systemOutput(tws, targetSys):
    if len(tws) == 0:
        if targetSys.initState in targetSys.acceptStates:
            return 1
        else:
            return 0
    else:
        curStateNow = targetSys.initState
        for tw in tws:
            flag = False
            for tran in targetSys.trans:
                if tran.source == curStateNow and tran.isPass(tw):
                    curStateNow = tran.target
                    flag = True
                    break
            if not flag:
                return -1
        if curStateNow in targetSys.acceptStates:
            return 1
        else:
            return 0
