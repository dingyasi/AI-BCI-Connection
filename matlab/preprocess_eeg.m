function preprocess_all(data_dir, save_dir)

    % ===== 默认参数 =====
    if nargin < 1
        data_dir = 'D:/NEW_start_xiaoD/study/data';
    end
    if nargin < 2
        save_dir = 'D:/EEG/processed';
    end

    fprintf('===== 批量EEG预处理开始 =====\n');

    % ===== 扫描所有被试 =====
    d = dir(data_dir);
    subject_list = {};

    for i = 1:length(d)
        if d(i).isdir && startsWith(d(i).name,'S')
            subject_list{end+1} = d(i).name;
        end
    end

    fprintf('检测到 %d 个被试\n\n', length(subject_list));

    % ===== 批处理 =====
    for i = 1:length(subject_list)
        subject_id = subject_list{i};

        try
            preprocess_single(subject_id, data_dir, save_dir);
        catch ME
            fprintf('❌ %s 失败: %s\n', subject_id, ME.message);
        end
    end

    fprintf('\n===== 全部处理完成 =====\n');
end


% =====================================================
% =============== 单个被试处理函数 =====================
% =====================================================
function preprocess_single(subject_id, data_dir, save_dir)

    fprintf('===== 处理被试: %s =====\n', subject_id);

    tasks_left  = {'R03','R07','R11'};
    tasks_right = {'R04','R08','R12'};
    tasks_feet  = {'R05','R09','R13'};

    fs = 160;

    all_data = [];
    all_labels = [];

    % ===== 加载数据 =====
    [all_data, all_labels] = load_group(tasks_left, 0, subject_id, data_dir, all_data, all_labels);
    [all_data, all_labels] = load_group(tasks_right,1, subject_id, data_dir, all_data, all_labels);
    [all_data, all_labels] = load_group(tasks_feet, 2, subject_id, data_dir, all_data, all_labels);

    if isempty(all_data)
        fprintf('❌ %s 无数据，跳过\n\n', subject_id);
        return;
    end

    fprintf('原始: %d trials\n', size(all_data,3));

    % ===== 预处理 =====
    fprintf('滤波中...\n');
    all_data = notch_filter(all_data,50,fs);
    all_data = bandpass_filter(all_data,8,30,fs);

    fprintf('基线校正...\n');
    all_data = baseline_correct(all_data);

    fprintf('标准化...\n');
    all_data = normalize_data(all_data);

    % ===== 保存 =====
    if ~exist(save_dir,'dir')
        mkdir(save_dir);
    end

    out_file = fullfile(save_dir,[subject_id '_preprocessed.mat']);
    save(out_file,'all_data','all_labels','-v7.3');

    fprintf('✅ 保存: %s\n\n', out_file);
end


% =====================================================
% ==================== 数据加载 ========================
% =====================================================
function [all_data, all_labels] = load_group(tasks, label, subject_id, data_dir, all_data, all_labels)
    for i = 1:length(tasks)
        [data, labels] = load_task(subject_id, tasks{i}, data_dir, label);
        if ~isempty(data)
            all_data = cat(3, all_data, data);
            all_labels = [all_labels, labels];
        end
    end
end


function [data, labels] = load_task(subject_id, task, data_dir, label)

    edf_file = fullfile(data_dir, subject_id, [subject_id task '.edf']);

    if ~exist(edf_file,'file')
        fprintf('⚠️ 文件不存在: %s\n', edf_file);
        data=[]; labels=[]; return;
    end

    fprintf('加载: %s\n', edf_file);

    try
        [~, record] = edfread(edf_file);
        record = double(record(1:64,:));

        n_trials = 6;
        trial_len = 12800;
        skip = 1000;

        data = [];
        labels = [];

        for i = 1:n_trials
            s = (i-1)*16000 + skip;
            e = s + trial_len;

            if e <= size(record,2)
                data = cat(3,data,record(:,s:e));
                labels = [labels,label];
            end
        end

    catch err
        fprintf('❌ 读取失败: %s\n', err.message);
        data=[]; labels=[];
    end
end


% =====================================================
% ==================== 信号处理 ========================
% =====================================================
function out = notch_filter(data,freq,fs)

    [b,a] = butter(2,[freq-2,freq+2]/(fs/2),'stop');

    [n_channels, ~, n_trials] = size(data);
    out = zeros(size(data));

    for t = 1:n_trials
        for c = 1:n_channels
            out(c,:,t) = filtfilt(b,a,data(c,:,t));
        end
    end
end


function out = bandpass_filter(data,low,high,fs)

    [b,a] = butter(4,[low,high]/(fs/2),'bandpass');

    [n_channels, ~, n_trials] = size(data);
    out = zeros(size(data));

    for t = 1:n_trials
        for c = 1:n_channels
            out(c,:,t) = filtfilt(b,a,data(c,:,t));
        end
    end
end


function out = baseline_correct(data)
    base = mean(data(:,1:1000,:),2);
    out = data - base;
end


function out = normalize_data(data)
    m = mean(data,2);
    s = std(data,0,2);
    s(s<1e-6) = 1;
    out = (data - m) ./ s;
end