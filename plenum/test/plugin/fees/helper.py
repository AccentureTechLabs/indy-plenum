from plenum.common.constants import TXN_TYPE
from plenum.server.plugin.fees.constants import FEE, FEES, GET_FEES
from plenum.test.helper import waitForSufficientRepliesForRequests


def set_fees_request(trustees, fees, sender_client):
    signatures = {}
    op = {
        TXN_TYPE: FEE,
        FEES: fees,
    }
    first_trustee = trustees[0]
    request = first_trustee.sign_using_multi_sig(
        op, identifier=first_trustee.defaultId)
    for wallet in trustees[1:]:
        signatures[wallet.defaultId] = wallet.do_multi_sig_on_req(
            request, identifier=wallet.defaultId)
    sender_client.submitReqs(request)
    return request


def send_set_fees(looper, trustees, fees, sender_client):
    request = set_fees_request(trustees, fees, sender_client)
    waitForSufficientRepliesForRequests(looper, sender_client,
                                        requests=[request], fVal=1)
    return request


def set_fees(looper, trustees, fees, sender_client):
    request = send_set_fees(looper, trustees, fees, sender_client)
    result, _ = sender_client.getReply(request.identifier, request.reqId)
    return result


def get_fees_request(sender_wallet, sender_client):
    op = {
        TXN_TYPE: GET_FEES,
    }
    request = sender_wallet.signOp(op)
    sender_client.submitReqs(request)
    return request


def send_get_fees(looper, sender_wallet, sender_client):
    request = get_fees_request(sender_wallet, sender_client)
    waitForSufficientRepliesForRequests(looper, sender_client,
                                        requests=[request], fVal=1)
    return request


def get_fees_from_ledger(looper, wallet, client):
    req = send_get_fees(looper, wallet, client)
    rep, _ = client.getReply(wallet.defaultId, req.reqId)
    return rep[FEES]


def check_fee_req_handler_in_memory_map_updated(nodes, fees):
    for node in nodes:
        assert node.get_req_handler(txn_type=FEE).fees == fees
