from plenum.common.constants import TXN_TYPE
from plenum.common.types import f
from plenum.server.plugin.token.constants import MINT_PUBLIC, OUTPUTS, XFER
from plenum.test.helper import waitForSufficientRepliesForRequests


def send_mint_public(looper, trustees, outputs, sender_client):
    signatures = {}
    op = {
        TXN_TYPE: MINT_PUBLIC,
        OUTPUTS: outputs,
    }
    first_trustee = trustees[0]
    request = first_trustee.sign_using_multi_sig(
        op, identifier=first_trustee.defaultId)
    for wallet in trustees[1:]:
        signatures[wallet.defaultId] = wallet.do_multi_sig_on_req(
            request, identifier=wallet.defaultId)
    sender_client.submitReqs(request)
    waitForSufficientRepliesForRequests(looper, sender_client,
                                        requests=[request], fVal=1)
    return request


def do_public_minting(looper, trustees, sender_client, total_mint,
                      sf_master_share, sf_address, seller_address):
    seller_share = total_mint - sf_master_share
    outputs = [[sf_address, sf_master_share], [seller_address, seller_share]]
    send_mint_public(looper, trustees, outputs, sender_client)


def send_xfer(inputs, outputs, sender_client, sender_wallet, extra_data=None):
    op = {
        TXN_TYPE: XFER,
    }

    req = sender_wallet.signOp(op)
    sender_client.submitReqs(req)
    return req, sender_wallet
