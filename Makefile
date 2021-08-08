pre_deploy:
	sudo apt install python3-pip python3-wheel python3-setuptools -y

# microk8s enable registry
deploy:
	charmcraft pack --destructive-mode
	juju deploy ./mariadb-galera-operator_ubuntu-20.04-amd64.charm --resource galera-image=localhost:32000/mariadb-galera:latest

d:
	juju deploy ./mariadb-galera-operator_ubuntu-20.04-amd64.charm --resource galera-image=localhost:32000/mariadb-galera:latest

remove:
	juju remove-application mariadb-galera-operator --force


juju_reset:
	juju destroy-controller galera --destroy-all-models --destroy-storage

# microk8s enable dns
juju_setup:
	juju bootstrap microk8s galera
