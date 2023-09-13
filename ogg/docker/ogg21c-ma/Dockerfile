FROM quay.io/centos/centos:stream9

USER root

# インストールに必要なパッケージのインストール
RUN dnf install -y \
    sudo \
    unzip \
    # Oracle GoldenGate Microservices Architecture のインストールに必要なパッケージ
    # https://stackoverflow.com/a/66006075
    libnsl \
    libaio

# oracle ユーザーの作成
RUN groupadd -g 54321 oinstall && \
    useradd  -u 54321 -g oinstall oracle

# oracle ユーザーに sudo 権限を付与 (コンテナでの動作確認用)
RUN dnf install -y passwd && echo oracle | passwd --stdin oracle && usermod -aG wheel oracle

# Oracle ユーザーの所有に変更 (インストールディレクトリも設定しないとSegmentation fault が発生する)
RUN mkdir -p /tmp/orainstall && \
    mkdir -p /opt/oracle && \
    chown -R oracle:oinstall /tmp/orainstall && \
    chown -R oracle:oinstall /opt/oracle && \
    chmod -R 775 /opt/oracle

USER oracle

# Oracle GoldenGate Microservices Architecture のインストールに必要なファイルをコピー
COPY 213000_fbo_ggs_Linux_x64_Oracle_services_shiphome.zip /tmp/orainstall/
COPY oggcore.rsp oggca.rsp /tmp/orainstall/

# Oracle GoldenGate Microservices Architecture の配置
# https://docs.oracle.com/cd/F22974_01/installing/installing-microservices-architecture-oracle-goldengate.html#GUID-2E805D77-8362-460A-BA61-D267FC303863
RUN unzip /tmp/orainstall/213000_fbo_ggs_Linux_x64_Oracle_services_shiphome.zip -d /tmp/orainstall

# Oracle GoldenGate Microservices Architecture のインストール
RUN /tmp/orainstall/fbo_ggs_Linux_x64_Oracle_services_shiphome/Disk1/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /tmp/orainstall/oggcore.rsp
USER root
RUN /home/oracle/oraInventory/orainstRoot.sh
USER oracle
ENV OGG_HOME=/opt/oracle/product/21.3.0/oggcore_1

# Deploymentの作成は起動時に実施
ENV PORT_BASE=11000

# デフォルトでは以下のポートを使用する
# 11000: Service Manager
# 11001: Administration server
# 11002: Distribution server
# 11003: Receiver server
# 11004: Performance Metrics server (TCP)
# 11005: Performance Metrics server (UDP)

USER root
COPY docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh

USER oracle
WORKDIR /home/oracle
CMD [ "/docker-entrypoint.sh" ]
