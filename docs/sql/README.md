# How to Send Cowrie Output to a MySQL Database


## Prerequisites

* Working Cowrie installation
* MySQL Server installation


## Installation

```
$ sudo apt-get install mysql-server libmysqlclient-dev python-mysqldb
$ su - cowrie
$ source cowrie/cowrie-env/bin/activate
$ pip install mysqlclient

```

Previously MySQL-python was used. Only if you run into isses with mysqlclient, try this instead:
```
$ pip install MySQL-python
```

## MySQL Configuration

First create an empty database named 'cowrie'.
```
$ mysql -u root -p
CREATE DATABASE cowrie;
```

Create a cowrie user account for the database and grant access privileges:

**All Privileges:**

```
GRANT ALL ON cowrie.* TO 'cowrie'@'localhost' IDENTIFIED BY 'PASSWORD HERE';

```

**Restricted Privileges:**

Alternatively you can grant the cowrie account with less privileges. The following command grants the account with the
bare minimum required for the output logging to function:

```
GRANT INSERT, SELECT, UPDATE ON cowrie.* TO 'cowrie'@'localhost' IDENTIFIED BY 'PASSWORD HERE';
```

Apply the privilege settings and exit mysql.
```
FLUSH PRIVILEGES;
exit
```

Next, log into the MySQL database using the cowrie account to verify proper access privileges and load the database schema provided in the docs/sql/ directory:
```
$ cd ~/cowrie/docs/sql/
$ mysql -u cowrie -p
USE cowrie;
source mysql.sql;
exit
```


## Cowrie Configuration

Uncomment and update the following entries to ~/cowrie/cowrie.cfg under the Output Plugins section:

```
[output_mysql]
host = localhost
database = cowrie
username = cowrie
password = PASSWORD HERE
port = 3306
debug = false
```


## Restart Cowrie

```
$ cd ~/cowrie/bin/
$ ./cowrie restart
```


## Verify That the MySQL Output Engine Has Been Loaded

Check the end of the ~/cowrie/log/cowrie.log to make sure that the MySQL output engine has loaded successfully.
```
$ cd ~/cowrie/log/
$ tail cowrie.log
```

Example expected output:
```
2017-11-27T22:19:44-0600 [-] Loaded output engine: jsonlog
2017-11-27T22:19:44-0600 [-] Loaded output engine: mysql
...
2017-11-27T22:19:58-0600 [-] Ready to accept SSH connections

```


## Confirm That Events are Logged to the MySQL Database
Wait patiently for a new login attempt to occur.  Use tail like before to quickly check if any activity has 
been recorded in the cowrie.log file.

Once a login event has occurred, log back into the MySQL database and verify that the event was recorded:

```
$ mysql -u cowrie -p
USE cowrie;
SELECT * FROM auth;
```

Example output:
```
+----+--------------+---------+----------+-------------+---------------------+
| id | session      | success | username | password    | timestamp           |
+----+--------------+---------+----------+-------------+---------------------+
|  1 | a551c0a74e06 |       0 | root     | 12345       | 2017-11-27 23:15:56 |
|  2 | a551c0a74e06 |       0 | root     | seiko2005   | 2017-11-27 23:15:58 |
|  3 | a551c0a74e06 |       0 | root     | anko        | 2017-11-27 23:15:59 |
|  4 | a551c0a74e06 |       0 | root     | 123456      | 2017-11-27 23:16:00 |
|  5 | a551c0a74e06 |       0 | root     | dreambox    | 2017-11-27 23:16:01 |
...
```
