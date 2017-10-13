from common.serializers.json_serializer import JsonSerializer
from plenum.common.constants import TXN_TYPE, TRUSTEE
from plenum.common.exceptions import UnauthorizedClientRequest, \
    InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn
from plenum.common.types import f
from plenum.persistence.util import txnsWithSeqNo
from plenum.server.domain_req_handler import DomainRequestHandler
from plenum.server.plugin.fees.constants import FEE, GET_FEES, FEES
from plenum.server.plugin.fees.fee_req_handler import FeeReqHandler
from plenum.server.plugin.fees.messages.fields import FeesStructureField


class StaticFeesReqHandler(FeeReqHandler):
    valid_txn_types = {FEE, GET_FEES}
    query_types = {GET_FEES, }
    _fees_validator = FeesStructureField()
    MinSendersForFees = 4
    fees_state_key = b'fees'
    state_serializer = JsonSerializer()

    def __init__(self, ledger, state, utxo_cache, domain_state):
        super().__init__(ledger, state)
        self.utxo_cache = utxo_cache
        self.domain_state = domain_state

        # In-memory map of fees, changes on FEE txns
        self.fees = self._get_fees(is_committed=True)

        self.query_handlers = {
            GET_FEES: self.get_fees,
        }

    def can_pay_fees(self, request) -> bool:
        # TODO:
        print(1)

    def deduct_fees(self, request) -> bool:
        # TODO:
        print(2)

    def doStaticValidation(self, request: Request):
        operation = request.operation
        if operation[TXN_TYPE] in (FEE, GET_FEES):
            error = ''
            if operation[TXN_TYPE] == FEE:
                error = self._fees_validator.validate(operation.get(FEES))
            if error:
                raise InvalidClientRequest(request.identifier, request.reqId,
                                           error)
        else:
            super().doStaticValidation(request)

    def validate(self, req: Request):
        operation = req.operation
        if operation[TXN_TYPE] == FEE:
            error = ''
            senders = req.all_identifiers
            if not all(DomainRequestHandler.get_role(
                    self.domain_state, idr, TRUSTEE) for idr in senders):
                error = 'only Trustees can send this transaction'
            if error:
                raise UnauthorizedClientRequest(req.identifier, req.reqId,
                                                error)
        else:
            super().validate(req)

    def apply(self, req: Request, cons_time: int):
        operation = req.operation
        if operation[TXN_TYPE] == FEE:
            txn = reqToTxn(req, cons_time)
            (start, end), _ = self.ledger.appendTxns(
                [self.transform_txn_for_ledger(txn)])
            self.updateState(txnsWithSeqNo(start, end, [txn]))
            return txn
        else:
            super().apply(req, cons_time)

    def get_query_response(self, request: Request):
        return self.query_handlers[request.operation[TXN_TYPE]](request)

    def updateState(self, txns, isCommitted=False):
        for txn in txns:
            self._update_state_with_single_txn(txn, is_committed=isCommitted)

    def _update_state_with_single_txn(self, txn, is_committed=False):
        if txn[TXN_TYPE] == FEE:
            existing_fees = self._get_fees(is_committed=is_committed)
            existing_fees.update(txn[FEES])
            val = self.state_serializer.serialize(existing_fees)
            self.state.set(self.fees_state_key, val)
            self.fees = existing_fees

    def get_fees(self, request: Request):
        fees = self._get_fees(is_committed=True)
        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId, FEES: fees}
        result.update(request.operation)
        return result

    def _get_fees(self, is_committed=False):
        fees = {}
        try:
            serz = self.state.get(self.fees_state_key,
                                  isCommitted=is_committed)
            if serz:
                fees = self.state_serializer.deserialize(serz)
        except KeyError:
            pass
        return fees
