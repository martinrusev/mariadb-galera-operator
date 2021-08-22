pre_deploy:
	sudo apt install python3-pip python3-wheel python3-setuptools -y

pack:
	charmcraft pack --destructive-mode

remove:
	juju remove-application mariadb-galera-operator --force

sleep:
	timeout 20

# microk8s enable registry
deploy: remove sleep
	charmcraft pack --destructive-mode
	juju deploy ./mariadb-galera-operator_ubuntu-20.04-amd64.charm --resource galera-image=localhost:32000/mariadb-galera:$(shell docker images mariadb-galera:latest --format '{{.ID}}')



juju_reset:
	juju destroy-controller galera --destroy-all-models --destroy-storage

# microk8s enable dns
juju_setup:
	juju bootstrap microk8s galera
