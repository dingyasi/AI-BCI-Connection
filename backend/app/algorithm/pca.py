"""
PCA降维模块
"""

import numpy as np


class PCA:
    def __init__(self, n_components: int = 16):
        self.n_components = n_components
        self.mean = None
        self.components = None
        self.explained_variance_ratio = None

    def fit(self, X: np.ndarray):
        """训练PCA模型"""
        # 数据标准化
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean

        # 计算协方差矩阵
        cov_matrix = np.cov(X_centered.T)

        # 特征值分解
        eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

        # 取实部（避免数值误差）
        eigenvalues = np.real(eigenvalues)
        eigenvectors = np.real(eigenvectors)

        # 排序
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # 选取前n_components个主成分
        self.components = eigenvectors[:, : self.n_components]
        self.explained_variance_ratio = eigenvalues[: self.n_components] / np.sum(
            eigenvalues
        )

        return self

    def transform(self, X: np.ndarray):
        """降维转换"""
        X_centered = X - self.mean
        return np.dot(X_centered, self.components)

    def fit_transform(self, X: np.ndarray):
        """训练并转换"""
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X_reduced: np.ndarray):
        """逆转换（可选）"""
        return np.dot(X_reduced, self.components.T) + self.mean


def load_edf_data(file_path: str):
    """加载EDF格式EEG数据"""
    try:
        import mne

        raw = mne.io.read_raw_edf(file_path, preload=True)
        data = raw.get_data()  # (n_channels, n_times)
        return data
    except ImportError:
        # 备用方案：手动解析EDF
        return load_edf_manual(file_path)


def load_edf_manual(file_path: str):
    """手动解析EDF文件"""
    with open(file_path, "rb") as f:
        # EDF文件头解析
        header = f.read(256)

        # 获取通道数和采样数
        n_channels = int(header[252:254].decode())
        n_samples = int(header[244:252].decode())

        # 读取数据
        data = np.frombuffer(f.read(n_channels * n_samples * 2), dtype=np.int16)
        data = data.reshape(n_channels, n_samples)

        return data.astype(np.float64)


def preprocess_eeg(data: np.ndarray, sampling_rate: int = 128):
    """EEG预处理"""
    # 1. 陷波滤波 - 去除50Hz工频干扰
    from scipy.signal import butter, filtfilt

    # 50Hz陷波滤波
    notch_freq = 50
    quality_factor = 30
    b, a = butter(
        2, [notch_freq / 0.5, notch_freq * 1.5], btype="bandstop", fs=sampling_rate
    )
    data = filtfilt(b, a, data, axis=1)

    # 2. 带通滤波 - 提取8-30Hz Mu/Beta节律
    low_freq, high_freq = 8, 30
    b, a = butter(4, [low_freq, high_freq], btype="bandpass", fs=sampling_rate)
    data = filtfilt(b, a, data, axis=1)

    # 3. 基线校正
    data = data - np.mean(data, axis=1, keepdims=True)

    # 4. Z-score标准化
    data = (data - np.mean(data, axis=1, keepdims=True)) / np.std(
        data, axis=1, keepdims=True
    )

    return data


def extract_trials(data: np.ndarray, trial_length: int = 128, overlap: int = 0):
    """提取试验片段"""
    n_channels = data.shape[0]
    step = trial_length - overlap
    n_trials = (data.shape[1] - trial_length) // step + 1

    trials = []
    for i in range(n_trials):
        start = i * step
        trial = data[:, start : start + trial_length]
        trials.append(trial.flatten())

    return np.array(trials)
