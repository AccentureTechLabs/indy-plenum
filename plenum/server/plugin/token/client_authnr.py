from plenum.common.constants import TXN_TYPE
from plenum.common.types import PLUGIN_TYPE_AUTHENTICATOR, OPERATION
from plenum.server.client_authn import CoreAuthNr
from plenum.server.plugin.token import AcceptableTxnTypes
from plenum.server.plugin.token.constants import MINT_PUBLIC, XFER


class TokenAuthNr(CoreAuthNr):
    pluginType = PLUGIN_TYPE_AUTHENTICATOR

    acceptable_txn_types = AcceptableTxnTypes
    query_types = set()

    def authenticate(self, req_data, identifier: str = None,
                     signature: str = None):
        if req_data[OPERATION][TXN_TYPE] == MINT_PUBLIC:
            return super().authenticate(req_data, identifier, signature)
