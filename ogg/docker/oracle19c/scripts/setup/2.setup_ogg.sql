shutdown immediate;
startup mount;
alter databse archivelog;
alter database open;

-- CDBユーザー権限
-- https://docs.oracle.com/cd/F51462_01/ggmas/quickstart-your-data-replication-oracle-goldengate-microservices-architecture.html#GUID-FAAAFDB1-FF77-4EF5-A85C-3FBBB832CCD1
-- CGGNORTH DATABASE SETUP AT CDB LEVEL
alter session set container=cdb$root;
alter system set enable_goldengate_replication=TRUE;
alter system set streams_pool_size=2G;
alter database force logging;
alter database add supplemental log data;
archive log list;
create tablespace GG_DATA datafile '+DATA' size 100m autoextend on next 100m;
create user c##ggadmin identified by Password container=all default tablespace GG_DATA temporary tablespace temp;
grant alter system to c##ggadmin container=all;
grant dba to c##ggadmin container=all;
grant create session to c##ggadmin container=all;
grant alter any table to c##ggadmin container=all;
grant resource to c##ggadmin container=all;
exec dbms_goldengate_auth.grant_admin_privilege('c##ggadmin',container=>'all');

-- ソースPDBユーザー権限(ORCLPDB1)
alter session set container=ORCLPDB1;
create tablespace GG_DATA datafile '+DATA' size 100m autoextend on next 100m;
create user ggadmin identified by Password container=current; 
grant create session to ggadmin container=current;
grant alter any table to ggadmin container=current;
grant resource to ggadmin container=current;
grant dba to ggadmin container=current;
exec dbms_goldengate_auth.grant_admin_privilege('ggadmin');