import pytest

from plenum.common.constants import NYM, TXN_TYPE
from plenum.common.types import f
from plenum.common.util import randomString
from plenum.server.plugin.fees.constants import FEES
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.pool_transactions.helper import new_client_request
from plenum.test.plugin.fees.test_set_get_fees import fees_set


def test_insufficient_fees(tokens_distributed, looper, steward1, stewardWallet,  # noqa
              client1, wallet1, client1Connected, fees_set, user1_address,
              user1_token_wallet):
    """
    The fee amount is less than required
    """
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    fee_amount -= 1
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    client1.submitReqs(req)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1, requests=[req])


def test_fees_incorrect_sig(tokens_distributed, looper, steward1, stewardWallet,  # noqa
              client1, wallet1, client1Connected, fees_set, user1_address,
              user1_token_wallet):
    """
    The fee amount is correct but signature over the fee is incorrect.
    """
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    fee_senders = [s[0] for s in getattr(req, f.FEES.nm)[0]]
    sigs = getattr(req, f.SIGS.nm)
    for s in sigs:
        if s in fee_senders:
            # reverse the signature to make it incorrect
            sigs[s] = sigs[s][::-1]
    client1.submitReqs(req)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1, requests=[req])


def test_invalid_fees_valid_payload(tokens_distributed, looper, steward1, stewardWallet,  # noqa
              client1, wallet1, client1Connected, fees_set, user1_address,
                                    user1_token_wallet, seller_token_wallet,
                                    seller_address):
    """
    The fee amount is correct but the payer does not have enough tokens to
    pay the fees, though the payload is a valid txn.
    """
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    utxos = seller_token_wallet.get_all_utxos(seller_address).values()
    utxo = next(iter(utxos))[0]
    # The sender owns less tokens
    assert utxo[1] < fee_amount
    fees, sigs = seller_token_wallet.get_fees_and_sigs([[seller_address,
                                                         utxo[0]]], [])
    req.__setattr__(f.FEES.nm, fees)
    for addr, sig in sigs.items():
        req.add_signature(addr, sig)
    client1.submitReqs(req)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1, requests=[req])


def test_valid_fees_invalid_payload_sig(tokens_distributed, looper, steward1, stewardWallet,  # noqa
                                client1, wallet1, client1Connected, fees_set,
                                user1_address, user1_token_wallet):
    """
    The fee part of the txn is valid but the payload has invalid signature
    """
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    # Reverse the signature of NYM txn sender, making it invalid
    req.__setattr__(f.SIG.nm, getattr(req, f.SIG.nm)[::-1])
    client1.submitReqs(req)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1, requests=[req])


def test_valid_fees_invalid_payload(tokens_distributed, looper, steward1, stewardWallet,  # noqa
              client1, wallet1, client1Connected, fees_set,
              user1_address, user1_token_wallet):
    """
    The fee part of the txn is valid but the payload fails dynamic validation
    (unauthorised request)
    """
    name = randomString(6)
    # Try to register new DID but sender is not Steward
    req, wallet = new_client_request(None, name, wallet1)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    client1.submitReqs(req)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1, requests=[req])


@pytest.fixture(scope="module")
def fees_paid(tokens_distributed, looper, steward1, stewardWallet,  # noqa
              client1, wallet1, client1Connected, fees_set,
              user1_address, user1_token_wallet):
    name = randomString(6)
    req, wallet = new_client_request(None, name, stewardWallet)
    fee_amount = fees_set[FEES][req.operation[TXN_TYPE]]
    req = user1_token_wallet.add_fees_to_request(req, fee_amount=fee_amount,
                                                 address=user1_address)
    client1.submitReqs(req)
    waitForSufficientRepliesForRequests(looper, client1, requests=[req])


def test_valid_txn_with_fees(fees_paid):
    """
    Provide sufficient fees for transaction with correct signatures and payload
    """
    pass


def test_fees_utxo_reuse(fees_paid):
    """
    Check that utxo used in fees cannot be reused
    """
    # TODO
    pass
