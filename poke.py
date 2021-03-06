import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split

from sklearn.mixture import BayesianGaussianMixture as BGM
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, rand_score, adjusted_rand_score

from DataGenerator import DataGenerator
from models.AutoEncoders import MLPAE
import utils

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from tqdm import tqdm

### Constants
TOTAL_POINTS = 10000
N_CLUSTERS = 10
RATIOS = np.array([0.16,0.15,0.05,0.1,0.2,0.05,0.05,0.12,0.08,0.04]) # might need random assignments for ratio
# RATIOS = np.ones(N_CLUSTERS) * (1/N_CLUSTERS) # balanced clusters --- DP and KMeans same performance

myGenerator = DataGenerator(samples=TOTAL_POINTS, n_features=100, n_clusters=N_CLUSTERS, spread=[1,30], ratio_per_cluster=RATIOS)
X, labels, centers = myGenerator.generate_data()

X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.8, random_state=0)

#%% OG dim reduction
X_train_LDA, X_test_LDA = utils.dimension_reduction_LDA(X_train,y_train,X_test, 4) #could change up to 10

#%% DPGMM comparison 
clf_dp = BGM(n_components=20, covariance_type="full", weight_concentration_prior_type='dirichlet_process')
clf_dp.fit(X_train)
y_pred_dp = clf_dp.predict(X_test)

### some params
# dp_mean = clf.means_,
# dp_cov = clf.covariances_

# plt.figure(1, figsize=(8,8))
# plt.clf()
# plt.scatter(X_train[:,2],X_train[:,3])
# plt.show()

#%% LDA + DPGMM
clf_comb = BGM(n_components=20, covariance_type="full", weight_concentration_prior_type='dirichlet_process')
clf_comb.fit(X_train_LDA)
y_pred_comb = clf_comb.predict(X_test_LDA)

# comb_mean = clf_comb.means_,
# comb_cov = clf_comb.covariances_

# plt.figure(2, figsize=(8,8))
# plt.clf()
# plt.scatter(X_test_LDA[:,2],X_test_LDA[:,3])
# plt.show()

#%% K-means
clf_kmeans = KMeans(n_clusters=10)
clf_kmeans.fit(X_train)
kmeans_mean = clf_kmeans.cluster_centers_
y_pred_kmeans = clf_kmeans.predict(X_test)

#%% use S-score
dp_rscore = rand_score(y_test, y_pred_dp)
comb_rscore = rand_score(y_test, y_pred_comb)
km_rscore = rand_score(y_test, y_pred_kmeans)

dp_sscore = silhouette_score(X_test, y_pred_dp)
comb_sscore = silhouette_score(X_test_LDA, y_pred_comb)
km_sscore = silhouette_score(X_test, y_pred_kmeans)

dp_arscore = adjusted_rand_score(y_test, y_pred_dp) # better than rand index as a metrics?
comb_arscore = adjusted_rand_score(y_test, y_pred_comb)
km_arscore = adjusted_rand_score(y_test, y_pred_kmeans)

print('###### RI ######')
print(dp_rscore)
print(comb_rscore)
print(km_rscore)

print('###### Silhouette Score ######')
print(dp_sscore)
print(comb_sscore)
print(km_sscore)

print('###### ARI ######')
print(dp_arscore)
print(comb_arscore)
print(km_arscore)

class_dp = set(y_pred_dp)
class_comb = set(y_pred_comb)
class_km = set(y_pred_kmeans)
class_true = set(y_pred_kmeans)

print('###### Clusters ######')
print(class_dp)
print(class_comb)
print(class_km)
print(class_true)
print(len(class_dp))
print(len(class_comb))
print(len(class_km))
print(len(class_true))


#%% try plotting

# X_train_tSNE = utils.dimension_reduction_TSNE(X_train, 2) #could change up to 10
# X_test_tSNE  = utils.dimension_reduction_TSNE(X_test, 2) #could change up to 10

# clf_tSNE = BGM(n_components=20, covariance_type="full", weight_concentration_prior_type='dirichlet_process')
# clf_tSNE.fit(X_train_tSNE)
# y_pred_tSNE = clf_tSNE.predict(X_test_tSNE)

# tSNE_rscore = rand_score(y_test, y_pred_tSNE)
# tSNE_sscore = silhouette_score(X_test_tSNE, y_pred_tSNE)
# tSNE_arscore = adjusted_rand_score(y_test, y_pred_tSNE)

# print('###### tSNE ######')
# print(tSNE_rscore)
# print(tSNE_sscore)
# print(tSNE_arscore)

# class_tSNE = set(y_pred_tSNE)
# print(class_tSNE)
# print(len(class_tSNE))

# # if we really need plots ... 
# utils.plot_results(
#   X_test_tSNE,
#   y_pred_tSNE,
#   clf_tSNE.means_,
#   clf_tSNE.covariances_,
#   title="DPBGM with tSNE",
# )

#%% Try DNN on DIM
TOTAL_POINTS = 100000
IMAGE_DIM = 32
N_CLUSTERS = 10
RATIOS = np.array([0.16,0.15,0.05,0.1,0.2,0.05,0.05,0.12,0.08,0.04]) # might need random assignments for ratio

myGenerator = DataGenerator(samples=TOTAL_POINTS, n_features=IMAGE_DIM*IMAGE_DIM, n_clusters=N_CLUSTERS, spread=20, ratio_per_cluster=RATIOS, lower_bound=0, upper_bound=100)
X, labels, centers = myGenerator.generate_data()
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.8, random_state=0)

train_dataset = TensorDataset(torch.Tensor(X_train), torch.Tensor(y_train))
test_dataset = TensorDataset(torch.Tensor(X_test), torch.Tensor(y_test))

#%% DNN Fun

### Need StandardScaler?
EPOCHS = 1
BATCH_SIZE = 32
device = 'cuda' if torch.cuda.is_available() else 'cpu'

train_losses = np.zeros(EPOCHS)
model = MLPAE(in_components=IMAGE_DIM*IMAGE_DIM, out_components=16).to(device)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in tqdm(range(EPOCHS)):
  train_loss = utils.train(model, device, train_loader, criterion, optimizer)

  train_losses[epoch] = train_loss
  print(f'Training loss for AE is: {train_loss}')

X_train, X_test, y_train, y_test = utils.get_datasets(model, device, train_loader, test_loader)
print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)