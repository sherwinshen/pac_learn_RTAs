import json
import time
from Automata.system import buildSystem
from learningRTA_Symbol.learner import learnRTA
from common.makePic import makeRTA, makeLearnedRTA


def main():
    ### 构建目标系统
    filePath = "../Automata/Model/test4"
    targetSys = buildSystem(filePath + "/example.json")
    makeRTA(targetSys, filePath, '/results/目标系统')

    ### 获取前提条件
    with open(filePath + '/precondition.json', 'r') as f:
        # 文件数据获取
        data = json.load(f)
        inputs = data["inputs"]  # input字母表
        upperGuard = data["upperGuard"]  # 时间上界
        stateNum = data["stateNum"]  # 状态数(含sink状态)
        sampleNum = data["sampleNum"]  # 证据采样数
        epsilon = data["epsilon"]  # 准确度
        delta = data["delta"]  # 置信度

    ### 学习RTA
    startLearning = time.time()
    learnedSys, mqNum, eqNum, testNum = learnRTA(targetSys, inputs, upperGuard, stateNum, sampleNum, epsilon, delta)
    endLearning = time.time()

    ### 学习结果
    if learnedSys is None:
        print("Error! Learning Failed.")
    else:
        print("---------------------------------------------------")
        print("Succeed! The learned RTA is as follows.")
        makeLearnedRTA(learnedSys, filePath, '/results/猜想系统')
        print("---------------------------------------------------")
        print("学习总时间: " + str(endLearning - startLearning))
        print("成员查询数量: " + str(mqNum))
        print("等价查询数量: " + str(eqNum))
        print("测试数量: " + str(testNum))
        data = {
            "time": endLearning - startLearning,
            "mqNum": mqNum,
            "eqNum": eqNum,
            "testNum": testNum
        }
        # 结果存入json文件
        json_str = json.dumps(data, indent=4)
        with open(filePath + "/result.json", 'w') as json_file:
            json_file.write(json_str)


if __name__ == '__main__':
    main()
