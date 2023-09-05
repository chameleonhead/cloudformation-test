FROM centos:7
# Cent OS 9 で実行しようとしたところ、Oracle Database Client のインストールでエラーとなった。
# 解決方法がわからないので、Cent OS 7 に変更。
# FROM quay.io/centos/centos:stream9

USER root

# Oracle のインストーラーに入っている jre は GUI の表示でエラーになることがあったので
# ディストリビューションの java をインストールし、JAVA_HOME を設定することで
# 回避している。
RUN yum install -y \
    sudo \
    unzip \
    java-11-openjdk-headless \
    # Oracle Database Client 19c のインストールに必要なパッケージ
    # https://docs.oracle.com/cd/F19136_01/lacli/supported-red-hat-enterprise-linux-8-distributions-for-x86-64.html#GUID-B1487167-84F8-4F8D-AC31-A4E8F592374B
    bc \
    binutils \
    elfutils-libelf \
    elfutils-libelf-devel \
    fontconfig-devel \
    glibc \
    glibc-devel \
    ksh \
    libaio \
    libaio-devel \
    libXrender \
    libX11 \
    libXau \
    libXi \
    libXtst \
    libgcc \
    libnsl \
    librdmacm \
    libstdc++ \
    libstdc++-devel \
    libxcb \
    libibverbs \
    make \
    policycoreutils \
    policycoreutils-python-utils \
    smartmontools \
    sysstat
ENV JAVA_HOME=/usr/lib/jvm/jre

COPY LINUX.X64_193000_client.zip client_install.rsp 191001_fbo_ggs_Linux_x64_services_shiphome.zip oggcore.rsp oggca.rsp /tmp/orainstall/

# Oracle Database Client 19c の配置
# https://docs.oracle.com/cd/F19136_01/lacli/running-oracle-universal-installer-to-install-oracle-database-client.html#GUID-DB056013-736D-4A7A-8C98-607103E2F07F
# LINUX.X64_193000_client.zip を展開すると client/runInstaller が現れる
RUN unzip -q /tmp/orainstall/LINUX.X64_193000_client.zip -d /tmp/orainstall

# Oracle GoldenGate Microservices Architecture の配置
# https://docs.oracle.com/cd/F22974_01/installing/installing-microservices-architecture-oracle-goldengate.html#GUID-2E805D77-8362-460A-BA61-D267FC303863
RUN unzip /tmp/orainstall/191001_fbo_ggs_Linux_x64_services_shiphome.zip -d /tmp/orainstall

# oracle ユーザーの作成
RUN groupadd -g 54321 oinstall && \
    useradd  -u 54321 -g oinstall oracle

# oracle ユーザーに sudo 権限を付与 (コンテナでの動作確認用)
RUN yum install -y passwd && echo oracle | passwd --stdin oracle && usermod -aG wheel oracle

# Oracle ユーザーの所有に変更 (インストールディレクトリも設定しないとSegmentation fault が発生する)
RUN mkdir -p /opt/oracle && \
    chown -R oracle:oinstall /tmp/orainstall && \
    chown -R oracle:oinstall /opt/oracle && \
    chmod -R 775 /opt/oracle

# Oracle Database Client 19c のインストール
USER oracle
RUN /tmp/orainstall/client/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /tmp/orainstall/client_install.rsp || true
USER root
RUN /opt/oracle/oraInventory/orainstRoot.sh
USER oracle
ENV ORACLE_HOME=/opt/oracle/product/19.3.0/client_1 \
    PATH=/opt/oracle/product/19.3.0/client_1/bin:$PATH

# Oracle GoldenGate Microservices Architecture のインストール
RUN /tmp/orainstall/fbo_ggs_Linux_x64_services_shiphome/Disk1/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /tmp/orainstall/oggcore.rsp
ENV OGG_HOME=/opt/oracle/product/19.1.0/oggcore_1 \
    PATH=/opt/oracle/product/19.1.0/oggcore_1/bin:$PATH

# Deployment の作成
RUN /opt/oracle/product/19.1.0/oggcore_1/bin/oggca.sh -silent -responseFile /tmp/orainstall/oggca.rsp

# Service Manager
EXPOSE 11000
# Administration server
EXPOSE 11001
# Distribution server
EXPOSE 11002
# Receiver server
EXPOSE 11003
# Performance Metrics server (TCP)
EXPOSE 11004
# Performance Metrics server (UDP)
EXPOSE 11005

COPY docker-entrypoint.sh /
CMD [ "/docker-entrypoint.sh" ]
