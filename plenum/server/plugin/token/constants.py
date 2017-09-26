from plenum.server.plugin.token.transactions import TokenTransactions

INPUTS = 'inputs'
OUTPUTS = 'outputs'
EXTRA = 'extra'
ADDRESS = 'address'

TOKEN_LEDGER_ID = 1001

MINT_PUBLIC = TokenTransactions.MINT_PUBLIC.value
# TODO: Change to PUBLIC_XFER
XFER = TokenTransactions.XFER.value
GET_UTXO = TokenTransactions.GET_UTXO.value
