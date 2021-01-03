from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from argparse import ArgumentParser

from wallet import Wallet
from blockchain import Blockchain

"""
Flask est un framework de developpement web
Il crée des routes (URI) et permet de dialoguer via des requetes HTTP (GET, POST, DELETE, PUT)

Fonctionnement:
    - Avant la fonction : @app.route('/xxxx', methods=['METHOD'])
    - La fonction doit retourner un string (ou un JSON) ainsi que les codes HTTP

Les codes :
1xx - Information
2xx - Succès
3xx - Redirection
4xx - Erreur du client web
5xx - Erreur du serveur / du serveur d'application
"""



app = Flask(__name__)
CORS(app)




@app.route('/wallet', methods=['GET'])
def get_wallet():
    """
    Affiche le wallet de l'utilisateur courant
        - clé publique
        - clé privé
        - solde (fonction get_balance() dans blockchain.py)

    """
    # Si l'utilisateur n'a pas de wallet, creation d'un wallet
    if not wallet.hasKeys():
        wallet.create_keys()
        global blockchain
        # la blockchain de l'utilisateur détient la clé publique
        # de l'utilisateur pour faciliter les fonctions
        blockchain.set_public_key(wallet.public_key)

    response = {
        'public_key': wallet.public_key,
        'private_key': wallet.private_key,
        'solde': blockchain.get_balance()
    }
    return jsonify(response), 201


@app.route('/nodes', methods=['GET'])
def get_nodes():
    """
    Retourne la liste de noeuds connus
    Methode : get_nodes() dans blockchain.py

    """
    nodes = blockchain.get_nodes()
    response = {
        'nodes': nodes
    }
    return jsonify(response), 200



@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    """
    Retourne une copie actuelle de la blockchain
    """
    blockchain_copy = blockchain.blockchain
    dict_chain = []
    for block in blockchain_copy:
        dict_chain.append(block.__dict__.copy())

    for dict_block in dict_chain:
        dict_block['transactions'] = [transaction.__dict__ for transaction in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/add_node', methods=['POST'])
def add_node():
    """
    Ajoute un noeud au réseau
    Retourne un message (erreur/success) JSON
    """
    values = request.get_json()
    if not values:
        response = {
            'info': 'No data found.'
        }
        return jsonify(response), 400


    node = values['node']
    blockchain.add_node(node)
    response = {
        'info': 'Node added successfully.',
        'node': node
    }
    return jsonify(response), 201



@app.route('/mine', methods=['POST'])
def mine():
    """
    Mine le block courant (fonction mine_block() dans blockchain.py)
    Retourne un message (erreur/success) JSON
    """
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [transaction.__dict__ for transaction in dict_block['transactions']]

        response = {
            'info': 'Block added, miner get reward',
            'block': dict_block,
        }
        return jsonify(response), 201
    else:
        response = {
            'info': 'Add block Error. Wallet may not initialized',
        }
        return jsonify(response), 500


@app.route('/current_transactions', methods=['GET'])
def get_current_transactions():
    """
    Retourne les transactions en cours (non validées)

    """
    transactions = []
    transactions = blockchain.get_transactions()
    print(blockchain.get_transactions())
    dict_transactions = []
    for t in transactions:
        dict_transactions.append(t.__dict__)
    return jsonify(dict_transactions), 200


@app.route('/create_transaction', methods=['POST'])
def transaction():
    """
    Crée une nouvelle transaction via la fonction (create_transaction() de blockchain.py)
    La transaction est implicitement envoyé à tout les noeuds connus (dans la fonction create_transaction() de blockchain.py)
    Retourne un message (succes/error) JSON
    """

    if wallet.public_key == None:
        response = {'info': 'Error: No wallet'}
        return jsonify(response), 400

    request_data = request.get_json()
    if not request_data or ('receiver' not in request_data):
        response = {'info': 'Error: POST data'}
        return jsonify(response), 400

    receiver = request_data['receiver']
    amount = request_data['amount']


    signature = wallet.sign_transaction(wallet.public_key, receiver, amount)
    add_transaction = blockchain.create_transaction(receiver, wallet.public_key, signature, amount)

    if add_transaction:
        response = {
            'info': 'Transaction created',
            'transaction_signature': signature
            }
        return jsonify(response), 201
    else:
        response = {
            'info': 'Error: transaction failed.'
        }
        return jsonify(response), 500




@app.route('/store-received-transaction', methods=['POST'])
def store_received_transaction():
    """
    Stocke la transaction reçu par les autres noeuds dans
    la liste de transactions en cours (non validées)

    """

    request_data = request.get_json()

    if not request_data:
        response = {'info': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'receiver', 'amount', 'signature']
    if not all(key in request_data for key in required):
        response = {'info': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        request_data['receiver'], request_data['sender'], request_data['signature'], request_data['amount'])
    if success:
        response = {
            'info': 'Transaction added.',
            'transaction_signature': request_data['signature']
        }
        return jsonify(response), 201
    else:
        response = {
            'info': 'Error: transaction not added'
        }
        return jsonify(response), 500


@app.route('/store-received-block', methods=['POST'])
def store_received_block():
    """
    Stocke le block reçu par les autres noeuds dans
    la blockchain actuelle

    """
    request_data = request.get_json()

    if not request_data:
        response = {'info': 'No data found.'}
        return jsonify(response), 400

    block = request_data['block']
    if block['index'] == blockchain.blockchain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'info': 'Block added'}
            return jsonify(response), 201
    elif block['index'] > blockchain.blockchain[-1].index:
        pass
    else:
        response = {'info': 'Error, blockchain, block not added'}
        return jsonify(response), 409



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet()
    blockchain = Blockchain(None)
    app.run(host='0.0.0.0', port=port)
