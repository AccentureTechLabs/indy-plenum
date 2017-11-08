from plenum.common.util import updateNamedTuple


class ThreePhaseCommitHandler:
    def __init__(self, master_replica):
        self.master_replica = master_replica

    def add_to_pre_prepare(self, pre_prepare):
        # TODO:
        pre_prepare = updateNamedTuple(pre_prepare)
        return pre_prepare

    def add_to_prepare(self, prepare):
        # TODO:
        prepare = updateNamedTuple(prepare)
        return prepare

    def add_to_commit(self, commit):
        # TODO:
        return commit

    def add_to_ordered(self, ordered):
        # TODO:
        ordered = updateNamedTuple(ordered)
        return ordered

    def check_recvd_pre_prepare(self, pre_prepare):
        # TODO:
        return

    def check_recvd_prepare(self, prepare):
        # TODO:
        return

    def check_recvd_commit(self, commit):
        # TODO:
        return
