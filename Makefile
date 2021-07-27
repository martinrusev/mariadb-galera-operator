deploy:
	charmcraft pack
	juju deploy ./mariadb-galera.charm --resource galera-image=


remove:
	juju remove-application galera --force


juju_reset:
	juju destroy-controller galera --destroy-all-models --destroy-storage

juju_setup:
	juju bootstrap microk8s galera
