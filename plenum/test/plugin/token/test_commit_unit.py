import pytest
from mock import Mock, MagicMock

from ledger.util import F
from plenum.common.constants import TXN_TYPE, DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.ledger import Ledger
from plenum.common.request import Request
from plenum.common.txn_util import reqToTxn
from plenum.common.util import randomString
from plenum.persistence import util
from plenum.persistence.util import txnsWithSeqNo
from plenum.server.plugin.token.constants import XFER_PUBLIC, MINT_PUBLIC, \
    OUTPUTS, INPUTS, GET_UTXO, ADDRESS, TOKEN_LEDGER_ID
from plenum.server.plugin.token.storage import get_token_hash_store, \
    get_token_ledger, get_token_state, get_utxo_cache
from plenum.server.plugin.token.token_req_handler import TokenReqHandler
# TEST CONSTANTS
from plenum.server.plugin.token.types import Output

VALID_ADDR_1 = '6baBEYA94sAphWBA5efEsaA6X2wCdyaH7PXuBtv2H5S1'
VALID_ADDR_2 = '8kjqqnF3m6agp9auU7k4TWAhuGygFAgPzbNH3shp4HFL'
VALID_IDENTIFIER = "6ouriXMZkLeHsuXrN1X1fd"
VALID_REQID = 1517423828260117
CONS_TIME = 1518541344
PROTOCOL_VERSION = 1
SIGNATURES = {'B8fV7naUqLATYocqu7yZ8W':
                '27BVCWvThxMV9pzqz3JepMLVKww7MmreweYjh15LkwvAH4qwYAMbZWeYr6E6LcQexYAikTHo212U1NKtG8Gr2PPP',
              'M9BJDuS24bqbJNvBRsoGg3':
                '5BzS7J7uSuUePRzLdF5BL5LPvnXxzQyB5BqMT19Hz8QjEyb41Mum71TeNvPW9pKbhnDK12Pciqw9WRHUvsfwdYT5',
              'E7QRhdcnhAwA6E46k9EtZo':
                'MsZsG2uQHFqMvAsQsx5dnQiqBjvxYS1QsVjqHkbvdS2jPdZQhJfackLQbxQ4RDNUrDBy8Na6yZcKbjK2feun7fg',
              'CA4bVFDU4GLbX8xZju811o':
                '3A1Pmkox4SzYRavTj9toJtGBr1Jy9JvTTnHz5gkS5dGnY3PhDcsKpQCBfLhYbKqFvpZKaLPGT48LZKzUVY4u78Ki'}


@pytest.fixture(scope='function')
def node(txnPoolNodeSet):
    a, b, c, d = txnPoolNodeSet
    return a


@pytest.fixture(scope='function')
def token_handler(node):
    return node.ledger_to_req_handler[TOKEN_LEDGER_ID]


@pytest.yield_fixture(scope='function')
def node_state(node, token_handler, tdir):
    l = node.getLedger(TOKEN_LEDGER_ID)
    s = node.getState(TOKEN_LEDGER_ID)
    u = token_handler.utxo_cache
    old_dir = node.dataLocation
    node.dataLocation = tdir
    node.config.tokenTransactionsFile = randomString(6)
    node.config.tokenStateDbName = randomString(6)
    node.config.utxoCacheDbName = randomString(6)
    hash_store = get_token_hash_store(node.dataLocation)
    ledger = get_token_ledger(node.dataLocation,
                              node.config.tokenTransactionsFile,
                              hash_store, node.config)
    state = get_token_state(node.dataLocation,
                            node.config.tokenStateDbName,
                            node.config)
    utxo_cache = get_utxo_cache(node.dataLocation,
                                node.config.utxoCacheDbName,
                                node.config)
    token_handler.__init__(ledger, state, utxo_cache,
                           node.getLedger(DOMAIN_LEDGER_ID))
    yield node
    node.dataLocation = old_dir
    node.ledgerManager.ledgerRegistry[TOKEN_LEDGER_ID] = l
    node.states[TOKEN_LEDGER_ID] = s
    token_handler.utxo_cache = u


def test_token_req_handler_MINT_PUBLIC_validate_success(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: MINT_PUBLIC, OUTPUTS: [[VALID_ADDR_2, 60],
                                                          [VALID_ADDR_1, 40]]}
    request.identifier = VALID_IDENTIFIER
    ret_val = token_handler._MINT_PUBLIC_validate(request)
    assert ret_val == None


def test_token_req_handler_MINT_PUBLIC_validate_missing_output(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: MINT_PUBLIC}
    request.identifier = VALID_IDENTIFIER
    with pytest.raises(InvalidClientRequest):
        token_handler._MINT_PUBLIC_validate(request)


def test_token_req_handler_XFER_PUBLIC_validate_success(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: XFER_PUBLIC, OUTPUTS: [[VALID_ADDR_2, 60],
                                                          [VALID_ADDR_1, 40]],
                         INPUTS: [[VALID_ADDR_1, 1]]}
    request.identifier = VALID_IDENTIFIER
    ret_val = token_handler._XFER_PUBLIC_validate(request)
    assert ret_val == None


def test_token_req_handler_XFER_PUBLIC_validate_missing_output(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: XFER_PUBLIC,
                         INPUTS: [[VALID_ADDR_1, 1]]}
    request.identifier = VALID_IDENTIFIER
    with pytest.raises(InvalidClientRequest):
        token_handler._XFER_PUBLIC_validate(request)


def test_token_req_handler_XFER_PUBLIC_validate_missing_input(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: XFER_PUBLIC, OUTPUTS: [[VALID_ADDR_2, 60],
                                                          [VALID_ADDR_1, 40]]}
    request.identifier = VALID_IDENTIFIER
    with pytest.raises(InvalidClientRequest):
        token_handler._XFER_PUBLIC_validate(request)


def test_token_req_handler_GET_UTXO_validate_missing_address(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: GET_UTXO}
    request.identifier = VALID_IDENTIFIER
    with pytest.raises(InvalidClientRequest):
        token_handler._GET_UTXO_validate(request)


def test_token_req_handler_GET_UTXO_validate_success(token_handler):
    request = Mock(Request)
    request.reqId = VALID_REQID
    request.operation = {TXN_TYPE: GET_UTXO, ADDRESS: VALID_ADDR_2}
    request.identifier = VALID_IDENTIFIER
    ret_val = token_handler._GET_UTXO_validate(request)
    assert ret_val == None


def test_token_req_handler_doStaticValidation_MINT_PUBLIC_success(token_handler):
    request = Mock(Request)
    request.operation = {TXN_TYPE: MINT_PUBLIC,
                         OUTPUTS: [ [VALID_ADDR_2, 60], [VALID_ADDR_1, 40] ]}
    request.identifier = VALID_IDENTIFIER
    request.reqId = VALID_REQID
    try:
        token_handler.doStaticValidation(request)
    except InvalidClientRequest:
        pytest.fail("This test failed because error is not None")
    except Exception:
        pytest.fail("This test failed outside the doStaticValidation method")


def test_token_req_handler_doStaticValidation_XFER_PUBLIC_success(token_handler):
    request = Mock(Request)
    request.operation = {TXN_TYPE: XFER_PUBLIC,
                         OUTPUTS: [[VALID_ADDR_2, 60],[VALID_ADDR_1, 40]],
                         INPUTS: [[VALID_ADDR_1, 1]]}
    request.identifier = VALID_IDENTIFIER
    request.reqId = VALID_REQID
    try:
        token_handler.doStaticValidation(request)
    except InvalidClientRequest:
        pytest.fail("This test failed because error is not None")
    except Exception:
        pytest.fail("This test failed outside the doStaticValidation method")


def test_token_req_handler_doStaticValidation_GET_UTXO_success(token_handler):
    request = Mock(Request)
    request.operation = {TXN_TYPE: GET_UTXO, ADDRESS: VALID_ADDR_1}
    request.identifier = VALID_IDENTIFIER
    request.reqId = VALID_REQID
    try:
        token_handler.doStaticValidation(request)
    except InvalidClientRequest:
        pytest.fail("This test failed because error is not None")
    except Exception:
        pytest.fail("This test failed outside the doStaticValidation method")


def test_token_req_handler_doStaticValidation_invalid_txn_type(token_handler):
    request = Mock(Request)
    request.operation = {TXN_TYPE: 'Not valid TXN_TYPE'}
    request.identifier = VALID_IDENTIFIER
    request.reqId = VALID_REQID
    with pytest.raises(InvalidClientRequest):
        token_handler.doStaticValidation(request)


def test_token_req_handler_validate(token_handler):
    pass

# TODO: This test passes with GET_UTXO type, but not XFER_PUBLIC (KEYERROR)
def test_token_req_handler_apply_xfer_public_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: XFER_PUBLIC,
                                                      OUTPUTS: [[VALID_ADDR_2, 60]],
                                                      INPUTS: [[VALID_ADDR_1, 40]]}, None, SIGNATURES, 1)
    token_handler.validate(request)
    seq_no , txn = token_handler.apply(request, CONS_TIME)
    assert seq_no == 40
    assert txn == {OUTPUTS: [[VALID_ADDR_2, 60], [VALID_ADDR_1, 40]], TXN_TYPE: XFER_PUBLIC, 'reqId': VALID_REQID,
                   'signature': None, 'txnTime': CONS_TIME, 'identifier': VALID_IDENTIFIER, 'signatures': SIGNATURES}


def test_token_req_handler_apply_get_utxo_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: GET_UTXO}, None, SIGNATURES, 1)
    txn = reqToTxn(request, CONS_TIME)
    txn['seqNo'] = 1
    Ledger.appendTxns = MagicMock(return_value = ((1,1),txn))
    TokenReqHandler.updateState = MagicMock()
    TokenReqHandler.transform_txn_for_ledger =  MagicMock()
    util.txnsWithSeqNo =  MagicMock(return_value = [txn], wraps=util.txnsWithSeqNo)
    token_handler.apply(request, CONS_TIME)

    assert Ledger.appendTxns.call_count == 1
    assert token_handler.updateState.call_count == 1
    assert token_handler.transform_txn_for_ledger.call_count == 1
    # assert util.txnsWithSeqNo.call_count == 1

#TODO: this passes alone, but not with the class
def test_token_req_handler_updateState_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: XFER_PUBLIC,
                                                        OUTPUTS: [[VALID_ADDR_2, 60]],
                                                        INPUTS: [[VALID_ADDR_1, 40]]}, None, SIGNATURES, 1)
    txns = [reqToTxn(request, CONS_TIME)]
    txns_with_seqNo = txnsWithSeqNo(1,1,txns)
    token_handler._update_state_with_single_txn = MagicMock()
    token_handler.updateState(txns_with_seqNo)
    assert token_handler._update_state_with_single_txn.call_count == 1

# TODO: Fix this
def test_token_req_handler_update_state_with_single_txn_MINT_PUBLIC_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: MINT_PUBLIC,
                                                      OUTPUTS: [[VALID_ADDR_2, 60]]}, None, SIGNATURES, 1)
    txn = reqToTxn(request, CONS_TIME)
    TokenReqHandler._add_new_output = MagicMock()
    token_handler._update_state_with_single_txn(txn)
    TokenReqHandler._add_new_output.assert_called_with(Output(VALID_ADDR_2, txn[F.seqNo.name], 60))


# TODO: This test is failing -> missing state_root positional argument
def test_token_req_handler_onBatchCreated_success(token_handler):
    token_handler.onBatchCreated()
    assert token_handler.utxo_cache.un_committed == [Output(VALID_ADDR_1, 40, 100)]


def test_token_req_handler_onBatchRejected_success(token_handler):
    token_handler._add_new_output(Output(VALID_ADDR_1, 40, 100))
    token_handler.onBatchRejected()
    assert token_handler.utxo_cache.un_committed == []

#This relies upon validate and apply having occurred already
def test_token_req_handler_commit_success(token_handler):
    pass

#TODO: if this test is below get_query_response_success it fails when all are run. It's interacting somehow
def test_token_req_handler_get_all_utxo_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: GET_UTXO, ADDRESS: VALID_ADDR_1}, None, SIGNATURES, 1)
    query_result = token_handler.get_all_utxo(request)
    assert query_result == {'identifier': VALID_IDENTIFIER, 'reqId':VALID_REQID,
                            ADDRESS: VALID_ADDR_1, TXN_TYPE: GET_UTXO, OUTPUTS: []}

# This test cant pass because spying on switch statements doesn't work
# If get_query_response() is refactored it will pass
def test_token_req_handler_get_query_response_success(token_handler):
    request = Request(VALID_IDENTIFIER, VALID_REQID, {TXN_TYPE: GET_UTXO, ADDRESS: VALID_ADDR_1}, None, SIGNATURES, 1)
    TokenReqHandler.get_all_utxo = MagicMock()
    token_handler.get_query_response(request)
    TokenReqHandler.get_all_utxo.assert_called_with(request)


def test_token_req_handler_create_state_key_success(token_handler):
    state_key = token_handler.create_state_key(VALID_ADDR_1, 40)
    assert state_key == b'6baBEYA94sAphWBA5efEsaA6X2wCdyaH7PXuBtv2H5S1:40'


def test_token_req_handler_sum_inputs_success(token_handler):
    pass


def test_token_req_handler_spend_input_success(token_handler):
    pass


def test_token_req_handler_add_new_output_success(token_handler):
    pass