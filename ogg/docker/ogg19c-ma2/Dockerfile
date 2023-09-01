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
        # https://docs.oracle.com/cd/F19136_01/lacli/supported-oracle-linux-8-distributions-for-x86-64.html#GUID-F4902762-325B-4C89-B85B-F52BA482190F
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
# 簡略のためなら以下でもいいかも？(未検証)
# RUN yum install -y \
#         sudo \
#         java-11-openjdk-headless
# RUN yum groupinstall -y 'Development Tools' --setopt=group_package_types=mandatory

COPY LINUX.X64_193000_client.zip client_install.rsp 191001_fbo_ggs_Linux_x64_services_shiphome.zip oggcore.rsp /tmp/orainstall/

# Oracle Database Client 19c の配置
# https://docs.oracle.com/cd/F19136_01/lacli/running-oracle-universal-installer-to-install-oracle-database-client.html#GUID-DB056013-736D-4A7A-8C98-607103E2F07F
# LINUX.X64_193000_client.zip を展開すると client/runInstaller が現れる
RUN mkdir -p /u01/stage/clientsc && \
    unzip -q /tmp/orainstall/LINUX.X64_193000_client.zip -d /u01/stage/clientsc

# Oracle GoldenGate Microservices Architecture の配置
# https://docs.oracle.com/cd/F22974_01/installing/installing-microservices-architecture-oracle-goldengate.html#GUID-2E805D77-8362-460A-BA61-D267FC303863
RUN mkdir -p /u01/stage/oggsc && \
    unzip /tmp/orainstall/191001_fbo_ggs_Linux_x64_services_shiphome.zip -d /u01/stage/oggsc

# oracle ユーザーの作成
RUN groupadd -g 54321 oinstall && \
    useradd  -u 54321 -g oinstall oracle && \
    mkdir -p /u01/app/oraInventory && \
    chown -R oracle:oinstall /u01/stage && \
    chown -R oracle:oinstall /u01/app

# oracle ユーザーに sudo 権限を付与 (コンテナでの動作確認用)
RUN yum install -y passwd && echo oracle | passwd --stdin oracle && usermod -aG wheel oracle

ENV JAVA_HOME=/usr/lib/jvm/jre \
    PATH=$JAVA_HOME/bin:$PATH

USER oracle

# Oracle Database Client 19c のインストール
RUN /u01/stage/clientsc/client/runInstaller -silent -waitForCompletion -responseFile /tmp/orainstall/client_install.rsp || true
USER root
RUN /u01/app/oraInventory/orainstRoot.sh
USER oracle

# Oracle GoldenGate Microservices Architecture のインストール
RUN /u01/stage/oggsc/fbo_ggs_Linux_x64_services_shiphome/Disk1/runInstaller -silent -waitForCompletion -responseFile /tmp/orainstall/oggcore.rsp

ENV ORACLE_HOME=/u01/app/oracle/product/19.3.0/client_1 \
    OGG_HOME=/u01/app/ogg \
    PATH=$ORACLE_HOME/bin:$OGG_HOME/bin:$PATH
