import json
from time import time
from Automata.system import buildSystem
from learningRTA.learner import learnRTA
from common.makePic import makeRTA, makeLearnedRTA


def main():
    ### 构建目标系统
    targetSys = buildSystem(filePath + "/example.json")
    makeRTA(targetSys, filePath, '/results/目标系统')

    ### 获取前提条件
    with open(filePath + '/precondition.json', 'r') as f:
        # 文件数据获取
        custom = json.load(f)
        inputs = custom["inputs"]  # input字母表
        upperGuard = custom["upperGuard"]  # 时间上界
        stateNum = custom["stateNum"]  # 状态数(含sink状态)
        epsilon = custom["epsilon"]  # 准确度
        delta = custom["delta"]  # 置信度

    ### 学习RTA
    startLearning = time()
    learnedSys, mqNum, eqNum, testNum = learnRTA(targetSys, inputs, upperGuard, stateNum, epsilon, delta)
    endLearning = time()

    ### 学习结果
    if learnedSys is None:
        print("Error! Learning Failed.")
        return {"Data": "Failed"}
    else:
        print("---------------------------------------------------")
        print("Succeed! The learned RTA is as follows.")
        makeLearnedRTA(learnedSys, filePath, '/results/猜想系统')

        print("---------------------------------------------------")
        print("学习总时间: " + str(endLearning - startLearning))
        print("成员查询数量: " + str(mqNum))
        print("等价查询数量: " + str(eqNum))
        print("测试数量: " + str(testNum))

        result = {
            "Data": "Success",
            "time": endLearning - startLearning,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum
        }
        return result


if __name__ == '__main__':
    # 目标模型
    filePath = "../Automata/Model/test3"
    # 实验次数
    testTime = 1
    # 实验结果
    data = {}
    for i in range(testTime):
        temp = main()
        data.update({i: temp})
    json_str = json.dumps(data, indent=4)
    with open(filePath + "/result_1.json", 'w') as json_file:
        json_file.write(json_str)
