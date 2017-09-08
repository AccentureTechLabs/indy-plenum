# It is assumed the initial minting will give some tokens to the Sovrin
# Foundation and Exchange. From then on, exchange will be responsible for
# giving tokens to "users".
from plenum.test.pool_transactions.conftest import clientAndWallet1, \
    client1, wallet1, client1Connected, looper
from plenum.test.plugin.token.helper import send_mint_public


def test_trustee_minting(looper, txnPoolNodeSet, client1, # noqa
                         wallet1, client1Connected, trustee_wallets,
                         SF_address, seller_address):
    """
    Trustees should mint new tokens increasing the balance of `SF_MASTER`
    and seller_address
    """
    total_mint = 100
    sf_master_gets = 60
    seller_gets = total_mint - sf_master_gets
    outputs = [[SF_address, sf_master_gets], [seller_address, seller_gets]]
    send_mint_public(trustee_wallets, outputs, client1, wallet1)
