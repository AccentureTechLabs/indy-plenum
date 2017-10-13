import pytest

from plenum.server.plugin.token.wallet import TokenWallet, Address


def test_set_get_utxo():
    wallet = TokenWallet()
    address1 = Address()
    address2 = Address()
    address3 = Address()
    wallet.add_new_address(address1)
    wallet.add_new_address(address2)
    wallet.add_new_address(address3)

    vals = [(address1.address, 1), (address2.address, 2),
            (address3.address, 10)]

    with pytest.raises(ValueError):
        wallet._update_outputs(outputs=vals)

    with pytest.raises(ValueError):
        wallet._update_outputs(outputs=vals, txn_seq_no='3001')

    wallet._update_outputs(outputs=vals, txn_seq_no=3001)
    assert wallet.get_total_amount(address1.address) == 1
    assert wallet.get_total_amount(address2.address) == 2
    assert wallet.get_total_amount(address3.address) == 10
    assert wallet.get_total_amount() == 13

    vals = [(address1.address, 3002, 1), (address2.address, 3002, 2),
            (address3.address, 3003, 10)]
    wallet._update_outputs(outputs=vals)
    assert wallet.get_total_amount(address1.address) == 2
    assert wallet.get_total_amount(address2.address) == 4
    assert wallet.get_total_amount(address3.address) == 20
    assert wallet.get_total_amount() == 26

    wallet._update_outputs(outputs=[(address3.address, 3004, 3)])
    wallet._update_outputs(outputs=[(address3.address, 9010, 4)])
    wallet._update_outputs(outputs=[(address3.address, 3005, 15)])
    wallet._update_outputs(outputs=[(address3.address, 1010, 16)])

    assert wallet.get_min_utxo_ge(0) == (address1.address, 3001, 1)
    assert wallet.get_min_utxo_ge(1) == (address1.address, 3001, 1)
    assert wallet.get_min_utxo_ge(1, address=address3.address) == (address3.address,
                                                                   3004, 3)
    assert wallet.get_min_utxo_ge(2, address=address3.address) == (address3.address,
                                                                   3004, 3)
    assert wallet.get_min_utxo_ge(3, address=address3.address) == (address3.address,
                                                                   3004, 3)
    assert wallet.get_min_utxo_ge(4, address=address3.address) == (address3.address,
                                                                   9010, 4)
    assert wallet.get_min_utxo_ge(5, address=address3.address) == (address3.address,
                                                                   3001, 10)
    assert wallet.get_min_utxo_ge(11, address=address3.address) == (address3.address,
                                                                    3005, 15)

    # Repeating same address
    vals = [(address1.address, 1), (address1.address, 2),
            (address3.address, 10)]
    with pytest.raises(AssertionError):
        wallet._update_outputs(outputs=vals, txn_seq_no=2)
