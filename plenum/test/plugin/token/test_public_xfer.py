import pytest

from ledger.util import F
from plenum.common.util import lxor
from plenum.server.plugin.token.constants import OUTPUTS
from plenum.server.plugin.token.wallet import TokenWallet
from plenum.test.plugin.token.helper import do_public_minting, send_xfer, \
    check_output_val_on_all_nodes, xfer_request, send_get_utxo
from plenum.test.pool_transactions.conftest import clientAndWallet1, \
    client1, wallet1, client1Connected, looper

total_mint = 100
seller_gets = 40


@pytest.fixture(scope='module') # noqa
def public_minting(looper, txnPoolNodeSet, client1, # noqa
                   wallet1, client1Connected, trustee_wallets,
                   SF_address, seller_address):
    return do_public_minting(looper, trustee_wallets, client1, total_mint,
                             total_mint - seller_gets, SF_address,
                             seller_address)


@pytest.fixture(scope="module")
def user1_token_wallet():
    return TokenWallet('user1')


@pytest.fixture(scope="module")
def user2_token_wallet():
    return TokenWallet('user2')


@pytest.fixture(scope="module")
def user1_address(user1_token_wallet):
    seed = 'user1000000000000000000000000000'.encode()
    user1_token_wallet.add_new_address(seed=seed)
    return next(iter(user1_token_wallet.addresses.keys()))


@pytest.fixture(scope="module")
def user2_address(user2_token_wallet):
    seed = 'user2000000000000000000000000000'.encode()
    user2_token_wallet.add_new_address(seed=seed)
    return next(iter(user2_token_wallet.addresses.keys()))


def test_seller_xfer_invalid_outputs(public_minting, looper, txnPoolNodeSet,# noqa
                                     client1, seller_token_wallet,
                                     seller_address, user1_address):
    global seller_gets
    seq_no = public_minting[F.seqNo.name]
    inputs = [[seller_token_wallet, seller_address, seq_no]]
    seller_remaining = seller_gets - 10
    outputs = [[user1_address, 10], [seller_address, seller_remaining / 2],
               [seller_address, seller_remaining / 2]]
    with pytest.raises(AssertionError):
        send_xfer(looper, inputs, outputs, client1)


def test_seller_xfer_invalid_amount(public_minting, looper, txnPoolNodeSet, # noqa
                                    client1, seller_token_wallet,
                                    seller_address, user1_address):
    global seller_gets
    seq_no = public_minting[F.seqNo.name]
    inputs = [[seller_token_wallet, seller_address, seq_no]]
    seller_remaining = seller_gets + 10
    outputs = [[user1_address, 10], [seller_address, seller_remaining]]
    with pytest.raises(AssertionError):
        send_xfer(looper, inputs, outputs, client1)


@pytest.fixture(scope='module')     # noqa
def valid_xfer_txn_done(public_minting, looper, txnPoolNodeSet, client1,
                        seller_token_wallet, seller_address, user1_address):
    global seller_gets
    seq_no = public_minting[F.seqNo.name]
    user1_gets = 10
    seller_gets -= user1_gets
    inputs = [[seller_token_wallet, seller_address, seq_no]]
    outputs = [[user1_address, user1_gets], [seller_address, seller_gets]]
    req = send_xfer(looper, inputs, outputs, client1)
    check_output_val_on_all_nodes(txnPoolNodeSet, seller_address, seller_gets)
    check_output_val_on_all_nodes(txnPoolNodeSet, user1_address, user1_gets)
    result, _ = client1.getReply(req.identifier, req.reqId)
    return result


def test_seller_xfer_valid(valid_xfer_txn_done):
    pass


def test_seller_xfer_double_spend_attempt(looper, txnPoolNodeSet, client1,  # noqa
                                          seller_token_wallet, seller_address,
                                          valid_xfer_txn_done, user1_address,
                                          user2_address):
    seq_no = valid_xfer_txn_done[F.seqNo.name]
    user1_gets = 3
    user2_gets = 5
    inputs = [[seller_token_wallet, seller_address, seq_no]]
    seller_remaining = seller_gets - user1_gets
    outputs1 = [[user1_address, user1_gets], [seller_address, seller_remaining]]
    seller_remaining -= user2_gets
    outputs2 = [[user2_address, user2_gets], [seller_address, seller_remaining]]
    xfer_request(inputs, outputs1, client1)
    xfer_request(inputs, outputs2, client1)
    # So that both requests are sent simultaneously
    looper.runFor(.2)
    # Both requests should not be successful, one and only one should be
    sucs1, sucs2 = False, False
    try:
        check_output_val_on_all_nodes(txnPoolNodeSet, user1_address, user1_gets)
        sucs1 = True
    except Exception:
        pass

    try:
        check_output_val_on_all_nodes(txnPoolNodeSet, user2_address, user2_gets)
        sucs2 = True
    except Exception:
        pass

    assert lxor(sucs1, sucs2)

    if sucs1:
        check_output_val_on_all_nodes(txnPoolNodeSet, seller_address,
                                      seller_gets - user1_gets)
    else:
        check_output_val_on_all_nodes(txnPoolNodeSet, seller_address,
                                      seller_gets - user2_gets)


def test_query_utxo(looper, txnPoolNodeSet, client1, wallet1, seller_token_wallet,  # noqa
                    seller_address, valid_xfer_txn_done, user1_address):
    req1 = send_get_utxo(looper, seller_address, wallet1, client1)
    rep1, _ = client1.getReply(wallet1.defaultId, req1.reqId)
    assert rep1[OUTPUTS]

    req2 = send_get_utxo(looper, user1_address, wallet1, client1)
    rep2, _ = client1.getReply(wallet1.defaultId, req2.reqId)
    assert rep2[OUTPUTS]

    with pytest.raises(AssertionError):
        send_get_utxo(looper, '', wallet1, client1)
