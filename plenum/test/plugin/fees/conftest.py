import pytest

from plenum.common.constants import NYM
from plenum.server.plugin.fees.wallet import FeeSupportedWallet
from plenum.server.plugin.token.constants import XFER_PUBLIC
from plenum.server.plugin.token.main import update_node_obj as enable_token
from plenum.server.plugin.fees.main import update_node_obj as enable_fees
from plenum.server.plugin.token.util import register_token_wallet_with_client
from plenum.test.plugin.token.helper import send_get_utxo, send_xfer

# fixtures, do not remove
from plenum.test.pool_transactions.conftest import clientAndWallet1, \
    client1, wallet1, client1Connected, looper, stewardAndWallet1, steward1, \
    stewardWallet
from plenum.test.plugin.token.conftest import trustee_wallets, SF_address, \
    seller_address, seller_token_wallet, SF_token_wallet, tokens_distributed
from plenum.test.plugin.token.test_public_xfer_1 import public_minting, \
    user1_address, user1_token_wallet, user2_address, user2_token_wallet, \
    user3_address, user3_token_wallet


@pytest.fixture(scope="module")
def txnPoolNodeSet(txnPoolNodeSet):
    for node in txnPoolNodeSet:
        enable_token(node)
        enable_fees(node)
    return txnPoolNodeSet


@pytest.fixture(scope="module")
def fees():
    return {
        NYM: 4,
        XFER_PUBLIC: 8
    }


# Wallet should have support to track fees

@pytest.fixture(scope="module")
def seller_token_wallet():
    return FeeSupportedWallet('SELLER')


@pytest.fixture(scope="module") # noqa
def user1_token_wallet():
    return FeeSupportedWallet('user1')


@pytest.fixture(scope="module") # noqa
def user2_token_wallet():
    return FeeSupportedWallet('user2')


@pytest.fixture(scope="module") # noqa
def user3_token_wallet():
    return FeeSupportedWallet('user3')
