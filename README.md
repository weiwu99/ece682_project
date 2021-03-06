# ECE 682 Project: Nonparametric Clustering Scheme - Dirichlet Process Mixture Model
This is the repository for ECE682 project: Nonparametric Clustering Scheme - Dirichlet Process Mixture Model

## Authors
Boxuan Li, Danny Luo, Jingyu Peng, Nianli Peng, Wei Wu

## Contents

- [ECE 682 Project: Nonparametric Clustering Scheme - Dirichlet Process Mixture Model](#ece682-project)
  - [Authors](#authors)
  - [Contents](#contents)
  - [Introduction](#intro)
  - [Note](#note)

## Introduction

Clustering is a common problem encountered in data analysis, and it gets especially challenging for high dimensional data. 
Moreover, it is difficult to identify the optimal cluster size in parametric models such as the k-means algorithm in these problems.

Therefore, we are proposing Dirichlet Process Mixture Model, a Bayesian nonparametric
approach that not only assumes no fixed cluster size and has unbounded complexity but also provides
interpretability to the clustering model as it estimates the underlying distribution of the data. 
Our approach can provide an effecitve alternative approach for real-life machine learning applications with high-dimensional data, 
ranging from profiling grouping to social media analysis. 

## Note

`experiment.ipynb` is the main graph generating script. `DataGenerator.py` is the data generator used in this project, and the undercomplete autoencoder is in `models/AutoEncoders.py`. `utils.py` contains relevant helper methods used in the experiments. 