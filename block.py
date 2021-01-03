from time import time


# Block
class Block():

    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        """
        :param index: index du bloc dans la blockchain
        :param previous_hash: hash du bloc précédent
        :param timestamp: date de création du bloc
        :param transactions: liste des transactions du bloc
        :param proof: nombre proof généré lors du minage

        """
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof


