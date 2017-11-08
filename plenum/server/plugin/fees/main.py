from plenum.common.constants import DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID, \
    POST_DYNAMIC_VALIDATION, POST_REQUEST_APPLICATION, POST_SIG_VERIFICATION, \
    PRE_REQUEST_APPLICATION, POST_REQUEST_COMMIT, CREATE_PPR, CREATE_PR, \
    CREATE_ORD, RECV_CM, RECV_PPR
from plenum.server.plugin.fees.client_authnr import FeesAuthNr
from plenum.server.plugin.fees.static_fee_req_handler import StaticFeesReqHandler
from plenum.server.plugin.fees.three_phase_commit_handling import \
    ThreePhaseCommitHandler
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
    token_ledger = token_req_handler.ledger
    token_state = token_req_handler.state
    utxo_cache = token_req_handler.utxo_cache
    fees_authnr = FeesAuthNr(node.getState(DOMAIN_LEDGER_ID), token_authnr)
    fees_req_handler = StaticFeesReqHandler(node.configLedger,
                                            node.getState(CONFIG_LEDGER_ID),
                                            token_ledger,
                                            token_state,
                                            utxo_cache,
                                            node.getState(DOMAIN_LEDGER_ID))
    node.clientAuthNr.register_authenticator(fees_authnr)
    node.register_req_handler(CONFIG_LEDGER_ID, fees_req_handler)
    node.register_hook(POST_SIG_VERIFICATION, fees_req_handler.verify_signature)
    node.register_hook(POST_DYNAMIC_VALIDATION, fees_req_handler.can_pay_fees)
    node.register_hook(POST_REQUEST_APPLICATION, fees_req_handler.deduct_fees)
    node.register_hook(POST_REQUEST_COMMIT, fees_req_handler.commit_fee_txns)

    three_pc_handler = ThreePhaseCommitHandler(node.master_replica)
    node.master_replica.register_hook(CREATE_PPR,
                                      three_pc_handler.add_to_pre_prepare)
    node.master_replica.register_hook(CREATE_PR,
                                      three_pc_handler.add_to_prepare)
    node.master_replica.register_hook(CREATE_ORD,
                                      three_pc_handler.add_to_ordered)
    node.master_replica.register_hook(RECV_PPR,
                                      three_pc_handler.check_recvd_pre_prepare)
    node.master_replica.register_hook(RECV_CM,
                                      three_pc_handler.check_recvd_prepare)