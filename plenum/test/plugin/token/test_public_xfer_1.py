import pytest

from plenum.common.types import f
from plenum.server.plugin.token.constants import INPUTS
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.plugin.token.helper import send_xfer, xfer_request
from plenum.test.pool_transactions.conftest import clientAndWallet1, \
    client1, wallet1, client1Connected, looper
from plenum.test.plugin.token.test_public_xfer import public_minting, \
    user1_address, user1_token_wallet, user2_address, user2_token_wallet, \
    user3_address, user3_token_wallet


def inputs_outputs(*input_token_wallets, output_addr, change_addr=None,
                   change_amount=None):
    inputs = []
    out_amount = 0
    for tw in input_token_wallets:
        addr, vals = next(iter(tw.get_all_utxos().items()))
        inputs.append([tw, addr.address, vals[0][0]])
        out_amount += vals[0][1]

    if change_amount is not None:
        assert change_amount <= out_amount
        out_amount -= change_amount

    outputs = [[output_addr, out_amount], ]
    if change_addr:
        outputs.append([change_addr, change_amount])
    return inputs, outputs


def test_multiple_inputs_with_1_incorrect_input_sig(tokens_distributed, # noqa
                                                    looper,
                                                    client1,
                                                    seller_address,
                                                    user1_token_wallet,
                                                    user2_token_wallet,
                                                    user3_token_wallet,
                                                    seller_token_wallet):
    # Multiple inputs are used in a transaction but one of the inputs
    # has incorrect signature
    inputs, outputs = inputs_outputs(user1_token_wallet, user2_token_wallet,
                                     user3_token_wallet,
                                     output_addr=seller_address)

    request = xfer_request(inputs, outputs)
    sigs = getattr(request, f.SIGS.nm)
    # Change signature for 2nd input, set it same as the 1st input's signature
    sigs[request.operation[INPUTS][1][0]] = sigs[request.operation[INPUTS][0][0]]
    client1.submitReqs(request)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1,
                                            requests=[request])


def test_multiple_inputs_with_1_missing_sig(tokens_distributed, # noqa
                                            looper,
                                            client1,
                                            seller_address,
                                            user1_token_wallet,
                                            user2_token_wallet,
                                            user3_token_wallet,
                                            seller_token_wallet):
    # Multiple inputs are used in a transaction but one of the inputs's
    # signature is missing, 2 cases are checked, in 1st case one of the input's
    # signature is removed from the request so there are 3 inputs but only 2
    # signatures, in 2nd case one of the inputs signature is still not included
    #  but a different input's signature is added which is not being spent in
    # this txn, so there are 3 inputs and 3 signtures.
    inputs, outputs = inputs_outputs(user1_token_wallet, user2_token_wallet,
                                     user3_token_wallet,
                                     output_addr=seller_address)

    # Remove signature for 2nd input
    request = xfer_request(inputs, outputs)
    sigs = getattr(request, f.SIGS.nm)
    del sigs[request.operation[INPUTS][1][0]]
    assert len(sigs) == (len(inputs) - 1)
    client1.submitReqs(request)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1,
                                            requests=[request])

    # Add signature from an address not present in input
    seq_no, _ = next(iter(
        seller_token_wallet.get_all_utxos(seller_address).values()))[0]
    seller_token_wallet.sign_using_output(seller_address, seq_no,
                                          request=request)
    assert len(sigs) == len(inputs)
    client1.submitReqs(request)
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1,
                                            requests=[request])


def test_multiple_inputs_outputs_without_change():
    # TODO
    pass


def test_multiple_inputs_outputs_with_change():
    # TODO
    pass
