-- CDBユーザー権限
-- https://docs.oracle.com/cd/F51462_01/ggmas/quickstart-your-data-replication-oracle-goldengate-microservices-architecture.html#GUID-FAAAFDB1-FF77-4EF5-A85C-3FBBB832CCD1
-- CGGNORTH DATABASE SETUP AT CDB LEVEL
alter system set enable_goldengate_replication=TRUE scope=both;
alter system set streams_pool_size=100m scope=both;

shutdown immediate;
startup mount;
alter database archivelog;
alter database open;

alter database add supplemental log data;
alter database force logging;
alter system switch logfile;
archive log list;

create tablespace GG_DATA datafile '/opt/oracle/oradata/ORCL/gg_data.dbf' size 100m autoextend on next 100m;
create user ggadmin identified by passw0rd default tablespace GG_DATA temporary tablespace temp;
grant create session to ggadmin;
grant alter any table to ggadmin;
grant resource to ggadmin;
grant dba to ggadmin;
exec dbms_goldengate_auth.grant_admin_privilege('ggadmin');
