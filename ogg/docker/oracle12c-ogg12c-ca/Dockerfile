FROM quay.io/centos/centos:7

USER root

# 必要なパッケージのインストール
RUN yum install -y \
    sudo \
    unzip \
    # Oracle Database Client 12c のインストールに必要なパッケージ
    # https://docs.oracle.com/cd/E57425_01/121/LADBI/pre_install.htm
    binutils \
    compat-libcap1 \
    compat-libstdc++-33 \
    gcc \
    gcc-c++ \
    glibc \
    glibc-devel \
    ksh \
    libaio \
    libaio-devel \
    libgcc \
    libstdc++ \
    libstdc++-devel \
    libXi \
    libXtst \
    make \
    sysstat \
    # Additional packages for Oracle Database
    net-tools \
    smartmontools

# https://docs.oracle.com/cd/E82638_01/ladbi/changing-kernel-parameter-values.html#GUID-FB0CC366-61C9-4AA2-9BE7-233EB6810A31
# https://docs.oracle.com/cd/E51614_01/doc.12104/e49732/dbinstall.htm
RUN echo "fs.aio-max-nr = 1048576" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "fs.file-max = 6815744" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "kernel.shmall = 2097152" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "kernel.shmmax = 4294967295" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "kernel.shmmni = 4096" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "kernel.sem = 250 32000 100 128" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "net.ipv4.ip_local_port_range = 9000 65500" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "net.core.rmem_default = 262144" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "net.core.rmem_max = 4194304" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "net.core.wmem_default = 262144" >> /etc/sysctl.d/97-oracle-database-sysctl.conf \
    echo "net.core.wmem_max = 1048576" >> /etc/sysctl.d/97-oracle-database-sysctl.conf && \
    /sbin/sysctl --system || true

# https://docs.oracle.com/en/database/oracle/oracle-database/12.2/ladbi/checking-resource-limits-for-oracle-software-installation-users.html#GUID-293874BD-8069-470F-BEBF-A77C06618D5A
RUN echo "oracle soft nofile 1024" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle hard nofile 65536" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle soft nproc 16384" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle hard nproc 16384" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle soft stack 10240" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle hard stack 32768" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle hard memlock unlimit" >> /etc/security/limits.d/97-oracle-limits.conf && \
    echo "oracle soft memlock unlimit" >> /etc/security/limits.d/97-oracle-limits.conf

# oracle ユーザーの作成
RUN groupadd -g 54321 oinstall && \
    groupadd -g 54322 dba && \
    groupadd -g 54323 oper && \
    groupadd -g 54324 backupdba && \
    groupadd -g 54325 dgdba && \
    groupadd -g 54326 kmdba && \
    groupadd -g 54330 racdba && \
    useradd  -u 54321 -g oinstall oracle && \
    usermod -aG dba,oper,backupdba,dgdba,kmdba,racdba oracle

# oracle ユーザーに sudo 権限を付与 (コンテナでの動作確認用)
RUN yum install -y passwd && echo oracle | passwd --stdin oracle && usermod -aG wheel oracle

# Oracle ユーザーの所有に変更 (インストールディレクトリも設定しないとSegmentation fault が発生する)
RUN mkdir -p /opt/oracle && \
    chown -R oracle:oinstall /opt/oracle && \
    chmod -R 775 /opt/oracle

USER oracle

# Oracle Database Client 12c のインストールに必要なファイルをコピー
RUN mkdir /home/oracle/install
COPY --chown=oracle:oinstall linuxx64_12201_database.zip /home/oracle/install/
COPY --chown=oracle:oinstall db_install.rsp /home/oracle/install/
COPY --chown=oracle:oinstall netca.rsp /home/oracle/install/
COPY --chown=oracle:oinstall dbca.rsp /home/oracle/install/

# Oracle Database Client 12c の配置
# https://docs.oracle.com/cd/F19136_01/lacli/running-oracle-universal-installer-to-install-oracle-database-client.html#GUID-DB056013-736D-4A7A-8C98-607103E2F07F
# linuxx64_12201_database.zip を展開すると database/runInstaller が現れる
RUN unzip -q /home/oracle/install/linuxx64_12201_database.zip -d /home/oracle/install && \
    /home/oracle/install/database/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /home/oracle/install/db_install.rsp || true && \
    rm -rf /home/oracle/install/database
USER root
RUN /home/oracle/oraInventory/orainstRoot.sh && /opt/oracle/product/12c/dbhome_1/root.sh
USER oracle
ENV ORACLE_HOME=/opt/oracle/product/12c/dbhome_1 \
    PATH=/opt/oracle/product/12c/dbhome_1/bin:$PATH

# Oracle GoldenGate Classic Architecture のインストールに必要なファイルをコピー
COPY 123010_fbo_ggs_Linux_x64_shiphome.zip /home/oracle/install/
COPY oggcore.rsp /home/oracle/install/

ENV OGG_HOME=/opt/oracle/ogg \
    LD_LIBRARY_PATH=$ORACLE_HOME/lib
ENV PATH=$OGG_HOME:$PATH

WORKDIR /opt/oracle/ogg
COPY docker-entrypoint.sh /
CMD [ "/docker-entrypoint.sh" ]
