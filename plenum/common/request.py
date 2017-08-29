from hashlib import sha256
from typing import Mapping, NamedTuple, Dict

from common.serializers.serialization import serialize_msg_for_signing
from plenum.common.constants import REQDIGEST, REQKEY, FORCE
from plenum.common.messages.client_request import ClientMessageValidator
from plenum.common.types import f, OPERATION
from plenum.common.util import getTimeBasedId
from stp_core.types import Identifier


class Request:
    def __init__(self,
                 identifier: Identifier=None,
                 reqId: int=None,
                 operation: Mapping=None,
                 signature: str=None,
                 signatures: Dict[str, str]=None):
        self._identifier = identifier
        self.signature = signature
        self.signatures = signatures
        self.reqId = reqId
        self.operation = operation
        self.digest = self.getDigest()

    @property
    def as_dict(self):
        return {
            f.IDENTIFIER.nm: self.identifier,
            f.REQ_ID.nm: self.reqId,
            OPERATION: self.operation,
            f.SIG.nm: self.signature,
            f.SIGS.nm: self.signatures
        }

    def __eq__(self, other):
        return self.as_dict == other.as_dict

    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self.as_dict)

    @property
    def key(self):
        return self.identifier, self.reqId

    def getDigest(self):
        return sha256(serialize_msg_for_signing(self.signingState())).hexdigest()

    # @property
    # def reqDigest(self):
    #     return ReqDigest(self.identifier, self.reqId, self.digest)

    def __getstate__(self):
        return self.__dict__

    def signingState(self, identifier=None):
        return {
            f.IDENTIFIER.nm: identifier or self.identifier,
            f.REQ_ID.nm: self.reqId,
            OPERATION: self.operation
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        return self

    @classmethod
    def fromState(cls, state):
        obj = cls.__new__(cls)
        cls.__setstate__(obj, state)
        return obj

    def serialized(self):
        return serialize_msg_for_signing(self.__getstate__())

    def isForced(self):
        force = self.operation.get(FORCE)
        return str(force) == 'True'

    @property
    def identifier(self):
        return self._identifier or ''.join(self._all_identifiers)

    @property
    def _all_identifiers(self):
        return sorted(self.signatures.keys())

    @staticmethod
    def gen_req_id():
        return getTimeBasedId()

    def add_signature(self, identifier, signature):
        if not isinstance(self.signatures, Dict):
            self.signatures = {}
        self.signatures[identifier] = signature

    # def _hashed_idrs(self):
    #     # Only called when request is a multisig
    #     assert self.signatures
    #     return

    def __hash__(self):
        return hash(self.serialized())


# class ReqDigest(NamedTuple(REQDIGEST, [f.IDENTIFIER,
#                                        f.REQ_ID,
#                                        f.DIGEST])):
#     @property
#     def key(self):
#         return self.identifier, self.reqId


class ReqKey(NamedTuple(REQKEY, [f.IDENTIFIER, f.REQ_ID])):
    pass


class SafeRequest(Request, ClientMessageValidator):

    def __init__(self, **kwargs):
        self.validate(kwargs)
        super().__init__(**kwargs)
