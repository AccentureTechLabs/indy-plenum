from plenum.server.plugin.token.constants import XFER, MINT_PUBLIC
from plenum.server.req_handler import RequestHandler


class TokenReqHandler(RequestHandler):
    valid_txn_types = {MINT_PUBLIC, XFER}

    def __init__(self, ledger, state):
        super().__init__(ledger, state)
