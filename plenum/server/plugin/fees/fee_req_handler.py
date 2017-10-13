from abc import abstractmethod

from plenum.server.config_req_handler import ConfigReqHandler
from plenum.server.plugin.fees.constants import FEE, GET_FEES


class FeeReqHandler(ConfigReqHandler):
    @abstractmethod
    def can_pay_fees(self, request) -> bool:
        pass

    @abstractmethod
    def deduct_fees(self, request) -> bool:
        pass
