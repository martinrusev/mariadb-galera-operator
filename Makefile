deploy:
	charmcraft pack
	juju deploy ./mariadb-galera-operator_ubuntu-20.04-amd64.charm --resource galera-image=localhost:32000/mariadb-galera:latest


remove:
	juju remove-application galera --force


juju_reset:
	juju destroy-controller galera --destroy-all-models --destroy-storage

juju_setup:
	juju bootstrap microk8s galera
