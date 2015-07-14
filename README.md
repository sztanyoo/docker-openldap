# osixia/openldap

A docker image to run OpenLDAP.
> [www.openldap.org](http://www.openldap.org/)

Fork of Nick Stenning docker-slapd :
https://github.com/nickstenning/docker-slapd

Add support of TLS and multi master replication.

## Quick start
Run OpenLDAP docker image :

	docker run -h ldap.example.org -d osixia/openldap

This start a new container with a OpenLDAP server running inside.
The odd string printed by this command is the `CONTAINER_ID`.
We are going to use this `CONTAINER_ID` to execute some commands inside the container.

Then run a terminal on this container,
make sure to replace `CONTAINER_ID` by your container id :

	docker exec -it CONTAINER_ID bash

You should now be in the container terminal,
and we can search on the ldap server :

	ldapsearch -x -h ldap.example.org -b dc=example,dc=org -D "cn=admin,dc=example,dc=org" -w admin

This should output :

	# extended LDIF
	#
	# LDAPv3
	# base <dc=example,dc=org> with scope subtree
	# filter: (objectclass=*)
	# requesting: ALL
	#

	[...]

	# numResponses: 3
	# numEntries: 2

if you have the following error, OpenLDAP is not started yet, wait some time.

		ldap_sasl_bind(SIMPLE): Can't contact LDAP server (-1)


## Examples

### Create new ldap server

This is the default behaviour when you run the image.
It will create an empty ldap for the compagny **Example Inc.** and the domain **example.org**.

By default the admin has the password **admin**. All those default settings can be changed at the docker command line, for example :

	docker run -h ldap.example.org -e LDAP_ORGANISATION="My Compagny" -e LDAP_DOMAIN="my-compagny.com" \
	-e LDAP_ADMIN_PASSWORD="JonSn0w" -d osixia/openldap

#### Data persitance

The directories `/var/lib/ldap` (LDAP database files) and `/etc/ldap/slapd.d`  (LDAP config files) has been declared as volumes, so your ldap files are saved outside the container in data volumes.

Be careful, if you remove the container, data volumes will me removed too, except if you have linked this data volume to an other container.

For more information about docker data volume, please refer to :

> [https://docs.docker.com/userguide/dockervolumes/](https://docs.docker.com/userguide/dockervolumes/)


### Use an existing ldap database

This can be achieved by mounting host directories as volume.
Assuming you have a LDAP database on your docker host in the directory `/data/slapd/database`
and the corresponding LDAP config files on your docker host in the directory `/data/slapd/config`
simply mount this directories as a volume to `/var/lib/ldap` and `/etc/ldap/slapd.d`:

	docker run -h ldap.example.org -v /data/slapd/database:/var/lib/ldap \
	-v /data/slapd/config:/etc/ldap/slapd.d
	-d osixia/openldap

You can also use data volume containers. Please refer to :
> [https://docs.docker.com/userguide/dockervolumes/](https://docs.docker.com/userguide/dockervolumes/)

### Using TLS

#### Use autogenerated certificate
By default TLS is enable, a certificate is created with the container hostname (set by -h option eg: ldap.example.org).

	docker run -h ldap.example.org -e SERVER_NAME=ldap.my-compagny.com -d osixia/openldap

#### Use your own certificate

Add your custom certificate, private key and CA certificate in the directory **image/service/slapd/assets/ssl** adjust filename in **image/env.yml** and rebuild the image ([see manual build](#manual-build)).

Or you can set your custom certificate at run time, by mouting a directory containing thoses files to **/osixia/slapd/assets/ssl** and adjust there name with the following environment variables :

	docker run -h ldap.example.org -v /path/to/certifates:/osixia/slapd/assets/ssl \
	-e SSL_CRT_FILENAME=my-ldap.crt \
	-e SSL_KEY_FILENAME=my-ldap.key \
	-e SSL_CA_CRT_FILENAME=the-ca.crt \
	-d osixia/openldap

#### Disable TLS
Add -e USE_TLS=false to the run command :

	docker run -h ldap.example.org  -e USE_TLS=false -d osixia/openldap

### Multi master replication
Quick example, with the default config.

Create the first ldap server, save the container id in LDAP_CID and get its IP:

	LDAP_CID=$(docker run -h ldap.example.org -e USE_REPLICATION=true -d osixia/openldap)
	LDAP_IP=$(docker inspect -f "{{ .NetworkSettings.IPAddress }}" $LDAP_CID)

Create the second ldap server, save the container id in LDAP2_CID and get its IP:

	LDAP2_CID=$(docker run -h ldap2.example.org -e USE_REPLICATION=true -d osixia/openldap)
	LDAP2_IP=$(docker inspect -f "{{ .NetworkSettings.IPAddress }}" $LDAP2_CID)

Add the pair "ip hostname" to /etc/hosts on each containers,
beacause ldap.example.org and ldap2.example.org are fake hostnames

	docker exec $LDAP_CID /osixia/test/add-host.sh $LDAP2_IP ldap2.example.org
	docker exec $LDAP2_CID /osixia/test/add-host.sh $LDAP_IP ldap.example.org

We reload slapd to let him take into consideration /etc/hosts changes

	docker exec $LDAP_CID pkill slapd
	docker exec $LDAP2_CID pkill slapd

That's it ! But a litle test to be sure :

Add a new user "billy" on the first ldap server

	docker exec $LDAP_CID ldapadd -x -D "cn=admin,dc=example,dc=org" -w admin -f /osixia/test/new-user.ldif -h ldap.example.org -ZZ

Search on the second ldap server, and billy should show up !

	docker exec $LDAP2_CID ldapsearch -x -h ldap2.example.org -b dc=example,dc=org -D "cn=admin,dc=example,dc=org" -w admin -ZZ

	[...]

	# billy, example.org
	dn: uid=billy,dc=example,dc=org
	uid: billy
	cn: billy
	sn: 3
	objectClass: top
	objectClass: posixAccount
	objectClass: inetOrgPerson
	[...]


## Administrate your ldap server
If you are looking for a simple solution to administrate your ldap server you can take a look at our phpLDAPadmin docker image :
> [osixia/phpldapadmin](https://github.com/osixia/docker-phpLDAPadmin)

## Environment Variables

Environement variables defaults are set in **image/env.yml**. You can modify environment variable values directly in this file and rebuild the image ([see manual build](#manual-build)). You can also override those values at run time with -e argument or by setting your own env.yml file as a docker volume to `/etc/env.yml`. See examples below.

General container configuration :
- **LDAP_LOG_LEVEL**: Slap log level. defaults to  `-1`. See table 5.1 in http://www.openldap.org/doc/admin24/slapdconf2.html for the available log levels.

Required and used for new ldap server only :
- **LDAP_ORGANISATION**: Organisation name. Defaults to `Example Inc.`
- **LDAP_DOMAIN**: Ldap domain. Defaults to `example.org`
- **LDAP_ADMIN_PASSWORD** Admin password. Defaults to `admin`

TLS options :
- **USE_TLS**: Add openldap TLS capabilities. Defaults to `true`
- **SSL_CRT_FILENAME**: Ldap ssl certificate filename. Defaults to `ldap.crt`
- **SSL_KEY_FILENAME**: Ldap ssl certificate private key filename. Defaults to `ldap.key`
- **SSL_CA_CRT_FILENAME**: Ldap ssl CA certificate  filename. Defaults to `ca.crt`

Replication options :
- **USE_REPLICATION**: Add openldap replication capabilities. Defaults to `false`
- **REPLICATION_CONFIG_SYNCPROV**: olcSyncRepl options used for the config database. Without **rid** and **provider** which are automaticaly added based on REPLICATION_HOSTS.  Defaults to `binddn="cn=admin,cn=config" bindmethod=simple credentials=$LDAP_CONFIG_PASSWORD searchbase="cn=config" type=refreshAndPersist retry="5 5 300 5" timeout=1 starttls=critical`
- **REPLICATION_HDB_SYNCPROV**: olcSyncRepl options used for the HDB database. Without **rid** and **provider** which are automaticaly added based on REPLICATION_HOSTS.  Defaults to `binddn="cn=admin,$BASE_DN" bindmethod=simple credentials=$LDAP_ADMIN_PASSWORD searchbase="$BASE_DN" type=refreshAndPersist interval=00:00:00:10 retry="5 5 300 5" timeout=1  starttls=critical`
- **REPLICATION_HOSTS**: list of replication hosts, must contains the current container hostname set by -h on docker run command. Defaults to `['ldap://ldap.example.org', 'ldap://ldap2.example.org']`

### Set environment variables at run time :

Environment variable can be set directly by adding the -e argument in the command line, for example :

	docker run -h ldap.example.org -e LDAP_ORGANISATION="My Compagny" -e LDAP_DOMAIN="my-compagny.com" \
	-e LDAP_ADMIN_PASSWORD="JonSn0w" -d osixia/openldap

Or by setting your own `env.yml` file as a docker volume to `/etc/env.yml`

	docker run -h ldap.example.org -v /data/my-ldap-env.yml:/etc/env.yml \
	-d osixia/openldap

## Manual build

Clone this project :

	git clone https://github.com/osixia/docker-openldap
	cd docker-openldap

Adapt Makefile, set your image NAME and VERSION, for example :

	NAME = osixia/openldap
	VERSION = 0.10.0

	becomes :
	NAME = billy-the-king/openldap
	VERSION = 0.1.0

Build your image :

	make build

Run your image :

	docker run -h ldap.example.org -d billy-the-king/openldap:0.1.0

## Tests

We use **Bats** (Bash Automated Testing System) to test this image:

> [https://github.com/sstephenson/bats](https://github.com/sstephenson/bats)

Install Bats, and in this project directory run :

	make test
