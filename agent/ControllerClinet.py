import importlib
import os
import threading
import time

from abc import ABC, abstractmethod
from typing import Dict, Optional

from common.singleton import Singleton
from common import comm

import requests

from agent.data_collector.constants import CollectedNodeType
from common.constants import BasicClass
from util import env_util
from util.comm_util import find_free_port
from common.log import default_logger as logger


#OPTIMIZE: HTTPsClinet

class ControllerClinet(Singleton, ABC):
    """ControllerClient provides some APIs connect with the conntroller 
    service via http call

    Args:
        master_addr: the master address
        node_id (int), the unique and ordered node ID assigned by autoRL.
        node_type: the job type of node contains "TRAIN_NODE", "INFER_NODE" and "COLOC_NODE".

        timeout (int): the timeout second of requests.
    """
    _instance_lock = threading.Lock()

    def __init__(self, master_addr: str, node_id: int, node_type: CollectedNodeType, timeout: int = 10):
        logger.info(
            f"ControllerClient initialized with master_addr: 
            {master_addr}, node_id: {node_id}, node_type: 
            {node_type}, timeout: {timeout}"
        )
        self._timeout = timeout
        self._master_addr = master_addr
        self._node_id = node_id
        self._node_type = node_type
        self._node_ip = env_util.get_node_ip()
        self._worker_local_process_id = env_util.get_worker_local_process_id()
        self._ddp_server_port = find_free_port()

    @retry()
    @abstractmethod
    def _report(self, mssage:comm.Message):
        """Report the message to the controller service."""
        pass

    @retry()
    @abstractmethod
    def _get(self, message:comm.Message):
        """Get the message from the controller service."""
        pass

    #TODO: add more APIs here

class HttpControllerClient(ControllerClinet):
    def __init__(self, 
                 master_addr: str, 
                 node_id: int, 
                 node_type: CollectedNodeType, 
                 timeout: int = 10
    ):
        super(HttpControllerClient, self).__init__(
            master_addr, node_id, node_type, timeout
        )
    
    def _get_http_request_url(self, path: str) -> str:
        return "http://" + self._master_addr + path

    @retry()
    def _report(self, message: comm.Message):
        with requests.post(
            self._get_http_request_url("/report"),
            json=self._gen_request(message).to_json(),
        ) as response:
            if response.status_code != 200:
                error_msg = f"Failed to report master with http request: {type(message)}."
                raise RuntimeError(error_msg)
            response_data: BaseResponse = comm.deserialize_message(
                response.content
            )
            return response_data

    @retry()
    def _get(self, message: comm.Message):
        with requests.post(
            self._get_http_request_url("/get"),
            json=self._gen_request(message).to_json(),
        ) as response:
            if response.status_code != 200:
                error_msg = f"Failed to get from master with http request: {type(message)}."
                raise RuntimeError(error_msg)
            response_data: BaseResponse = comm.deserialize_message(
                response.content
            )
            return comm.deserialize_message(response_data.data)
        