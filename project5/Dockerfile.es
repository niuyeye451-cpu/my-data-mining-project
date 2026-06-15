FROM docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# 安装 IK 中文分词插件（新下载地址：get.infini.cloud）
RUN elasticsearch-plugin install --batch \
    https://get.infini.cloud/elasticsearch/analysis-ik/8.17.0
