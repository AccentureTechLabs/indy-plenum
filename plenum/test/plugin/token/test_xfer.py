import pytest


@pytest.fixture(scope="module")
def inputs_added(looper, txnPoolNodeSet):

    return


def test_xfer_repeating_inputs_outputs(looper, txnPoolNodeSet, client1,
                                       wallet1, client1Connected):
    """
    Test that inputs (address+seq_no) are not repeated.
    Test that output addresses are not repeated.
    """
    pass


def test_xfer_non_existent_inputs(looper, txnPoolNodeSet, client1,
                                  wallet1, client1Connected):
    """
    Test that non existent inputs are rejected.
    """
    pass


def test_xfer_small_inputsa(looper, txnPoolNodeSet, client1,
                            wallet1, client1Connected):
    """
    Test that inputs without sufficient balance are rejected.
    """
    pass
