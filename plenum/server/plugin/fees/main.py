from plenum.common.constants import DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID, \
    PRE_DYNAMIC_VALIDATION, PRE_REQUEST_APPLICATION
from plenum.server.plugin.fees.client_authnr import FeesAuthNr
from plenum.server.plugin.fees.static_fee_req_handler import StaticFeesReqHandler
from plenum.server.plugin.token import TOKEN_LEDGER_ID
from plenum.server.plugin.token.client_authnr import TokenAuthNr


def update_node_obj(node):
    if 'token' not in node.config.ENABLED_PLUGINS:
        raise ModuleNotFoundError('token plugin should be enabled') # noqa
    token_authnr = node.clientAuthNr.get_authnr_by_type(TokenAuthNr)
    if not token_authnr:
        raise ModuleNotFoundError('token plugin should be loaded, ' # noqa
                                  'authenticator not found')
    token_req_handler = node.get_req_handler(ledger_id=TOKEN_LEDGER_ID)
    if not token_req_handler:
        raise ModuleNotFoundError('token plugin should be loaded, request ' # noqa
                                  'handler not found')
    utxo_cache = token_req_handler.utxo_cache
    fees_authnr = FeesAuthNr(node.getState(DOMAIN_LEDGER_ID), token_authnr)
    fees_req_handler = StaticFeesReqHandler(node.configLedger,
                                            node.getState(CONFIG_LEDGER_ID),
                                            utxo_cache,
                                            node.getState(DOMAIN_LEDGER_ID))
    node.clientAuthNr.register_authenticator(fees_authnr)
    node.register_req_handler(CONFIG_LEDGER_ID, fees_req_handler)
    node.register_hook(PRE_DYNAMIC_VALIDATION, fees_req_handler.can_pay_fees)
    node.register_hook(PRE_REQUEST_APPLICATION, fees_req_handler.deduct_fees)
