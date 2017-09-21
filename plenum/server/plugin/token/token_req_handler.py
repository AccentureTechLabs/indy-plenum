from typing import Tuple, List

import base58

from ledger.util import F
from plenum.common.constants import TXN_TYPE, TRUSTEE
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.messages.fields import IterableField
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn
from plenum.persistence.util import txnsWithSeqNo
from plenum.server.domain_req_handler import DomainRequestHandler
from plenum.server.plugin.token.constants import XFER, MINT_PUBLIC, OUTPUTS
from plenum.server.plugin.token.messages.fields import PublicOutputField
from plenum.server.plugin.token.types import Output
from plenum.server.plugin.token.utxo_cache import UTXOCache
from plenum.server.req_handler import RequestHandler


class TokenReqHandler(RequestHandler):
    valid_txn_types = {MINT_PUBLIC, XFER}
    _public_output_validator = IterableField(PublicOutputField())
    MinSendersForPublicMint = 4

    def __init__(self, ledger, state,
                 utxo_cache: UTXOCache,
                 domain_state):
        super().__init__(ledger, state)
        self.utxo_cache = utxo_cache
        self.domain_state = domain_state

    def validate_output(self, outputs: List[Tuple]):
        return self._public_output_validator.validate(outputs)

    def doStaticValidation(self, request: Request):
        operation = request.operation
        if operation[TXN_TYPE] == MINT_PUBLIC:
            if OUTPUTS not in operation:
                raise InvalidClientRequest(request.identifier, request.reqId,
                                           "{} needs to be present".
                                           format(OUTPUTS))
            error = self.validate_output(operation[OUTPUTS])
            if error:
                raise InvalidClientRequest(request.identifier, request.reqId,
                                           error)

    def validate(self, req: Request):
        operation = req.operation
        error = ''
        if operation[TXN_TYPE] == MINT_PUBLIC:
            senders = req.all_identifiers
            if not all(DomainRequestHandler.get_role(
                    self.domain_state, idr, TRUSTEE) for idr in senders):
                error = 'only Trustees can send this transaction'
            if len(senders) < self.MinSendersForPublicMint:
                error = 'Need at least {} but only {} found'.\
                    format(self.MinSendersForPublicMint, len(senders))
        if error:
            raise UnauthorizedClientRequest(req.identifier, req.reqId,
                                            error)

    def apply(self, req: Request, cons_time: int):
        txn = reqToTxn(req, cons_time)
        (start, end), _ = self.ledger.appendTxns(
            [self.transform_txn_for_ledger(txn)])
        self.updateState(txnsWithSeqNo(start, end, [txn]))
        return txn

    @staticmethod
    def transform_txn_for_ledger(txn):
        """
        Some transactions need to be updated before they can be stored in the
        ledger
        """
        return txn

    def updateState(self, txns, isCommitted=False):
        for txn in txns:
            self._update_state_with_single_txn(txn, is_committed=isCommitted)

    def _update_state_with_single_txn(self, txn, is_committed=False):
        if txn[TXN_TYPE] == MINT_PUBLIC:
            for addr, amount in txn[OUTPUTS]:
                self._add_new_output(Output(addr, txn[F.seqNo.name], amount),
                                     is_committed=is_committed)

    def _add_new_output(self, output: Output, is_committed=False):
        self.utxo_cache.add_output(output, is_committed=is_committed)
        address, seq_no, amount = output
        state_key = self.create_state_key(address, seq_no)
        self.state.set(state_key, str(amount).encode())

    def onBatchCreated(self, state_root):
        self.utxo_cache.create_batch_from_current(state_root)

    def onBatchRejected(self):
        self.utxo_cache.reject_batch()

    def commit(self, txnCount, stateRoot, txnRoot) -> List:
        r = super().commit(txnCount, stateRoot, txnRoot)
        stateRoot = base58.b58decode(stateRoot.encode())
        assert self.utxo_cache.first_batch_idr == stateRoot
        self.utxo_cache.commit_batch()
        return r

    @staticmethod
    def create_state_key(address: str, seq_no: int) -> bytes:
        return ':'.join([address, str(seq_no)]).encode()
