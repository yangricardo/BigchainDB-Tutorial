# BigchainDB-Tutorial

Primeira experiência utilizando o Bigchain como um banco de dados blockchain (numa maquina com ambiente MacOS)

- virtualenv env

- source env/bin/activate

- brew install mongodb

- pip install --upgrade bigchaindb_driver pylint django

- mkdir -p data/db

- mongod --dbpath data/db/ --replSet=bigchain-rs

- bigchaindb start

- python test.py

https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html