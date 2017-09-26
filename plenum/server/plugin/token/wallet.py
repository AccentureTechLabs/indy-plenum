from collections import OrderedDict
from typing import Dict

from plenum.client.wallet import Wallet
from plenum.common.constants import TXN_TYPE
from plenum.common.did_method import DidMethods
from plenum.common.request import Request
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import lxor
from plenum.server.plugin.token.constants import INPUTS, GET_UTXO


class Address:
    def __init__(self, seed=None):
        self.signer = SimpleSigner(seed=seed)
        self.address = self.signer.verkey
        self.outputs = [set(), set()]  # Unspent and Spent

    def is_unspent(self, seq_no):
        return seq_no in self.outputs[0]

    def spent(self, seq_no):
        self.outputs[0].remove(seq_no)
        self.outputs[1].add(seq_no)


class TokenWallet(Wallet):
    def __init__(self,
                 name: str=None,
                 supportedDidMethods: DidMethods=None):
        super().__init__(name, supportedDidMethods)
        self.addresses = OrderedDict()
        self.reply_handlers = {
            GET_UTXO: self.handle_get_utxo_response
        }

    def add_new_address(self, address: Address=None, seed=None):
        assert address or seed
        if not address:
            address = Address(seed=seed)
        assert address.address not in self.addresses
        self.addresses[address.address] = address

    def sign_using_output(self, id, seq_no, op: Dict=None, request: Request=None):
        assert lxor(op, request)
        # assert self.addresses[id].is_unspent(seq_no)
        if op:
            request = Request(reqId=Request.gen_req_id(), operation=op)
        request.operation[INPUTS] = [[id, seq_no], ]
        signature = self.addresses[id].signer.sign(request.signingState(id))
        request.add_signature(id, signature)
        return request

    def on_reply_from_network(self, observer_name, req_id, frm, result,
                              num_replies):
        typ = result.get(TXN_TYPE)
        if typ and typ in self.reply_handlers:
            self.reply_handlers[typ](result)

    def handle_get_utxo_response(self, response):
        pass
