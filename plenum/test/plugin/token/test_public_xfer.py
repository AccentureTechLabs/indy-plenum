import pytest

from plenum.server.plugin.token.wallet import TokenWallet
from plenum.test.plugin.token.helper import do_public_minting


@pytest.fixture(scope='module')
def public_minting(looper, txnPoolNodeSet, client1, # noqa
                   wallet1, client1Connected, trustee_wallets,
                   SF_address, seller_address):
    total_mint = 100
    sf_master_gets = 60
    do_public_minting(looper, trustee_wallets, client1, total_mint,
                      sf_master_gets, SF_address, seller_address)


@pytest.fixture(scope="module")
def user1_token_wallet():
    return TokenWallet('user1')


@pytest.fixture(scope="module")
def user1_address(user1_token_wallet):
    seed = 'user1000000000000000000000000000'.encode()
    user1_token_wallet.add_new_address(seed=seed)
    return user1_token_wallet.addresses[0].address


def test_seller_valid_xfer(public_minting, looper, txnPoolNodeSet, client1,
                           seller_token_wallet, seller_address, user1_address):
    # TODO:
    pass
