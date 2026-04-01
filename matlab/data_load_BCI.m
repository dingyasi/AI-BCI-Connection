data_location='E:\BaiduNetdiskDownload\2026-本科毕设\数据\eeg-motor-movementimagery-dataset-1.0.0（数据集1原始数据）\files\';
k=1;
data_A=[]; %%处理不同类型数据，可以改变字母
for i=100:109% 根据不同数据集的数据名规则确定
%   for j=1:3
      %% 定义样本个数为k
%定义读取的数据名
if i<10
location = strcat(data_location,'S00',num2str(i));
%  data_name = strcat('S',num2str(i),'A0',num2str(j),'.edf');

if i<100 && i>=10
location = strcat(data_location,'S0',num2str(i));
if i>=100
location = strcat(data_location,'S',num2str(i));   
end


 cd(location) %%切换到当前存储数据位置   任务3、7、11一类任务；4、8、12次一类任务；3、9、13一类任务；4、10、14一类任务。

% cfg.dataset  = data_name;
[hdr,record] = edfread('S100R03.edf'); %%观察record明显7-38行才是需要的结果
data_A(k,:,:)= record(1:64,1:12800);%%为了消除每个原始数据长度不一致，可以截断相同长度部分数据128*100（采样频率128Hz) 根据实际情况决定公共最短的整数长度
k=k+1;
[hdr,record1] = edfread('S100R07.edf'); %%观察record明显7-38行才是需要的结果
data_A(k,:,:)= record(1:64,1:12800);%%为了消除每个原始数据长度不一致，可以截断相同长度部分数据128*100（采样频率128Hz) 根据实际情况决定公共最短的整数长度
k=k+1;
[hdr,record2] = edfread('S100R11.edf'); %%观察record明显7-38行才是需要的结果
 data_A(k,:,:)= record(1:64,1:12800);%%为了消除每个原始数据长度不一致，可以截断相同长度部分数据128*100（采样频率128Hz) 根据实际情况决定公共最短的整数长度
k=k+1;
%%
%%  直接分析某一类型的数据  小波分析，EEG 小波，功率谱分析。
%如果数据格式是.set
% %     if any(find([1 2 3 10 12 14]==s))  
%         if s<10
% %         setFileName = strcat('0',num2str(s),'_C','.set');
% %         setFileName = strcat('0',num2str(s),'_P50','.set');
%         setFileName = strcat('0',num2str(s),'_P80','.set');
% 
%         else
%              setFileName = strcat(num2str(s),'_C','.set');
% %             setFileName = strcat(num2str(s),'_P50','.set'); 
%          setFileName = strcat(num2str(s),'_P80','.set');
%         end   
eeg = pop_loadset(setFileName, filePath);%%location=filePath
record = eeg.data;%% eeg 数据
event = eeg.event;
srate = eeg.srate;
data0 = double(eeg.data); % 把eeg.data设定为double格式
srate = eeg.srate;

% data_A(k,:,:)= record(1:64,1:12800);%%为了消除每个原始数据长度不一致，可以截断相同长度部分数据128*100（采样频率128Hz)
% k=k+1;
%%获得类别A所有EEG数据样本 60*32*15232 数据格式
%%可以对32进行平均mean(data_A,2)，获得60个序列长度为15232样本（也可以等分截断序列进行降维处理）
%% 也可以对时间进行平均mean(data_A,1)，获得60个序列长度为32的样本。
%%此处可以进行简单平均预处理，将最终60个样本的特征序列手动保存到exel测试集或者训练集中，因为
% 数据样本明显不大，操作起来比较简便。
%   end
end

