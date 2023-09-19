# 参考:https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html
import oracledb
connection = oracledb.connect(user="c##admin", password="passw0rd", dsn="oracle19c/ORCLCDB")
cur = connection.cursor()
cur.execute("""SELECT name FROM v$pdbs""")