#inicializa servidor mongodb
## mongod --dbpath data/db/ --replSet=bigchain-rs
#inicializa servidor bigchaindb
## bigchaindb start
#https://www.bigchaindb.com/whitepaper/bigchaindb-whitepaper.pdf

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from time import sleep
from sys import exit

alice, bob = generate_keypair(), generate_keypair()

bdb_root_url = 'localhost:9984'  # Use YOUR BigchainDB Root URL here

bdb = BigchainDB(bdb_root_url)

bicycle_asset = {
    'data': {
        'bicycle': {
            'serial_number': 'abcd1234',
            'manufacturer': 'bkfab'
        },
    },
}

bicycle_asset_metadata = {
    'planet': 'earth'
}

prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset=bicycle_asset,
    metadata=bicycle_asset_metadata
)

fulfilled_creation_tx = bdb.transactions.fulfill(
    prepared_creation_tx,
    private_keys=alice.private_key
)

sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)

txid = fulfilled_creation_tx['id']

trials = 0
while trials < 60:
    try:
        if bdb.transactions.status(txid).get('status') == 'valid':
            print('Tx valid in:', trials, 'secs')
            break
    except bigchaindb_driver.exceptions.NotFoundError:
        trials += 1
        sleep(1)

if trials == 60:
    print('Tx is still being processed... Bye!')
    exit(0)

asset_id = txid

transfer_asset = {
    'id': asset_id
}

output_index = 0
output = fulfilled_creation_tx['outputs'][output_index]

transfer_input = {
    'fulfillment': output['condition']['details'],
    'fulfills': {
        'output_index': output_index,
        'transaction_id': fulfilled_creation_tx['id']
    },
    'owners_before': output['public_keys']
}

prepared_transfer_tx = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=bob.public_key,
)

fulfilled_transfer_tx = bdb.transactions.fulfill(
    prepared_transfer_tx,
    private_keys=alice.private_key,
)

sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)

print("Is Bob the owner?",
    sent_transfer_tx['outputs'][0]['public_keys'][0] == bob.public_key)


'''
{
    'inputs': [{'owners_before': ['JBtuNm2qdxKYwzGHVbgMCmvMASQeYxjj5RLggvp4KpP8'], 
    'fulfills': None, 
    'fulfillment':'pGSAIP9hLDqwOuelnV1GnfsHKZaZ5rA4A7owmVVoMn7eqX6_gUBYVuHEdlzyHPG9VdfqnsXlBtQT6nD4QglkTLr-D-oawQ46h4GDrs5G9vy2SdzwTJNsjrDDvBj6hnMN4X1t6lsK'}], 
    'outputs': [{
        'public_keys': ['JBtuNm2qdxKYwzGHVbgMCmvMASQeYxjj5RLggvp4KpP8'], 
        'condition': {
            'details': {
                'type': 'ed25519-sha-256', 'public_key': 'JBtuNm2qdxKYwzGHVbgMCmvMASQeYxjj5RLggvp4KpP8'
            }, 
            'uri': 'ni:///sha-256;BwsZGU0kDAUnsZQ7znPjMq22QDbBjNEDq-6LgZFq6-U?fpt=ed25519-sha-256&cost=131072'
        }, 
        'amount': '1'
    }], 
    'operation': 'CREATE', 
    'metadata': {'planet': 'earth'}, 
    'asset': {
        'data': {
            'bicycle': {'serial_number': 'abcd1234', 'manufacturer': 'bkfab'}
            }}, 
        'version': '1.0', 
        'id': '8b1983bbfacce39a43fc11e088b896be5d6bb40834eab65976ad6b9787d0e3eb'
}
'''
