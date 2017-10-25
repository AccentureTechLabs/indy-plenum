from plenum.test.plugin.token.test_public_xfer import public_minting, \
    user1_address, user1_token_wallet, user2_address, user2_token_wallet, \
    user3_address, user3_token_wallet


# def inputs_outputs():
#     inputs = [[seller_token_wallet, addr.address, new_seq_no]
#               for addr in new_addrs]
#     inputs = [[user1_token_wallet,
#                user1_token_wallet.get_all_utxos(address=user1_address)]]
#     outputs = [[user1_address, sum_utxo_val], ]
#     return inputs, outputs


def test_multiple_inputs_with_1_incorrect_input_address(tokens_distributed,
                                                        looper, txnPoolNodeSet,
                                                        client1,
                                                        seller_token_wallet,
                                                        seller_address):

    # send_xfer(looper, inputs, outputs, client1)
    pass


def test_multiple_inputs_with_1_incorrect_input_sig():
    # TODO:
    pass


def test_multiple_inputs_outputs_without_change():
    # TODO
    pass


def test_multiple_inputs_outputs_with_change():
    # TODO
    pass
