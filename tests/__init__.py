import logging
import sys
from .loadLogConf import loadLogConf


loadLogConf()

# Path to jde
sys.path.append('src')
sys.path.append('src/jde')
