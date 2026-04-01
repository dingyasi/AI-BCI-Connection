"""
快速训练测试 - 生成模拟数据训练Hopfield模型
"""

import numpy as np
import pickle

print("开始训练...")

# 生成模拟EEG数据
np.random.seed(42)
n_samples = 90  # 30样本 x 3类
n_channels = 64
n_features = n_channels * 100  # 展平

# 3类运动想象数据
X = []
y = []

for cls in range(3):
    for i in range(30):
        # 创建有区分度的特征
        base = np.random.randn(n_features) * 0.5

        # 添加类别特征
        if cls == 0:  # 左手
            base[1000:2000] += 2
        elif cls == 1:  # 右手
            base[3000:4000] += 2
        else:  # 脚
            base[5000:6000] += 2

        X.append(base)
        y.append(cls)

X = np.array(X)
y = np.array(y)

print(f"数据形状: {X.shape}")

# 简单预处理
X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

# PCA降维
from app.algorithm.pca import PCA

pca = PCA(n_components=16)
X_reduced = pca.fit_transform(X)
print(f"PCA降维后: {X_reduced.shape}")

# Hopfield训练
from app.algorithm.hopfield import HopfieldNetwork

hopfield = HopfieldNetwork(n_neurons=16)
hopfield.train(X_reduced)

# 测试
labels, iterations, energy = hopfield.predict(X_reduced)
accuracy = np.mean(labels == y) * 100
print(f"准确率: {accuracy:.1f}%")

# 保存模型
model_data = {
    "pca": pca,
    "hopfield": hopfield,
    "config": {
        "n_pca_components": 16,
        "accuracy": accuracy,
        "variance_ratio": pca.explained_variance_ratio.tolist()[:10],
    },
}

with open("eeg_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("模型已保存到 eeg_model.pkl")
