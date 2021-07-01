# mariadb-galera-operator

## Description

This is the MariaDB Galera charm for Kubernetes using the Python Operator Framework.

## Usage


### Deploying

```
$ git clone https://github.com/martinrusev/mariadb-galera-operator
$ cd mariadb-galera-operator

$ sudo snap install charmcraft --beta
$ charmcraft build
Created 'mariadb-galera.charm'.


$ juju deploy ./mariadb-galera.charm --resource kafka-image=bitnami/mariadb-galera:latest
```

## Developing

Create and activate a virtualenv with the development requirements:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements-dev.txt
```


## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

```
./run_tests
```
