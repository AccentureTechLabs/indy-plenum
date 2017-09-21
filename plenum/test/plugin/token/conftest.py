import pytest

from plenum.client.wallet import Wallet
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import randomSeed
from plenum.server.plugin.token.client_authnr import TokenAuthNr
from plenum.server.plugin.token.constants import TOKEN_LEDGER_ID
from plenum.server.plugin.token.main import update_node_class, update_node_obj
from plenum.server.plugin.token.wallet import TokenWallet
from plenum.test.plugin.helper import getPluginPath
from plenum.test.test_node import TestNode


def build_wallets_from_data(name_seeds):
    wallets = []
    for name, seed in name_seeds:
        w = Wallet(name)
        w.addIdentifier(seed=seed.encode())
        wallets.append(w)
    return wallets


@pytest.fixture(scope="module")
def SF_token_wallet():
    return TokenWallet('SF_MASTER')


@pytest.fixture(scope="module")
def SF_address(SF_token_wallet):
    seed = 'sf000000000000000000000000000000'.encode()
    SF_token_wallet.add_new_address(seed=seed)
    return SF_token_wallet.addresses[0].address


@pytest.fixture(scope="module")
def seller_token_wallet():
    return TokenWallet('SELLER')


@pytest.fixture(scope="module")
def seller_address(seller_token_wallet):
    # Token selling/buying platform's address
    seed = 'se000000000000000000000000000000'.encode()
    seller_token_wallet.add_new_address(seed=seed)
    return seller_token_wallet.addresses[0].address


@pytest.fixture(scope="module")
def trustee_wallets(trustee_data):
    return build_wallets_from_data(trustee_data)


@pytest.fixture(scope="module")
def allPluginsPath(allPluginsPath):
    return allPluginsPath + [getPluginPath('token')]


@pytest.fixture(scope="module")
def testNodeClass(patchPluginManager):
    return update_node_class(TestNode)


@pytest.fixture(scope="module")
def txnPoolNodeSet(txnPoolNodeSet):
    for node in txnPoolNodeSet:
        update_node_obj(node)
    return txnPoolNodeSet
