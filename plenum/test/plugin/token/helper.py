from plenum.common.constants import TXN_TYPE
from plenum.common.types import f
from plenum.server.plugin.token.constants import MINT_PUBLIC, OUTPUTS, XFER


def send_mint_public(trustees, outputs, sender_client, sender_wallet):
    signatures = {}
    op = {
        TXN_TYPE: MINT_PUBLIC,
        OUTPUTS: outputs,
    }
    for wallet in trustees:
        signatures[wallet.defaultId] = wallet.signMsg(
            op, identifier=wallet.defaultId)
    op[f.SIGS.nm] = signatures


def send_xfer(inputs, outputs, sender_client, sender_wallet, extra_data=None):
    op = {
        TXN_TYPE: XFER,
    }

    req = sender_wallet.signOp(op)
    sender_client.submitReqs(req)
    return req, sender_wallet
