from plenum.client.wallet import Wallet
from plenum.common.did_method import DidMethods
from plenum.common.signer_simple import SimpleSigner


class Address:
    def __init__(self, seed=None):
        self.signer = SimpleSigner(seed=seed)
        self.address = self.signer.verkey
        self.outputs = [set(), set()]  # Unspent and Spent

    def spent(self, seq_no):
        self.outputs[0].remove(seq_no)
        self.outputs[1].add(seq_no)


class TokenWallet(Wallet):
    def __init__(self,
                 name: str=None,
                 supportedDidMethods: DidMethods=None):
        super().__init__(name, supportedDidMethods)
        self.addresses = []

    def add_new_address(self, address: Address=None, seed=None):
        assert address or seed
        if not address:
            address = Address(seed=seed)
        self.addresses.append(address)
