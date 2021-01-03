from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

# Portefeuille (Classe Wallet)
class Wallet:

    def __init__(self):
        self.private_key = None
        self.public_key = None


    def hasKeys(self):
        return self.private_key != None


    def generate_keys(self):
        """
        Genere la paire de clés (privée/public)

        """
        privateK = RSA.generate(1024, Crypto.Random.new().read)
        publicK = privateK.publickey()
        return (binascii.hexlify(privateK.exportKey(format='DER')).decode('ascii'), binascii.hexlify(publicK.exportKey(format='DER')).decode('ascii'))


    def create_keys(self):
        """
        Stocke la clé publique/privée généré dans l'instance courante

        """
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

   

    def sign_transaction(self, sender, receiver, amount):
        """
        Créé la signature de la transaction
        Utilise l'envoyeur, le receveur et le montant pour créer un SHA256
        Signer ensuite par la clé privée


        """
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(receiver) + str(amount)).encode('utf8'))
        signature = signer.sign(h)

        #converti binaire en hexadecimal
        return binascii.hexlify(signature).decode('ascii')


    def verify_transaction(transaction):
        """
        Verification de la transaction
        Hash des informations de la transaction afin d'obtenir la signature et
        comparaison de la signature avec celle créée. 

        :param <Transaction>: transaction à vérifier
        :return <boolean>: Vrai si la transaction est verifié, Faux sinon
        """

        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.receiver) + str(transaction.amount)).encode('utf8'))

        return verifier.verify(h, binascii.unhexlify(transaction.signature))
