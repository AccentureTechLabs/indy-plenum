from plenum.common.constants import KeyValueStorageType


def get_config(config):
    config.tokenTransactionsFile = 'token_transactions'
    config.tokenStateStorage = KeyValueStorageType.Leveldb
    config.configStateDbName = 'token_state'
    return config
