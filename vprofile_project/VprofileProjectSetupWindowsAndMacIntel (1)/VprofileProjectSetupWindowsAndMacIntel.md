**VPROFILE PROJECT SETUP![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.001.png)**

**Prerequisite**

1. Oracle VM Virtualbox
1. Vagrant
1. Vagrant plugins

Execute below command in your computer to install hostmanager plugin

$ vagrant plugin install vagrant-hostmanager![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.002.png)

4. Git bash or equivalent editor

**VM SETUP**

1. Clone source code.
1. Cd into the repository.
1. Switch to the main branch.
1. cd into vagrant/Manual\_provisioning

Bring up vm’s

*$ vagrant up![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.003.png)*

NOTE: Bringing up all the vm’s may take a long time based on various factors. If vm setup stops in the middle run “vagrant up” command again.

INFO: All the vm’s hostname and /etc/hosts file entries will be automatically updated.

![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.004.png)

**PROVISIONING**

**Services**

1. Nginx => Web Service![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.005.png)
1. Tomcat => Application Server
1. RabbitMQ => Broker/Queuing Agent
1. Memcache => DB Caching
1. ElasticSearch => Indexing/Search service
1. MySQL => SQL Database

Setup should be done in below mentioned order

**MySQL (Database SVC) Memcache (![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.006.png)DB Caching SVC) RabbitMQ (Broker/Queue SVC) Tomcat (Application SVC) Nginx (Web SVC)**

**1. MYSQL Setup**

Login to the db vm

*$ vagrant ssh db01![ref1]*

Verify Hosts entry, if entries missing update the it with IP and hostnames

- *cat /etc/hosts![ref1]*

Update OS with latest patches

- *yum update -y![ref1]*

Set Repository

- *yum install epel-release -y![ref1]*

Install Maria DB Package

- *yum install git mariadb-server -y![ref1]*

Starting & enabling mariadb-server

- *systemctl start mariadb![ref2]*
- *systemctl enable mariadb*

RUN mysql secure installation script.

- *mysql\_secure\_installation![ref3]*

***NOTE**: Set db root password, I will be using **admin123 as password***

Set root password? [Y/n]**Y ![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.010.png)**New password:

Re-enter new password: Password updated successfully! Reloading privilege tables..

... Success!

By default, a MariaDB installation has an anonymous user, allowing anyone to log into MariaDB without having to have a user account created for them. This is intended only for testing, and to make the installation go a bit smoother. You should remove them before moving into a production environment.

Remove anonymous users? [Y/n]**Y**

... Success!

Normally, root should only be allowed to connect from 'localhost'. This ensures that someone cannot guess at the root password from the network.

Disallow root login remotely? [Y/n]**n**

... skipping.

By default, MariaDB comes with a database named 'test' that anyone can access. This is also intended only for testing, and should be removed before moving into a production environment.

Remove test database and access to it? [Y/n]**Y**

- Dropping test database...

... Success!

- Removing privileges on test database... ... Success!

Reloading the privilege tables will ensure that all changes made so far will take effect immediately.

Reload privilege tables now? [Y/n]**Y**

... Success!

Set DB name and users.

- *mysql -u root -padmin123![ref3]*

*mysql> create database accounts;![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.011.png)*

*mysql> grant all privileges on accounts.\* TO 'admin'@'%' identified by 'admin123'; mysql> FLUSH PRIVILEGES;*

*mysql> exit;*

Download Source code & Initialize Database.

- *git clone -b main https://github.com/hkhcoder/vprofile-project.git![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.012.png)*
- *cd vprofile-project*
- *mysql -u root -padmin123 accounts < src/main/resources/db\_backup.sql*
- *mysql -u root -padmin123 accounts*

*mysql> show tables;![ref3]*

Restart mariadb-server

- *systemctl restart mariadb![ref3]*

Starting the firewall and allowing the mariadb to access from port no. 3306

- systemctl start firewalld![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.013.png)
- systemctl enable firewalld
- firewall-cmd --get-active-zones
- firewall-cmd --zone=public --add-port=3306/tcp --permanent
- firewall-cmd --reload
- systemctl restart mariadb

**2.MEMCACHE SETUP**

Install, start & enable memcache on port 11211

- *sudo dnf install epel-release -y![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.014.png)*
- *sudo dnf install memcached -y*
- *sudo systemctl start memcached*
- *sudo systemctl enable memcached*
- *sudo systemctl status memcached*
- *sed -i 's/127.0.0.1/0.0.0.0/g' /etc/sysconfig/memcached*
- *sudo systemctl restart memcached*

Starting the firewall and allowing the port 11211 to access memcache

- *firewall-cmd --add-port=11211/tcp![ref4]*
- *firewall-cmd --runtime-to-permanent*
- *firewall-cmd --add-port=11111/udp*
- *firewall-cmd --runtime-to-permanent*
- *sudo memcached -p 11211 -U 11111 -u memcached -d*

**3.RABBITMQ SETUP**

Login to the RabbitMQ vm

*$ vagrant ssh rmq01![ref3]*

Verify Hosts entry, if entries missing update the it with IP and hostnames

- *cat /etc/hosts![ref3]*

Update OS with latest patches

- *yum update -y![ref3]*

Set EPEL Repository

- *yum install epel-release -y![ref3]*

Install Dependencies

- *sudo yum install wget -y![ref4]*
- *cd /tmp/*
- *dnf -y install centos-release-rabbitmq-38*
- *dnf --enablerepo=centos-rabbitmq-38 -y install rabbitmq-server*
- *systemctl enable --now rabbitmq-server*

Setup access to user test and make it admin

- *sudo sh -c 'echo "[{rabbit, [{loopback\_users, []}]}]." > /etc/rabbitmq/rabbitmq.config'![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.016.png)*
- *sudo rabbitmqctl add\_user test test*
- *sudo rabbitmqctl set\_user\_tags test administrator*
- *sudo systemctl restart rabbitmq-server*

Starting the firewall and allowing the port 5672 to access rabbitmq

- *firewall-cmd --add-port=5672/tcp![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.017.png)*
- *firewall-cmd --runtime-to-permanent*
- *sudo systemctl start rabbitmq-server*
- *sudo systemctl enable rabbitmq-server*
- *sudo systemctl status rabbitmq-server*

**4.TOMCAT SETUP**

Login to the tomcat vm *$ vagrant ssh app01![ref1]*

Verify Hosts entry, if entries missing update the it with IP and hostnames

- *cat /etc/hosts![ref1]*

Update OS with latest patches

- *yum update -y![ref1]*

Set Repository

- *yum install epel-release -y![ref1]*

Install Dependencies

- dnf -y install java-11-openjdk java-11-openjdk-devel![ref3]
- dnf install git maven wget -y![ref1]

Change dir to /tmp

- *cd /tmp/![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.018.png)*

Download & Tomcat Package

- *wget https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.75/bin/apache-tomcat-9.0.75.tar.gz![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.019.png)*
  - *tar xzvf apache-tomcat-9.0.75.tar.gz![ref3]*

Add tomcat user

- *useradd --home-dir /usr/local/tomcat --shell /sbin/nologin tomcat![ref3]*

Copy data to tomcat home dir

- *cp -r /tmp/apache-tomcat-9.0.75/\* /usr/local/tomcat/![ref1]*

Make tomcat user owner of tomcat home dir

- *chown -R tomcat.tomcat /usr/local/tomcat![ref1]*

Setup systemctl command for tomcat

Create tomcat service file

- *vi /etc/systemd/system/tomcat.service![ref3]*

Update the file with below content

[Unit] ![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.020.png)Description=Tomcat After=network.target

[Service]

User=tomcat

WorkingDirectory=/usr/local/tomcat Environment=JRE\_HOME=/usr/lib/jvm/jre Environment=JAVA\_HOME=/usr/lib/jvm/jre Environment=CATALINA\_HOME=/usr/local/tomcat Environment=CATALINE\_BASE=/usr/local/tomcat ExecStart=/usr/local/tomcat/bin/catalina.sh run ExecStop=/usr/local/tomcat/bin/shutdown.sh SyslogIdentifier=tomcat-%i

[Install] WantedBy=multi-user.target

Reload systemd files

- *systemctl daemon-reload![ref1]*

Start & Enable service

- *systemctl start tomcat![ref2]*
- *systemctl enable tomcat*

Enabling the firewall and allowing port 8080 to access the tomcat

- *systemctl start firewalld![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.021.png)*
- *systemctl enable firewalld*
- *firewall-cmd --get-active-zones*
- *firewall-cmd --zone=public --add-port=8080/tcp --permanent*
- *firewall-cmd --reload*

**CODE BUILD & DEPLOY (app01)**

Download Source code

- *git clone -b main https://github.com/hkhcoder/vprofile-project.git![ref3]*

Update configuration

- cd vprofile-project![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.022.png)
- vim src/main/resources/application.properties
- Update file with backend server details

**Build code**

*Run below command inside the repository (vprofile-project)*

- *mvn install![ref1]*

Deploy artifact

- *systemctl stop tomcat![ref1]*
- *rm -rf /usr/local/tomcat/webapps/ROOT\*![ref4]*
- *cp target/vprofile-v2.war /usr/local/tomcat/webapps/ROOT.war*
- *systemctl start tomcat*
- *chown tomcat.tomcat usr/local/tomcat/webapps -R*
- *systemctl restart tomcat*

**5.NGINX SETUP**

Login to the Nginx vm

*$ vagrant ssh web01 ![ref5]$ sudo -i*

Verify Hosts entry, if entries missing update the it with IP and hostnames

- *cat /etc/hosts![ref3]*

Update OS with latest patches

- *apt update![ref5]*
- *apt upgrade*

Install nginx

- *apt install nginx -y![ref3]*

Create Nginx conf file

- vi /etc/nginx/sites-available/vproapp![ref3]

Update with below content

*upstream vproapp {![](Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.024.png)*

*server app01:8080;*

*}*

*server {*

*listen 80;*

*location / {*

*proxy\_pass http://vproapp; }*

*}*

Remove default nginx conf

- *rm -rf /etc/nginx/sites-enabled/default![ref1]*

Create link to activate website

- *ln -s /etc/nginx/sites-available/vproapp /etc/nginx/sites-enabled/vproapp![ref1]*

Restart Nginx

- *systemctl restart nginx![ref1]*

[ref1]: Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.007.png
[ref2]: Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.008.png
[ref3]: Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.009.png
[ref4]: Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.015.png
[ref5]: Aspose.Words.89fd16cf-8d2b-4d70-9072-7a7c09d14b6e.023.png
