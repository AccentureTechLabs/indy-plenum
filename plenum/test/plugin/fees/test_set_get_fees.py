import pytest

from plenum.common.constants import NYM, STEWARD
from plenum.server.plugin.fees.constants import FEES
from plenum.server.plugin.token.constants import XFER_PUBLIC
from plenum.test.conftest import get_data_for_role
from plenum.test.plugin.fees.helper import send_set_fees, set_fees, \
    send_get_fees, get_fees_from_ledger, \
    check_fee_req_handler_in_memory_map_updated
from plenum.test.plugin.token.conftest import build_wallets_from_data


def test_get_fees_when_no_fees_set(looper, txnPoolNodeSet, wallet1, client1, # noqa
                                   client1Connected):
    assert get_fees_from_ledger(looper, wallet1, client1) == {}
    check_fee_req_handler_in_memory_map_updated(txnPoolNodeSet, {})


def test_trustee_set_invalid_fees(looper, txnPoolNodeSet, wallet1, client1, # noqa
                                  client1Connected, trustee_wallets):
    """
    Fees cannot be negative
    """
    fees = {
        NYM: -1,
        XFER_PUBLIC: 2
    }
    with pytest.raises(AssertionError):
        send_set_fees(looper, trustee_wallets, fees, client1)
    assert get_fees_from_ledger(looper, wallet1, client1) == {}


def test_non_trustee_set_fees(looper, txnPoolNodeSet, wallet1, client1, # noqa
                              client1Connected, poolTxnData):
    """
    Only trustees can change the fees
    """
    fees = {
        NYM: 1,
        XFER_PUBLIC: 2
    }
    steward_data = get_data_for_role(poolTxnData, STEWARD)
    steward_wallets = build_wallets_from_data(steward_data)
    with pytest.raises(AssertionError):
        send_set_fees(looper, steward_wallets, fees, client1)
    assert get_fees_from_ledger(looper, wallet1, client1) == {}


@pytest.fixture(scope="module")
def fees_set(looper, txnPoolNodeSet, client1, # noqa
             client1Connected, trustee_wallets, fees):
    return set_fees(looper, trustee_wallets, fees, client1)


def test_trustee_set_valid_fees(fees_set, txnPoolNodeSet, fees):
    """
    Set a valid fees
    """
    check_fee_req_handler_in_memory_map_updated(txnPoolNodeSet, fees)


def test_get_fees(fees_set, looper, txnPoolNodeSet, client1, wallet1,
                  client1Connected, fees):
    """
    Get the fees from the ledger
    """
    assert get_fees_from_ledger(looper, wallet1, client1) == fees


def test_change_fees(fees_set, looper, txnPoolNodeSet, client1, wallet1,
                     client1Connected, trustee_wallets, fees):
    """
    Change the fees on the ledger and check that fees has changed
    """
    updated_fees = {**fees, NYM: 10}
    set_fees(looper, trustee_wallets, updated_fees, client1)
    new_fees = get_fees_from_ledger(looper, wallet1, client1)
    assert new_fees == updated_fees
    assert new_fees != fees
    check_fee_req_handler_in_memory_map_updated(txnPoolNodeSet, updated_fees)
