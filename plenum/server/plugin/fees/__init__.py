from plenum.server.plugin.fees.messages.fields import TxnFeesField
from plenum.server.plugin.fees.transactions import FeesTransactions

# TODO: Fix this, use a constant
CLIENT_REQUEST_FIELDS = {
    'fees': TxnFeesField(optional=True, nullable=True),
}

AcceptableWriteTypes = {FeesTransactions.FEE.value, }

AcceptableQueryTypes = {FeesTransactions.GET_FEES.value, }
