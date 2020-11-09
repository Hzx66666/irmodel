运行方式：
cd $ELASTICSEARCH_ROOT
./elasticsearch
cd $REPO_ROOT
python index.py    
python query.py

文件说明：
convert.py 语料库预处理，包括分词
index.py 索引构建
query.py 搜索后端处理
rmrb.json 处理后的预料数据
templates/page_query.html 搜索前端页面
templates/page_SERP.html 搜索结果前端页面
