from plenum.common.constants import TXN_TYPE
from plenum.common.types import PLUGIN_TYPE_AUTHENTICATOR, OPERATION
from plenum.common.verifier import DidVerifier
from plenum.server.client_authn import CoreAuthNr
from plenum.server.plugin.fees import AcceptableWriteTypes, AcceptableQueryTypes
from plenum.server.plugin.fees.constants import FEE


class FeesAuthNr(CoreAuthNr):
    pluginType = PLUGIN_TYPE_AUTHENTICATOR

    write_types = AcceptableWriteTypes
    query_types = AcceptableQueryTypes

    def __init__(self, state, token_authnr):
        super().__init__(state)
        self.token_authnr = token_authnr

    def authenticate(self, req_data, identifier: str = None,
                     signature: str = None, verifier=None):
        if req_data[OPERATION][TXN_TYPE] == FEE:
            verifier = verifier or DidVerifier
            return super().authenticate(req_data, identifier, signature,
                                        verifier=verifier)
