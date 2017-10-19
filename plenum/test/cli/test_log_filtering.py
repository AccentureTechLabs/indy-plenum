import types

from plenum.test.cli.helper import checkRequest
from plenum.test.helper import waitForSufficientRepliesForRequests


def testLogFiltering(cli, validNodeNames, createAllNodes):
    msg = '{"amount": 20, "type": "buy"}'
    client, wallet = checkRequest(cli, msg)

    x = client.handleOneNodeMsg

    def handleOneNodeMsg(self, wrappedMsg, excludeFromCli=None):
        return x(wrappedMsg, excludeFromCli=True)

    client.handleOneNodeMsg = types.MethodType(handleOneNodeMsg, client)
    client.nodestack.msgHandler = client.handleOneNodeMsg
    msg = '{"amount": 30, "type": "buy"}'
    cli.enterCmd('client {} send {}'.format(client.name, msg))

    lastRequestId = client.reqRepStore.lastReqId
    waitForSufficientRepliesForRequests(cli.looper, client,
                                        requestIds=[lastRequestId])

    assert "got msg from node" not in cli.lastCmdOutput
