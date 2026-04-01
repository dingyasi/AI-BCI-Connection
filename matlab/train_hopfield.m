%% =======================
% 批量 Hopfield 网络训练脚本
% 功能：
%   1. 批量加载预处理好的 EEG 数据
%   2. 对每类提取典型模式压缩
%   3. PCA 降维
%   4. Hopfield 联想记忆训练（Hebb 规则）
%   5. 测试分类准确率 + 混淆矩阵
%
% 使用示例：
%   subject_dir = 'D:/NEW_start_xiaoD/study/matlab/processed';
%   train_hopfield_all(subject_dir, 16, 2);

function train_hopfield_all(data_dir, n_pca, n_mode_per_class)
    if nargin < 1
        data_dir = 'D:/NEW_start_xiaoD/study/matlab/processed';
    end
    if nargin < 2
        n_pca = 16;  % PCA 降维维度
    end
    if nargin < 3
        n_mode_per_class = 2;  % 每类保留的典型模式数量
    end

    fprintf('===== Hopfield 批量训练 =====\n');
    fprintf('数据路径: %s\n', data_dir);
    
    % 获取所有预处理数据文件
    files = dir(fullfile(data_dir, '*_preprocessed.mat'));
    if isempty(files)
        error('❌ 没有找到任何预处理文件!');
    end

    all_patterns = [];
    all_labels = [];

    % =======================
    % 1. 批量加载数据 + 每类模式压缩
    for f = 1:length(files)
        file_path = fullfile(files(f).folder, files(f).name);
        fprintf('加载: %s\n', file_path);
        tmp = load(file_path);
        X = tmp.all_data;    % (channels, samples, trials)
        y = tmp.all_labels;  % (1 x trials)

        n_trials = size(X,3);

        for cls = 0:2  % 左手/右手/脚
            idx = find(y == cls);
            if isempty(idx), continue; end
            X_cls = X(:,:,idx);  % 选出这一类 trial
            
            % PCA 压缩每个 trial
            X_flat = [];
            for i = 1:size(X_cls,3)
                X_flat = [X_flat; X_cls(:,:,i)'];
            end
            % 对这一类 trial 做 PCA 压缩
            [coeff, score, ~] = pca(X_flat);
            X_pca_cls = X_flat * coeff(:,1:n_pca);
            
            % 取前 n_mode_per_class 个模式均值作为代表
            n_take = min(n_mode_per_class, size(X_pca_cls,1));
            for k = 1:n_take
                all_patterns = [all_patterns; sign(X_pca_cls(k,:))];  % 转 +1/-1
                all_labels = [all_labels, cls];
            end
        end
    end

    fprintf('总模式数: %d, PCA特征维度: %d\n', size(all_patterns,1), n_pca);

    % =======================
    % 2. Hopfield 联想记忆训练 (Hebb 规则)
    n_patterns = size(all_patterns,1);
    W = (all_patterns' * all_patterns) / n_patterns;
    W = W - diag(diag(W));     % 去除自连接
    W = (W + W') / 2;          % 对称化

    fprintf('Hopfield 网络训练完成!\n');

    % =======================
    % 3. 测试模式恢复
    fprintf('测试模型...\n');
    preds = zeros(1, n_patterns);
    for i = 1:n_patterns
        state = all_patterns(i,:);
        % 异步更新
        for iter = 1:500
            idx = randi(n_pca);
            h = W(idx,:) * state';
            new_state = sign(h);
            if new_state == state(idx), break; end
            state(idx) = new_state;
        end
        % 最近邻分类：找最相似的训练模式
        sim = all_patterns * state';
        [~, idx_max] = max(sim);
        preds(i) = all_labels(idx_max);
    end

    % =======================
    % 4. 输出准确率 & 混淆矩阵
    acc = mean(preds == all_labels) * 100;
    fprintf('准确率: %.2f%%\n', acc);

    fprintf('混淆矩阵:\n');
    for cls = 0:2
        idx = find(all_labels == cls);
        counts = histc(preds(idx), 0:2);
        fprintf('  真实%d: 左手=%d, 右手=%d, 脚=%d\n', cls, counts(1), counts(2), counts(3));
    end

    % =======================
    % 5. 保存模型
    save_file = fullfile(data_dir, 'hopfield_model_all.mat');
    save(save_file, 'W', 'n_pca', 'n_mode_per_class', 'acc', 'all_labels');
    fprintf('模型已保存: %s\n', save_file);
end