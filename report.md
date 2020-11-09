## 信息检索系统实验报告

##### 2017011439    韩之雄    计76

### 一.实验环境

- Python 3.7.0

- Elasticsearch 7.9.3
- Flask 1.1.2

- Thulac(python版本) 0.2.1

### 二.实验过程

#### 2.1 convert.py

语料的预处理文件。由于计算资源和时间的限制，我只选择了rmrb1946-2003-delrepeat.txt和Sogou{0010-0014}.txt作为语料库。首先把所有文件按行读入，每行作为一个文本，存入`rmrbData`。原本考虑把thulac包作为插件载入elasticsearch，但是由于环境配置等问题没有成功，故采用先分词后搭建es索引的方式。在convert.py中我把每个文本分别采用thulac的`seg_only=True`和`seg_only=False`两种分词方式，记作`tokens`和`ptokens`，以及原文本`text`，存入rmrb.json等待后续使用。

#### 2.2 index.py

搭建索引的过程，首先确定mapping方式，由于分词的结果是以空格间隔的term字符串，所以mapping时设置使用whitespace analyzer，建立索引后把所有文本导入，`raw`，`text`，`ptext`分别对应JSON文件中的`text`，`tokens`，`ptokens`。

#### 2.3query.py

搜索请求的处理过程。如果是普通的关键词搜索，把查询语句也使用thulac进行分词，然后直接使用`elasticsearch_dsl.search.query`的`match`匹配方式即可；如果是输入单词完全匹配的搜索方式，即使用`elasticsearch_dsl.search.query`的`match_phrase`的匹配方式。需要注意的是如果设置两个词相邻那么`match_phrase`的参数`slop`是默认的0，如果不相邻那么先设置`slop`参数是无穷大，再从匹配的结果中过滤掉相邻的instance即可。上面讨论的搜索均是针对`text`进行的，如果要设置搜索单词词性，那么搜索将在`ptext`中进行，匹配方式就可以直接使用`match_phrase`了。对于搜索的结果，我还做了高亮处理。

