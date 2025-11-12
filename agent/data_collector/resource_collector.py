from agent.data_collector.data_collector import DataCollector
from agent.monitor.resource import ResourceMonitor

class ResourceCollector(DataCollector):
    """
    ResourceCollector collects the resource usage of the node.
    """

    def __init__(self):
        super().__init__()
        self._monitor = ResourceMonitor()

    def collect_data(self) -> object:
        self._monitor.report_resource()
        return None

    def is_enabled(self) -> bool:
        return True