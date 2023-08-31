FROM quay.io/centos/centos:stream9

# Oracle GoldenGate Microservices Architectureのインストール
# https://docs.oracle.com/cd/F22974_01/installing/installing-microservices-architecture-oracle-goldengate.html#GUID-2E805D77-8362-460A-BA61-D267FC303863
# 
# 注意
# インストーラーに入っている jre は GUI の表示でエラーになることがあったので
# ディストリビューションの java をインストールし、JAVA_HOME を設定することで
# 回避している。

USER root

COPY 191001_fbo_ggs_Linux_x64_services_shiphome.zip oggcore.rsp /tmp/ogginstall/

RUN groupadd -g 54321 oinstall && \
    useradd  -u 54321 -g oinstall oracle && \
    yum install -y unzip java-11-openjdk-headless && \
    mkdir -p /u01/stage/oggsc && \
    unzip /tmp/ogginstall/191001_fbo_ggs_Linux_x64_services_shiphome.zip -d /u01/stage/oggsc && \
    chown -R oracle:oinstall /u01

ENV JAVA_HOME=/usr/lib/jvm/jre \
    PATH=$JAVA_HOME/bin:$PATH

USER oracle

RUN /u01/stage/oggsc/fbo_ggs_Linux_x64_services_shiphome/Disk1/runInstaller -silent -nowait -responseFile /tmp/ogginstall/oggcore.rsp
