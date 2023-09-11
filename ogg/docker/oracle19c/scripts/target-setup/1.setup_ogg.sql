-- CDBユーザー権限
-- https://docs.oracle.com/cd/F51462_01/ggmas/quickstart-your-data-replication-oracle-goldengate-microservices-architecture.html#GUID-FAAAFDB1-FF77-4EF5-A85C-3FBBB832CCD1
-- CGGNORTH DATABASE SETUP AT CDB LEVEL
alter session set container=cdb$root;
alter system set enable_goldengate_replication=TRUE scope=both;

-- ターゲットPDBユーザー権限(ORCLPDB1)
alter session set container=ORCLPDB1;
create user ggadmin identified by passw0rd container=current;
grant alter system to ggadmin container=current;
grant create session to ggadmin container=current;
grant alter any table to ggadmin container=current;
grant resource to ggadmin container=current;
grant dba to ggadmin container=current;
grant dv_goldengate_admin, dv_goldengate_redo_access to ggadmin container=current;
exec dbms_goldengate_auth.grant_admin_privilege('ggadmin');
