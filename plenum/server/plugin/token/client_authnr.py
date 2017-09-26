from copy import deepcopy

from base58 import b58decode

from common.serializers.serialization import serialize_msg_for_signing
from plenum.common.constants import TXN_TYPE
from plenum.common.types import PLUGIN_TYPE_AUTHENTICATOR, OPERATION
from plenum.common.verifier import Verifier, DidVerifier
from plenum.server.client_authn import CoreAuthNr
from plenum.server.plugin.token import AcceptableWriteTypes, AcceptableQueryTypes
from plenum.server.plugin.token.constants import MINT_PUBLIC, XFER, INPUTS
from stp_core.crypto.nacl_wrappers import Verifier as NaclVerifier


class AddressSigVerifier(Verifier):
    def __init__(self, verkey, **kwargs):
        self.verkey = verkey
        self._vr = NaclVerifier(b58decode(verkey))

    def verify(self, sig, msg) -> bool:
        return self._vr.verify(sig, msg)


class TokenAuthNr(CoreAuthNr):
    pluginType = PLUGIN_TYPE_AUTHENTICATOR

    write_types = AcceptableWriteTypes
    query_types = AcceptableQueryTypes

    def authenticate(self, req_data, identifier: str = None,
                     signature: str = None, verifier=None):
        if req_data[OPERATION][TXN_TYPE] == MINT_PUBLIC:
            verifier = verifier or DidVerifier
            return super().authenticate(req_data, identifier, signature,
                                        verifier=verifier)
        if req_data[OPERATION][TXN_TYPE] == XFER:
            verifier = verifier or AddressSigVerifier
            return super().authenticate(req_data, verifier=verifier)

    def serializeForSig(self, msg, identifier=None, topLevelKeysToIgnore=None):
        if msg[OPERATION][TXN_TYPE] == MINT_PUBLIC:
            return super().serializeForSig(msg, identifier=identifier,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)
        if msg[OPERATION][TXN_TYPE] == XFER:
            # return serialize_msg_for_signing(
            #     msg, topLevelKeysToIgnore=topLevelKeysToIgnore)
            return super().serializeForSig(msg, identifier=identifier,
                                           topLevelKeysToIgnore=topLevelKeysToIgnore)

    def getVerkey(self, identifier):
        if len(identifier) in (43, 44):
            # Address is the 32 byte verkey
            return identifier
        return super().getVerkey(identifier)

    @staticmethod
    def _get_xfer_ser_data(req_data):
        new_data = deepcopy(req_data)
        del new_data[OPERATION][INPUTS]
        return new_data
