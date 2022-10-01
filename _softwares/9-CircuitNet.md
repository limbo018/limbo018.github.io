---
title: "Open-Source Dataset for Machine Learning Applications in Electronic Design Automation (EDA)"
collection: softwares
type: "Softwares"
permalink: /softwares/9-CircuitNet
date: 2022-07-28
---

We present **[CircuitNet](https://github.com/circuitnet/CircuitNet)**, 
an open-source dataset for machine learning applications in electronic design automation.

The dataset consists of over 10K samples and 54 synthesized circuit netlists from six open-source RISC-V designs, provides holistic support for cross-stage prediction tasks, and supports tasks including routing congestion prediction, design rule check (DRC) violation prediction and IR drop prediction. The main characteristics of CircuitNet can be summarized as follows:

- Large scale: The dataset consists of more than 10K samples extracted from versatile runs of commercial EDA tools with commercial PDKs (currently in 28nm technology node, and will support 14nm technology soon).

- Diversity: Different settings in logic synthesis and physical design are introduced to reflect diverse situations in the design flow.

- Multiple tasks: The dataset supports three prediction tasks, i.e., congestion prediction, DRC violation prediction, and IR drop prediction. The dataset includes features widely adopted in the state-of-the-art methods and is validated through experiments.

- Easy-to-use formats: Features are preprocessed and transformed into Numpy arrays with restricted information removed. Users can load the data easily through Python scripts.

To evaluate the effectiveness of CircuitNet, we validate the dataset by experiments on three prediction tasks: congestion, DRC violations, and IR drop. Each experiment takes a method from recent studies and evaluates its result on CircuitNet with the same evaluation metrics as the original studies. Overall, the results are consistent with the original publications, which demonstrates the effectiveness of CircuitNet.
