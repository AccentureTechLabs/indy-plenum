import pytest

from plenum.client.wallet import Wallet
from plenum.common.signer_simple import SimpleSigner
from plenum.server.plugin.token.wallet import TokenWallet


@pytest.fixture(scope="module")
def SF_token_wallet():
    return TokenWallet('SF_MASTER')


@pytest.fixture(scope="module")
def SF_address(SF_token_wallet):
    SF_token_wallet.add_new_address()
    return SF_token_wallet.addresses[0].address


@pytest.fixture(scope="module")
def seller_token_wallet():
    return TokenWallet('SELLER')


@pytest.fixture(scope="module")
def seller_address(seller_token_wallet):
    # Token selling/buying platform's address
    seller_token_wallet.add_new_address()
    return seller_token_wallet.addresses[0].address


@pytest.fixture(scope="module")
def trustee_wallets(trustee_data):
    wallets = []
    for name, seed in trustee_data:
        w = Wallet(name)
        w.addIdentifier(signer=SimpleSigner(seed=seed))
        wallets.append(w)
    return wallets
