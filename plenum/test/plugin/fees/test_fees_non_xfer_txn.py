from plenum.common.constants import NYM, TXN_TYPE
from plenum.common.util import randomString
from plenum.server.plugin.fees.constants import FEES
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.pool_transactions.helper import new_client_request
from plenum.test.plugin.fees.test_set_get_fees import fees_set


def test_fees(fees_set, looper, steward1, stewardWallet,    # noqa
              client1, wallet1, client1Connected, tokens_distributed,
              user1_address, user1_token_wallet):
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    client1.submitReqs(req)
    waitForSufficientRepliesForRequests(looper, client1, requests=[req], fVal=1)
