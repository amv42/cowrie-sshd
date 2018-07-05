
# Installing Cowrie in seven steps.

* [Step 1: Install dependencies](#step-1-install-dependencies)
* [Step 2: Create a user account](#step-2-create-a-user-account)
* [Step 3: Checkout the code](#step-3-checkout-the-code)
* [Step 4: Setup Virtual Environment](#step-4-setup-virtual-environment)
* [Step 5: Install configuration file](#step-5-install-configuration-file)
* [Step 6: Generate a DSA key (OPTIONAL)](#step-6-generate-a-dsa-key)
* [Step 7: Starting Cowrie](#step-7-turning-on-cowrie)
* [Step 8: Port redirection (OPTIONAL)](#step-8-port-redirection-optional)
* [Running within supervisord (OPTIONAL)](#running-using-supervisord)
* [Configure Additional Output Plugins (OPTIONAL)](#configure-additional-output-plugins-optional)
* [Troubleshooting](#troubleshooting)

## Step 1: Install dependencies

First we install system-wide support for Python virtual environments and other dependencies.
Actual Python packages are installed later.

On Debian based systems (last verified on Debian 9, 2017-07-25):
```
$ sudo apt-get install git python-virtualenv libssl-dev libffi-dev build-essential libpython-dev python2.7-minimal authbind
```

## Step 2: Create a user account

It's strongly recommended to run with a dedicated non-root user id:

```
$ sudo adduser --disabled-password cowrie
Adding user `cowrie' ...
Adding new group `cowrie' (1002) ...
Adding new user `cowrie' (1002) with group `cowrie' ...
Changing the user information for cowrie
Enter the new value, or press ENTER for the default
Full Name []:
Room Number []:
Work Phone []:
Home Phone []:
Other []:
Is the information correct? [Y/n]

$ sudo su - cowrie
```

## Step 3: Checkout the code

```
$ git clone https://github.com/amv42/cowrie-sshd
Cloning into 'cowrie-sshd'...
remote: Counting objects: 9905, done.
remote: Compressing objects: 100% (2961/2961), done.
remote: Total 9905 (delta 6798), reused 9897 (delta 6790), pack-reused 0
Receiving objects: 100% (9905/9905), 7.63 MiB | 9.32 MiB/s, done.
Resolving deltas: 100% (6798/6798), done.
Checking connectivity... done.

$ cd cowrie-sshd
```

## Step 4: Setup Virtual Environment

Next you need to create your virtual environment:

```
$ pwd
/home/cowrie/cowrie
$ virtualenv cowrie-env
New python executable in ./cowrie/cowrie-env/bin/python
Installing setuptools, pip, wheel...done.
```

Alternatively, create a Python3 virtual environment (under development)
```
$ virtualenv --python=python3 cowrie-env
New python executable in ./cowrie/cowrie-env/bin/python
Installing setuptools, pip, wheel...done.
```

Activate the virtual environment and install packages

```
$ source cowrie-env/bin/activate

(cowrie-env) $ pip install --upgrade pip

(cowrie-env) $ pip install --upgrade -r requirements.txt
```

## Step 5: Install configuration file

The configuration for Cowrie is stored in cowrie.cfg.dist and
cowrie.cfg. Both files are read on startup, where entries from
cowrie.cfg take precedence. The .dist file can be overwritten by
upgrades, cowrie.cfg will not be touched. To run with a standard
configuration, there is no need to change anything. To enable telnet,
for example, create cowrie.cfg and input only the following:

```
[telnet]
enabled = true
```

## Step 6: Generate a DSA key (OPTIONAL)

This step should not be necessary, however some versions of Twisted
are not compatible. To avoid problems in advance, run:

```
$ cd data
$ ssh-keygen -t dsa -b 1024 -f ssh_host_dsa_key
$ cd ..
```

## Step 7: Starting Cowrie

Start Cowrie with the cowrie command. You can add the cowrie/bin
directory to your path if desired. An existing virtual environment
is preserved if activated, otherwise Cowrie will attempt to load
the environment called "cowrie-env"

```
$ bin/cowrie start
Activating virtualenv "cowrie-env"
Starting cowrie with extra arguments [] ...
```

## Step 8: Port redirection (OPTIONAL)

All port redirection commands are system-wide and need to be executed as root.

Cowrie-sshd runs by default on localhost (127.0.0.1) and port 65522. This can be modified in the configuration file.
The following firewall rule will forward incoming traffic on port 22 to port 65222 (default port for sshd-honeypot).

```
$ sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 65222
```

Note that you should test this rule only from another host; it
doesn't apply to loopback connections. Alternatively you can run
authbind to listen as non-root on port 22 directly:

```
$ sudo apt-get install authbind
$ sudo touch /etc/authbind/byport/22
$ sudo chown cowrie:cowrie /etc/authbind/byport/22
$ sudo chmod 770 /etc/authbind/byport/22
```

Or for telnet:

```
$ apt-get install authbind
$ sudo touch /etc/authbind/byport/23
$ sudo chown cowrie:cowrie /etc/authbind/byport/23
$ sudo chmod 770 /etc/authbind/byport/23
```

* Edit bin/cowrie and modify the AUTHBIND_ENABLED setting
* Change listen_port to 22 in cowrie.cfg

## Running using Supervisord (OPTIONAL)

On Debian, put the below in /etc/supervisor/conf.d/cowrie.conf
```
[program:cowrie]
command=/home/cowrie/cowrie/bin/cowrie start
directory=/home/cowrie/cowrie/
user=cowrie
autorestart=true
redirect_stderr=true
```
Update the bin/cowrie script, change:
 ```
 DAEMONIZE=""
 ```
 to:
 ```
 DAEMONIZE="-n"
 ```

## Configure Additional Output Plugins (OPTIONAL)

Cowrie automatically outputs event data to text and JSON log files
in ~/cowrie/log.  Additional output plugins can be configured to
record the data other ways.  Supported output plugins include:

* Cuckoo
* ELK (Elastic) Stack
* Graylog
* Kippo-Graph
* Splunk
* SQL (MySQL, SQLite3, RethinkDB)

See ~/cowrie/doc/[Output Plugin]/README.md for details.


## Troubleshooting

* If you see `twistd: Unknown command: cowrie` there are two
possibilities. If there's a python stack trace, it probably means
there's a missing or broken dependency. If there's no stack trace,
double check that your PYTHONPATH is set to the source code directory.
* Default file permissions

To make Cowrie logfiles public readable, change the ```--umask 0077``` option in start.sh into ```--umask 0022```

# Updating Cowrie

Updating is an easy process. First stop your honeypot. Then fetch updates from GitHub, as a next step upgrade your Python dependencies.

```
bin/cowrie stop
git pull
pip install --upgrade -r requirements.txt
bin/cowrie start
```

# Modifying Cowrie

The pre-login banner can be set by creating the file `honeyfs/etc/issue.net`.
The post-login banner can be customized by editing `honeyfs/etc/motd`.
