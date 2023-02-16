# SoftVC VITS Singing Voice Conversion (DirectML)

## DirectML
> 如何启用Pytorch for DirectML，请参阅[微软文档](https://learn.microsoft.com/en-us/windows/ai/directml/gpu-pytorch-windows)\
> 可用状态：
+ 预处理：基本可用
+ 训练：完全不可用（直到微软解决部分数据类型不支持的问题）
+ 推理：基本可用
+ onnx/gradio:没有经过测试
> 测试平台：Intel Arc A770 16GB\
> 问题：在预训练或推理过程中，都有很大概率遇到黑屏等情况而导致程序终止。
![](gpu.png)
## 以下是原仓库说明
## English docs
[英语资料](Eng_docs.md)
## Update
> 据不完全统计，多说话人似乎会导致**音色泄漏加重**，不建议训练超过5人的模型，目前的建议是如果想炼出来更像目标音色，**尽可能炼单说话人的**\
> 断音问题已解决，音质提升了不少\
> 2.0版本已经移至 sovits_2.0分支\
> 3.0版本使用FreeVC的代码结构，与旧版本不通用\
> 与[DiffSVC](https://github.com/prophesier/diff-svc) 相比，在训练数据质量非常高时diffsvc有着更好的表现，对于质量差一些的数据集，本仓库可能会有更好的表现，此外，本仓库推理速度上比diffsvc快很多


## 模型简介
歌声音色转换模型，通过SoftVC内容编码器提取源音频语音特征，与F0同时输入VITS替换原本的文本输入达到歌声转换的效果。同时，更换声码器为 [NSF HiFiGAN](https://github.com/openvpi/DiffSinger/tree/refactor/modules/nsf_hifigan) 解决断音问题


## 注意
+ 当前分支是32khz版本的分支，32khz模型推理更快，显存占用大幅减小，数据集所占硬盘空间也大幅降低，推荐训练该版本模型
+ 如果要训练48khz的模型请切换到[main分支](https://github.com/innnky/so-vits-svc/tree/main) 


## 预先下载的模型文件
+ soft vc hubert：[hubert-soft-0d54a1f4.pt](https://github.com/bshall/hubert/releases/download/v0.1/hubert-soft-0d54a1f4.pt)
  + 放在hubert目录下
+ 预训练底模文件 [G_0.pth](https://huggingface.co/innnky/sovits_pretrained/resolve/main/G_0.pth) 与 [D_0.pth](https://huggingface.co/innnky/sovits_pretrained/resolve/main/D_0.pth)
  + 放在logs/32k 目录下
  + 预训练底模为必选项，因为据测试从零开始训练有概率不收敛，同时底模也能加快训练速度
  + 预训练底模训练数据集包含云灏 即霜 辉宇·星AI 派蒙 绫地宁宁，覆盖男女生常见音域，可以认为是相对通用的底模
  + 底模删除了optimizer speaker_embedding 等无关权重, 只可以用于初始化训练，无法用于推理
  + 该底模和48khz底模通用
```shell
# 一键下载
# hubert
wget -P hubert/ https://github.com/bshall/hubert/releases/download/v0.1/hubert-soft-0d54a1f4.pt
# G与D预训练模型
wget -P logs/32k/ https://huggingface.co/innnky/sovits_pretrained/resolve/main/G_0.pth
wget -P logs/32k/ https://huggingface.co/innnky/sovits_pretrained/resolve/main/D_0.pth

```


## colab一键数据集制作、训练脚本
[一键colab](https://colab.research.google.com/drive/1_-gh9i-wCPNlRZw6pYF-9UufetcVrGBX?usp=sharing)


## 数据集准备
仅需要以以下文件结构将数据集放入dataset_raw目录即可
```shell
dataset_raw
├───speaker0
│   ├───xxx1-xxx1.wav
│   ├───...
│   └───Lxx-0xx8.wav
└───speaker1
    ├───xx2-0xxx2.wav
    ├───...
    └───xxx7-xxx007.wav
```


## 数据预处理
1. 重采样至 32khz

```shell
python resample.py
 ```
2. 自动划分训练集 验证集 测试集 以及自动生成配置文件
```shell
python preprocess_flist_config.py
# 注意
# 自动生成的配置文件中，说话人数量n_speakers会自动按照数据集中的人数而定
# 为了给之后添加说话人留下一定空间，n_speakers自动设置为 当前数据集人数乘2
# 如果想多留一些空位可以在此步骤后 自行修改生成的config.json中n_speakers数量
# 一旦模型开始训练后此项不可再更改
```
3. 生成hubert与f0
```shell
python preprocess_hubert_f0.py
```
执行完以上步骤后 dataset 目录便是预处理完成的数据，可以删除dataset_raw文件夹了


## 训练
```shell
python train.py -c configs/config.json -m 32k
```


## 推理

使用 [inference_main.py](inference_main.py)
+ 更改model_path为你自己训练的最新模型记录点
+ 将待转换的音频放在raw文件夹下
+ clean_names 写待转换的音频名称
+ trans 填写变调半音数量
+ spk_list 填写合成的说话人名称


## Onnx导出
### 重要的事情说三遍：导出Onnx时，请重新克隆整个仓库！！！导出Onnx时，请重新克隆整个仓库！！！导出Onnx时，请重新克隆整个仓库！！！
使用 [onnx_export.py](onnx_export.py)
+ 新建文件夹：checkpoints 并打开
+ 在checkpoints文件夹中新建一个文件夹作为项目文件夹，文件夹名为你的项目名称
+ 将你的模型更名为model.pth，配置文件更名为config.json，并放置到刚才创建的文件夹下
+ 将 [onnx_export.py](onnx_export.py) 中path = "NyaruTaffy" 的 "NyaruTaffy" 修改为你的项目名称
+ 运行 [onnx_export.py](onnx_export.py) 
+ 等待执行完毕，在你的项目文件夹下会生成一个model.onnx，即为导出的模型
+ 注意：若想导出48K模型，请按照以下步骤修改文件，或者直接使用48K.py
   + 请打开[model_onnx.py](model_onnx.py)，将其中最后一个class的hps中32000改为48000
   + 请打开[nvSTFT](/vdecoder/hifigan/nvSTFT.py)，将其中所有32000改为48000
   ### Onnx模型支持的UI
   + [MoeSS](https://github.com/NaruseMioShirakana/MoeSS)
+ 我去除了所有的训练用函数和一切复杂的转置，一行都没有保留，因为我认为只有去除了这些东西，才知道你用的是Onnx

## Gradio（WebUI）
使用 [sovits_gradio.py](sovits_gradio.py)
+ 新建文件夹：checkpoints 并打开
+ 在checkpoints文件夹中新建一个文件夹作为项目文件夹，文件夹名为你的项目名称
+ 将你的模型更名为model.pth，配置文件更名为config.json，并放置到刚才创建的文件夹下
+ 运行 [sovits_gradio.py](sovits_gradio.py) 


