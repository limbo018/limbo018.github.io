---
title: "MacroRank: Ranking Macro Placement Solutions Leveraging Translation Equivariancy"
collection: softwares
type: "Softwares"
permalink: /softwares/10-MacroRank
date: 2023-04-07
---

We present **[MacroRank](https://github.com/PKU-IDEA/MacroRank)** 
to predict the relative order of the quality of macro placement solutions.

Modern large-scale designs make extensive use of heterogeneous macros, which can significantly affect routability. Predicting the final routing quality in the early macro placement stage can filter out poor solutions and speed up design closure. By observing that routing is correlated with the relative positions between instances, we propose MacroRank, a macro placement ranking framework leveraging translation equivariance and a Learning to Rank technique. The framework is able to learn the relative order of macro placement solutions and rank them based on routing quality metrics like wirelength, number of vias, and number of shorts. 
