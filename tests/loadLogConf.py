import logging.config
import json
from importlib import reload


def loadLogConf(loggingReload=False):
    if loggingReload:
        logging.shutdown()
        reload(logging)

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LEVELV_NUM):  # pragma: no cover
            self._log(TRACE_LEVELV_NUM, message, args, **kws)  # pragma: no cover

    # Add TRACE logging level
    # Before loading logging configuration
    TRACE_LEVELV_NUM = 5
    logging.addLevelName(TRACE_LEVELV_NUM, 'TRACE')
    logging.Logger.trace = trace

    with open('./tests/logconfig.json', 'r') as f:
        log_cfg = json.load(f)
    logging.config.dictConfig(log_cfg)
