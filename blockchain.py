# Imports
from functools import reduce
import hashlib as hl

import json
import requests

from block import Block
from transaction import Transaction
from wallet import Wallet

# recompense pour le mineur
MINING_REWARD = 10

# nombre de 0 au début pour que le bloc soit valide
MINING_DIFFICULTY = '00'
MINING_DIFFICULTY_LENGTH = 2



class Blockchain:
    def __init__(self, public_key):
        # Chaine de bloc
        # Bloc de genèse (premier bloc de la chaine)
        self.blockchain = [Block(0, '', [], 100, 0)]
        # Transactions en cours (non validées)
        self.current_transactions = []

        # On stocke la clé publique du noeud pour faciliter le fonctionnement
        self.public_key = public_key

        # On utilise un set car il n'ajoute pas les nodes déjà présents dans la liste via sa méthode add()
        self.nodes = set()


    # Retourne les transactions en cours (non validées)
    def get_transactions(self):
        return self.current_transactions[:]

    # Ajoute un noeud au réseau
    def add_node(self, node):
        self.nodes.add(node)

    # Liste tous les noeuds du réseau
    def get_nodes(self):
        return list(self.nodes)

    # change la clé publique de l'utilisateur courant
    def set_public_key(self, key):
        self.public_key = key




    def hash_block(self, block):
        """
        Retourne le hash du bloc passé en paramètre

        :param block: <Block> Block à hasher
        :return <string>: Hash du bloc

        """
        hashable_block = block.__dict__.copy()

        # rend les transactions hashable
        hashable_block['transactions'] = [
            transaction.to_ordered_dict() for transaction in hashable_block['transactions']
            ]

        # Hashage du bloc (en JSON) en SHA256 (hashlib)
        json_hashable_block = json.dumps(hashable_block, sort_keys=True).encode()
        result = hl.sha256(json_hashable_block).hexdigest()
        return result


    def valid_proof(self, transactions, last_hash, proof):
        """
        Check si le proof number est valide (MINING_DIFFICULTY=nombre de zeros)

        :param transactions: Les transactions du bloc en cours de validation
        :param last_hash: Le hash du bloc précédent
        :param proof: Le POW à tester (actuel)
        :return <boolean>: Vrai si il est valide, Faux sinon.

        """
        # Créer le string à hasher (transactions + last hash + proof)
        test = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()

        #Hash le string (SHA256)
        test_hash = hl.sha256(test).hexdigest()

        #[0:MINING_DIFFICULTY_LENGTH] = les X premiers caractères du hash
        if test_hash[0:MINING_DIFFICULTY_LENGTH] == MINING_DIFFICULTY:
            return True
        else:
            return False


    def proof_of_work(self):
        """
        Genere un POW avec les transactions en cours, le hash du bloc précédent et un nombre aléatoire (proof)

        """
        last_block = self.blockchain[-1]
        last_hash = self.hash_block(last_block)
        proof = 0

        # Cherche le proof number en incrémentant de un à chaque test
        while not self.valid_proof(self.current_transactions, last_hash, proof):
            proof += 1
        return proof



    def get_balance(self, account=None):
        """
        Calcul le solde de l'utilisateur courant (via sa clé publique)

        """
        if account == None :
            user = self.public_key
        else:
            user = account

        solde_sent = 0
        solde_receive = 0

        # Dans chaque bloc de la blockchain, on regarde chaque transaction
        # Si le user est receiver/sender sur la transaction, on incrémente les variables solde_sent (argent envoyé) et solde_receive (argent reçu)
        for block in self.blockchain:
            for transaction in block.transactions:
                if transaction.sender == user:
                    solde_sent += transaction.amount
                if transaction.receiver == user:
                    solde_receive += transaction.amount

        # Même chose pour les transactions en cours
        # Note : On ne vérifie pas l'argent reçu dans les transactions qui ne sont pas encore validées
        for transac in self.current_transactions:
            if transac.sender == user:
                solde_sent += transac.amount

        # Retourne la différence entre argent reçu et argent envoyé (solde)
        return solde_receive - solde_sent



    def check_block(self, block):
        """
        Check si le bloc passée en paramètre est valide

        :param block: <Block>
        :return <boolean>: Vrai si valide, Faux sinon
        """
        if block.index != 0:
            if block.previous_hash != self.hash_block(blockchain[block.index - 1]):
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True


    def check_chain(self, blockchain):
        """
        Check si la blockchain passée en paramètre est valide

        :param blockchain: <Blockchain>
        :return <boolean>: Vrai si valide, Faux sinon
        """
        for block in enumerate(blockchain):
            if not check_block(block):
                return False
        return True


    def check_transaction(self, transaction, get_balance):
        """
        Check si l'envoyeur a assez pour effectuer de fond la transaction

        :param transaction: Transaction à vérifier
        :return <boolean>: Vrai si valide, Faux sinon
        """
        sender_balance = get_balance(transaction.sender)
        return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)


    def create_transaction(self, receiver, sender, signature, amount):
        """
        Ajoute une transaction aux transactions courante (non validés)
        Si valide, envoie cette transaction à tous les noeuds connus

        :return <boolean>: Vrai si la transaction est ajoutée, Faux sinon
        """

        transaction = Transaction(sender, receiver, signature, amount)
        check_transac = self.check_transaction(transaction, self.get_balance)
        if check_transac:
            self.current_transactions.append(transaction)

            # envoit la transaction à tout les noeuds connus
            for node in self.nodes:
                url = 'http://{}/store-received-transaction'.format(node)
                data = {'sender': sender, 'receiver': receiver, 'amount': amount, 'signature': signature}
                try:
                    response = requests.post(url, json=data)
                    if response.status_code != 201:
                        print("transaction error to {}".format(node) )
                        return False
                except:
                    print("Error Transaction add, -transaction")
                    continue
            return True
        else:
            return False

    def add_transaction(self, receiver, sender, signature, amount):
        """
        Stocke la transaction recu par les autres noeuds dans les transactions en cours (non validées)
        """
        transaction = Transaction(sender, receiver, signature, amount)
        check_transac = self.check_transaction(transaction, self.get_balance)
        if check_transac:
            self.current_transactions.append(transaction)
            return True
        return False




    def add_block(self, block):
        """
        Ajoute un bloc à la blockchain (pour les noeuds qui recoivent le block):
            - Verifie le bloc
            - Verifie les transactions courante de ce bloc
            - Supprime les transactions courante de la blockchaine courante

        :return <boolean>: Vrai si le bloc a été ajoutée, Faux sinon

        """
        transactions = []

        # Place toutes les transactions courantes (non validées) dans un tableau temporaire
        for transaction in block['transactions']:
            t = Transaction(transaction['sender'], transaction['receiver'], transaction['signature'], transaction['amount'])
            transactions.append(t)

        # Check si le proof du bloc est valide
        proof_valid = self.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        # Check si le previous hash du bloc courant est égal au hash du bloc précedent
        check_block = self.hash_block(self.blockchain[-1]) == block['previous_hash']

        if not proof_valid or not check_block:
            return False

        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.blockchain.append(converted_block)

        # Crée une copie des transactions courantes
        current_transactions = self.current_transactions[:]

        # Supprime les transactions courante si elle sont déjà dans le bloc
        for t in block['transactions']:
            for ct in current_transactions:
                if ct.sender == t['sender'] and ct.receiver == t['receiver'] and ct.signature == t['signature']:
                    try:
                        self.current_transactions.remove(ct)
                    except:
                        print('Error remove current transaction')
        return True


    # Mine a new block in the Blockchain ( Create a new block and add open transactions to it )
    def mine_block(self):
        """
        Mine le block courant:
            - Cherche PoW
            - Ajoute le bloc à la blockchain
            - Si trouvé, gagne reward
            - Envoi le bloc à tous les noeuds connus
            - Supprime les transactions courante de la blockchaine courante
        :return <Block>: retourne le block si miné / None si erreur
        """
        if self.public_key == None:
            print("Wallet not initialized, GET /wallet")
            return None

        # Le mineur hash le dernier block et cherche le proof number
        hashed_block = self.hash_block(self.blockchain[-1])
        proof = self.proof_of_work()


        # On vérifie si chaque transaction est valide
        current_transactions = self.current_transactions[:]
        for tx in current_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        # Création de la transaction récompense pour le mineur
        reward_transaction = Transaction('Mining reward', self.public_key, '', MINING_REWARD)
        current_transactions.append(reward_transaction)

        block = Block(len(self.blockchain), hashed_block,
                      current_transactions, proof)
        self.blockchain.append(block)
        self.current_transactions = []

        # Envoi le bloc à tout les noeuds connus
        for node in self.nodes:
            url = 'http://{}/store-received-block'.format(node)
            converted_block = block.__dict__.copy()
            # Converti les transactions en dict (JSON)
            converted_block['transactions'] = [transaction.__dict__ for transaction in converted_block['transactions']]
            data = {'block': converted_block}
            print(converted_block)
            try:
                response = requests.post(url, json=data)
                if response.status_code == 201:
                    print("bloc sent to {}".format(node))
            except :
                print("Error Mine block, store-received-block")
                continue

        return block
