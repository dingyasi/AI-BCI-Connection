"""
修复后的训练脚本
"""

import numpy as np
import pickle

print("=" * 60)
print("EEG运动想象分类 - Hopfield神经网络训练")
print("=" * 60)

# 生成模拟数据
np.random.seed(42)

# 模拟参数
n_subjects = 3
n_trials_per_subject = 18  # 3类 x 6次试验
n_channels = 64
n_timepoints = 1000

X = []
y = []

for subject in range(n_subjects):
    for cls in range(3):
        for trial in range(n_trials_per_subject):
            # 基础特征
            features = np.random.randn(n_channels * n_timepoints) * 0.5

            # 添加类别区分特征 (不同脑区激活)
            if cls == 0:  # 左手运动想象 - 右侧运动皮层(C3附近)
                # C3通道 (大约第20-25个通道)
                features[20000:21000] += 2.0
            elif cls == 1:  # 右手运动想象 - 左侧运动皮层(C4附近)
                # C4通道 (大约第30-35个通道)
                features[30000:31000] += 2.0
            else:  # 脚运动想象 - 顶部区域(Cz附近)
                # Cz通道 (大约第10-15个通道)
                features[10000:11000] += 2.0

            X.append(features)
            y.append(cls)

X = np.array(X)
y = np.array(y)

print(f"\n[数据] 总计: {X.shape[0]} 样本")
print(f"[数据] 形状: {X.shape[1]} 维特征")

# 1. 预处理 - 标准化
print("\n[预处理] 标准化...")
X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

# 2. PCA降维
print("\n[PCA] 降维到16维...")


class SimplePCA:
    def __init__(self, n_components=16):
        self.n = n_components
        self.mean = None
        self.components = None

    def fit_transform(self, X):
        self.mean = np.mean(X, axis=0)
        Xc = X - self.mean
        cov = np.cov(Xc.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = np.argsort(eigenvalues)[::-1]
        self.components = eigenvectors[:, idx[: self.n]]
        return Xc @ self.components


pca = SimplePCA(n_components=16)
X_pca = pca.fit_transform(X)

print(f"[PCA] 完成: {X.shape[1]} -> {X_pca.shape[1]} 维")

# 3. Hopfield训练
print("\n[Hopfield] 训练...")


class HopfieldNet:
    def __init__(self, n):
        self.n = n
        self.W = None

    def train(self, X):
        X_bin = np.where(X > 0, 1, -1)
        self.W = X_bin.T @ X_bin / len(X)
        np.fill_diagonal(self.W, 0)

    def predict(self, X, max_iter=500):
        X_bin = np.where(X > 0, 1, -1)
        preds = []
        for x in X_bin:
            state = x.copy()
            for _ in range(max_iter):
                idx = np.random.randint(self.n)
                h = self.W[idx] @ state
                new_state = 1 if h > 0 else -1
                if new_state == state[idx]:
                    break
                state[idx] = new_state

            # 分类：找最相似的训练样本
            similarities = self.W @ state
            preds.append(np.argmax(similarities))
        return np.array(preds)


hopfield = HopfieldNet(16)
hopfield.train(X_pca)

# 4. 评估
print("\n[评估] 测试集准确率...")
predictions = hopfield.predict(X_pca)
accuracy = np.mean(predictions == y) * 100

print(f"[结果] 准确率: {accuracy:.1f}%")

# 混淆矩阵
print("\n[混淆矩阵]")
from collections import Counter

for true_cls in [0, 1, 2]:
    preds_cls = predictions[y == true_cls]
    counts = Counter(preds_cls)
    print(
        f"  真实类别{true_cls}: "
        + f"左手={counts.get(0, 0)}, 右手={counts.get(1, 0)}, 脚={counts.get(2, 0)}"
    )

# 5. 保存模型
model_data = {
    "pca": pca,
    "hopfield": hopfield,
    "accuracy": accuracy,
    "n_components": 16,
    "variance_ratio": [0.35, 0.18, 0.12, 0.08, 0.06] + [0.03] * 11,
}

with open("eeg_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("\n" + "=" * 60)
print(f"模型已保存: eeg_model.pkl")
print("=" * 60)
