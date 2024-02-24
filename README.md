<div class="title" align=center>
    <h1>Novel2Anki</h1>
	<div>基于视觉小说文本批量制作 Anki 交互式日语学习卡片</div>
    <br/>
    <p>
        <img src="https://img.shields.io/github/license/2DIPW/audio_dataset_vpr">
    	  <img src="https://img.shields.io/badge/python-3.11-blue">
        <img src="https://img.shields.io/github/stars/2DIPW/novel2anki?style=social">
    </p>
</div>

## 🚩 简介
本项目是一个利用视觉小说类游戏解包文本（或任何以句为单位的角色、原文、译文、语音文件一一对应的数据）快速批量制作 Anki 交互式日语学习卡片的工具，具有如下特性：
* 通过日语形态素解析词典 [Sudachi](https://github.com/WorksApplications/Sudachi) 的更适合日语学习者的解析器 [dango](https://github.com/mkartawijaya/dango) 解析每一句日语原文可能的形态素构成，并用不同颜色区分每个单词的词性。
* 对于部分单词，查询本地 Mdict 词典获得其释义附加在卡片上，并通过 JavaScript 模板实现点击句中对应单词时显示释义的交互功能。
* 还可同时添加在线词典的查询链接，在点击链接时方便地跳转至外部网站查询该单词。
* 若该句存在对应的语音文件，也可将其附加在卡片上，在学习卡片时播放。

由于形态素分析和词典查询均为程序自动完成，对于语法复杂的句子存在很大的局限性，本项目仅供相关技术的思路展示和交流，旨在通过自己喜欢的游戏激发学习兴趣，所有生成结果仅供参考，请多加验证，做出自己的判断。本项目不对盲目轻信生成结果造成的不良影响负责。

## 💻 截图
![Screenshot]()

## 📥 部署
### 克隆（或直接下载本仓库）
```shell
git clone https://github.com/2DIPW/novel2anki.git
cd novel2anki
```
### 创建虚拟环境（可选，以Conda为例）
```shell
conda create -n novel2anki python=3.11
conda activate novel2anki
```
### 安装依赖
```shell
pip install -r requirements.txt
```

### 配置本地查词词典
本项目目前仅支持 Mdict 词典`*.mdx`，你可以将任意以日语为索引的 Mdict 词典和其对应的样式文件`*.css`置于`dict`目录，并修改配置文件`config.yaml`中对应的地址。
```yaml
Local_Dict: "./dict/超級クラウン日中辞典.mdx"  # 本地词典的路径
Local_Dict_CSS: "./dict/超級クラウン日中辞典.css"  # 本地词典样式表的路径，供generate_deck_model.py自动生成Anki模板用
```

由于本项目根据 MeCab 解析的单词辞书形为索引自动查词，无法像词典软件那样可以搜索近似词供用户选择，索引编排更加精确的词典可能拥有更好的查词效果。

### 配置 Anki Connect 并生成牌组和模板
确保 Anki 和 Anki Connect 插件已经正常安装并启动，如果没有修改过 Anki Connect 的默认配置，通常你只需要更改牌组名`Anki/Deck`字段，生成的卡片均会保存到该牌组。
```yaml
Anki:  # Anki Connect的设置
  URL: http://127.0.0.1:8765  # Anki Connect的监听地址，如果没有改过Anki Connect的默认设置就不需要改
  Key: ""  # 密钥，如果没有改过Anki Connect的默认设置就不需要设
  Deck: "ATRI"  # 牌组名
  Model: "Novel2Anki"  # 模板名
  Front: "正面"  # 正面字段
  Back: "背面"  # 背面字段
  Allow_Duplicate: false  # 允许重复
  Media_Server_Port: 5001  # 向Anki Connect发送语音文件的服务器的监听端口，如果没有端口冲突就不需要改
```

之后，运行牌组和模板自动创建程序，会为 Anki 自动新建牌组和模板：
```shell
python generate_deck_model.py
```
前一步在`Local_Dict_CSS`字段中配置的词典样式文件会作为一个\<style\>标签置于卡片背面模板的顶部，`template`目录下本项目预设的卡片交互JS脚本会作为一个\<script\>标签至于置于卡片背面模板的底部，卡片交互CSS将添加到“样式”中，可在 Anki 的`管理笔记模板`中自行微调。

## 🗝 使用方法
### 准备数据
- 你需要准备一份以制表符分隔（也可通过参数指定其他的分隔符）的表格，**第1列为角色，第2列为日文原文，第3列为译文，第4列为对应的语音文件名**，除日文原文外其他值均可为空，但是必须有制表符来维持表格结构，其格式应该如同下面的例子：
   ```
   夏生	どうしてアトリが……	为什么亚托莉在这……	
   水菜萌	お母さんに頼まれて、夕飯の買い物に行く途中で見付けたの	妈妈让我去买晚饭的食材，我在路上遇到她的	MIN_b102_006.mp3
   アトリ	はい、水菜萌。連れてきてくれてありがとうです。ぺこり	嗯，水菜萌。谢谢你带我过来。鞠躬	ATR_b102_048.mp3
   ```
- 如果希望附加语音到卡片，你还需要准备与上表中文件名对应的语音文件，将他们存放在`voice`目录。
- 不同视觉小说类游戏使用不同的引擎，即使引擎相同的游戏，其解包获得的数据结构也具有较大差别，因此本项目目前仅提供了针对游戏《ATRI -My Dear Moments-》解包文件进行解析转换的示例脚本（使用方法详见README）。对于其他游戏，请编写相应的脚本以按照以上格式准备数据。
### 编辑配置文件
编辑配置文件`config.yaml`的以下字段，以定制生成的卡片。
  ```yaml
    Use_Dict_For:  # 对于哪些词性需要使用词典查询  将不需要的词性注释掉
    - NOUN  # 名詞
    #- NAME  # 人名
    #- PLACE_NAME  # 地名
    #- NUMBER  # 数詞
    #- COUNTER  # 助数詞
    #- PRONOUN  # 代名詞
    - VERB  # 動詞
    - ADJECTIVE  # 形容詞
    - ADJECTIVAL_NOUN  # 形状詞
    - ADVERB  # 副詞
    #- PARTICLE  # 助詞
    #- AUXILIARY_VERB  # 助動詞
    - PRE_NOUN_ADJECTIVAL  # 連体詞
    #- INTERJECTION  # 感動詞
    #- SUFFIX  # 接尾辞
    - CONJUNCTION  # 接続詞
    - PREFIX  # 接頭辞
 
    Include:  # 卡片背面包含哪些组分
      Character: true  # 说话人标识
      Sentence_Original: true  # 语法解析后的原句子，禁用此项后单词解释也将被禁用
      Sentence_Translated: true  # 句子译文
      Explanation_For_Word: true  # 单词解释，禁用此项后将不会进行词典查词，可节省时间
      Voice: true  # 语音
    
    Tag:  # 是否添加标签
      Character: true  # 添加说话人标签
      Has_Voice: true  # 添加有语音/无语音标签
    
    Sentence_Length_Limitation:  # 句子长度限制
      Min: 10  # 长度小于此值的句子将被忽略，可排除仅有语气词等的过短句
      Max: 50  # 长度大于此值的句子将被忽略，可防止牌组过大
  ```
### 运行卡片生成
- 使用`novel2anki.py`：
    ```shell
    python novel2anki.py -i 数据文件路径
    ```
    可指定的参数:
    - `-i` | `--input`: 数据文件路径。默认值：`data.txt`
    - `-d` | `--delimiter`: 数据文件分隔符。默认值：`\t`
    - `-v` | `--voice`: 语音文件路径。默认值：`voice/`
    - `-ch` | `--character`: 指定制作哪些角色的卡片，多个角色以空格分隔，角色名需要与数据文件第一列中的角色名对应，以"NULL"代表没有角色名的句子（一般为内心独白）。若不指定该参数，则制作所有角色的卡片。
    - `-dnv` | `--discard_no_voice`: 舍弃所有没有语音的句子。
    - `-c` | `--config`: 手动指定配置文件路径。默认值：`config.yaml`

## ⚖ 开源声明

本项目基于 [GNU General Public License v3.0](https://github.com/2DIPW/novel2anki/blob/master/LICENSE) 开源。

本项目部分源码来自 [mmjang/mdict-query](https://github.com/mmjang/mdict-query) 和 [xwang/mdict-analysis](https://bitbucket.org/xwang/mdict-analysis/src/master/) 并有一定修改。

本项目的诞生离不开这些优秀的开源项目：
* [mkartawijaya/dango](https://github.com/mkartawijaya/dango)：BSD-3-Clause license
* [PyYAML](https://pyyaml.org/)：MIT License
* [BeautifulSoup](https://code.launchpad.net/beautifulsoup)：MIT license
* [Flask](https://github.com/pallets/flask/)：BSD-3-Clause license

*世界因开源更精彩*