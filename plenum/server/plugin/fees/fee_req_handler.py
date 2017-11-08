from abc import abstractmethod

import base58

from common.serializers.serialization import serialize_msg_for_signing
from plenum.common.exceptions import InsufficientCorrectSignatures, \
    InvalidSignatureFormat
from plenum.common.types import f
from plenum.server.config_req_handler import ConfigReqHandler
from plenum.server.plugin.fees.constants import FEE, GET_FEES
from plenum.server.plugin.token.client_authnr import AddressSigVerifier


class FeeReqHandler(ConfigReqHandler):
    @abstractmethod
    def can_pay_fees(self, request) -> bool:
        pass

    @abstractmethod
    def deduct_fees(self, request, *args, **kwargs) -> bool:
        pass

    def verify_signature(self, msg):
        try:
            fees = getattr(msg, f.FEES.nm)
        except (AttributeError, KeyError):
            return
        correct_sigs_from = set()
        required_sigs_from = set()
        outputs = fees[1]
        sigs = getattr(msg, f.SIGS.nm, {})
        for addr, seq_no in fees[0]:
            required_sigs_from.add(addr)
            if addr not in sigs:
                break
            try:
                sig = base58.b58decode(sigs[addr].encode())
            except Exception as ex:
                raise InvalidSignatureFormat from ex

            to_ser = [[addr, seq_no], outputs]
            serz = serialize_msg_for_signing(to_ser,
                                             topLevelKeysToIgnore=[
                                                 f.SIG.nm, f.SIGS.nm])
            verifier = AddressSigVerifier(verkey=addr)
            if verifier.verify(sig, serz):
                correct_sigs_from.add(addr)
        if correct_sigs_from != required_sigs_from:
            raise InsufficientCorrectSignatures(len(correct_sigs_from),
                                                len(fees[0]))

    def commit_fee_txns(self, txn, pp_time, state_root, txn_root):
        pass
