# It is assumed the initial minting will give some tokens to the Sovrin
# Foundation and Exchange. From then on, exchange will be responsible for
# giving tokens to "users".


def test_trustee_minting(looper, txnPoolNodeSet, client1,
                         wallet1, client1Connected):
    """
    Trustees should mint new tokens increasing the balance of `SF_MASTER`
    and exchange_address
    """
    pass
