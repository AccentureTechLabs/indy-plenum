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
                                                    user3_token_wallet):

    inputs, outputs = inputs_outputs(user1_token_wallet, user2_token_wallet,
                                     user3_token_wallet,
                                     output_addr=seller_address)

    request = xfer_request(inputs, outputs, client1)
    sigs = getattr(request, f.SIGS.nm)
    sigs[request.operation[INPUTS][1][0]] = sigs[request.operation[INPUTS][0][0]]
    with pytest.raises(AssertionError):
        waitForSufficientRepliesForRequests(looper, client1,
                                            requests=[request], fVal=1)


def test_multiple_inputs_outputs_without_change():
    # TODO
    pass


def test_multiple_inputs_outputs_with_change():
    # TODO
    pass
