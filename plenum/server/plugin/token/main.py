from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.server.plugin.token.client_authnr import TokenAuthNr
from plenum.server.plugin.token.config import get_config
from plenum.server.plugin.token.constants import TOKEN_LEDGER_ID
from plenum.server.plugin.token.storage import get_token_hash_store, get_token_ledger, get_token_state


def patch_node_class(node_class):
    node_class.ledger_ids += [TOKEN_LEDGER_ID, ]
    return node_class


def patch_node_obj(node):
    node.config = get_config(node.config)
    token_authnr = TokenAuthNr(node.states[DOMAIN_LEDGER_ID])
    hash_store = get_token_hash_store(node.dataLocation)
    ledger = get_token_ledger(node.dataLocation,
                              node.config.tokenTransactionsFile,
                              hash_store, node.config)
    state = get_token_state(node.dataLocation,
                            node.config.configStateDbName,
                            node.config)
    node.ledgerManager.addLedger(TOKEN_LEDGER_ID, ledger)
    node.on_new_ledger_added(TOKEN_LEDGER_ID)
    node.states[TOKEN_LEDGER_ID] = state
    node.clientAuthNr.register_authenticator(token_authnr)
    return node
