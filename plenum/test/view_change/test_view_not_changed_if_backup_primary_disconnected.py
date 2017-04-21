from stp_core.loop.eventually import eventually
from plenum.test.conftest import txnPoolNodeSet, txnPoolNodesLooper
from plenum.test.helper import stopNodes, checkViewNoForNodes
from plenum.test.test_node import primaryNodeNameForInstance, nodeByName


def testViewNotChangedIfBackupPrimaryDisconnected(txnPoolNodeSet,
                                                  txnPoolNodesLooper):
    """
    View change does not occurs when master's primary is disconnected
    """

    # Setup
    nodes = txnPoolNodeSet
    looper = txnPoolNodesLooper

    viewNoBefore = checkViewNoForNodes(nodes)
    primaryNodeForBackupInstance1Before = nodeByName(
        nodes, primaryNodeNameForInstance(nodes, 1))

    # Exercise
    stopNodes([primaryNodeForBackupInstance1Before], looper)

    # Verify
    remainingNodes = set(nodes) - {primaryNodeForBackupInstance1Before}

    def assertNewPrimariesElected():
        viewNoAfter = checkViewNoForNodes(remainingNodes)
        assert viewNoBefore == viewNoAfter

    looper.run(eventually(assertNewPrimariesElected, retryWait=1, timeout=30))