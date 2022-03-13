# PAC Learning of RTAs

> See [PAC Learning of DOTAs](https://github.com/sherwinshen/pac_learn_DOTAs) for a more general and powerful learning tool.

## Overview

This tool is dedicated to learning real-time automata (RTAs), which is a variant of [Lesliea - RTALearning](https://github.com/Leslieaj/RTALearning) based on L* algorithm. This tool for learning RTAs under more realistic assumptions within the framework of PAC learning. Membership queries and equivalence queries are realized via testing. 

## Installation

The project was developed using Python3, and you only need to download the project, but there are a few prerequisites before running：

- Python3.7.* (or high)
- graphviz (used for drawing)

## Usage

Before executing the program, we need to prepare two files, **model.json** (including model structure) and **precondition.json** (including model information known to learners).

- model.json

```json
{
	"inputs": ["a", "b"],  // input actions
	"states": ["0", "1"],  // state
	"trans": {  // transition set（source state, input, timeGuards, target state）
		"0": ["0", "b", "[0,2)U[3,6)", "0"],
		"1": ["0", "a", "[5,7)", "1"],
		"2": ["1", "b", "[0,7)", "1"]
	},
	"initState": "0",  // initial target
	"acceptStates": ["1"]  // accept state
}
```

- precondition.json

```json
{
  "inputs": ["a", "b"], // 输入actions
  "upperGuard": 7,  // 时间上界
  "sampleNum": 6, // 采样数（符号化学习使用）
  "epsilon": 0.01, // 精确度
  "delta": 0.01 // 置信度
}
```

We provide model examples in `Automata/Model`, and users can also customize the model structure according to file `model.json`. In ` learningrta/main.py ` or ` learningrta_ symbol/main.py `, users can set the target model file path, and run it directly.

- `learningrta/main.py`: a common method of learning RTAs combined with PAC.
- `learningrta_ symbol/main.py`: an advanced method of learning RTAs combined with symbolization method and PAC.

## Reference

1. Maler O , Mens I E . A Generic Algorithm for Learning Symbolic Automata from Membership Queries[M]// Models, Algorithms, Logics and Tools. 2017.
2. Dima C. Real-time automata.[J]. Journal of Automata Languages & Combinatorics, 2001, 6(6):3-24.
3. Dana, Angluin. Learning regular sets from queries and counterexamples[J]. Information & Computation, 1987.

## License

See [MIT LICENSE](./LICENSE) file.

## Contact

Please let me know if you have any questions 👉 [EnvisionShen@gmail.com](mailto:EnvisionShen@gmail.com)
