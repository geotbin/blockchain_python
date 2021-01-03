from collections import OrderedDict

# Transaction
class Transaction():
    def __init__(self, s, r, sign, am):
        self.sender = s
        self.receiver = r
        self.signature = sign
        self.amount = am

    # Converti la transaction en un dictonnaire ordonné (hashable)
    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount)])
