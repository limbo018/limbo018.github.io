---
title: "Timing Engine Inspired Pre-routing Timing Prediction"
collection: softwares
type: "Softwares"
permalink: /softwares/8-TimingPredict
date: 2022-07-14
---

We present **[TimingPredict](https://github.com/PKU-IDEA/TimingPredict)**, 
a timing engine inspired graph neural network model for pre-routing slack prediction.

Fast and accurate pre-routing timing prediction is essential for timingdriven placement since repetitive routing and static timing analysis (STA) iterations are expensive and unacceptable. Prior work on timing prediction aims at estimating net delay and slew, lacking the ability to model global timing metrics. In this work, we present a timing engine
inspired graph neural network (GNN) to predict arrival time and slack at timing endpoints. We further leverage edge delays as local auxiliary tasks to facilitate model training with increased model performance. Experimental results on real-world open-source designs demonstrate improved model accuracy and explainability when compared with vanilla deep GNN models.
