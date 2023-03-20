import time
import random
from helpers.common import getuid
from testflows.core import *
from helpers.common import create_xml_config_content, add_config
from helpers.common import getuid, instrument_clickhouse_server_log

insert_values = (
    " ('data1', 1, 0),"
    " ('data1', 2, 0),"
    " ('data1', 3, 0),"
    " ('data1', 3, 0),"
    " ('data1', 1, 1),"
    " ('data1', 2, 1),"
    " ('data2', 1, 0),"
    " ('data2', 2, 0),"
    " ('data2', 3, 0),"
    " ('data2', 3, 1),"
    " ('data2', 1, 1),"
    " ('data2', 2, 1),"
    " ('data3', 1, 0),"
    " ('data3', 2, 0),"
    " ('data3', 3, 0),"
    " ('data3', 3, 1),"
    " ('data3', 1, 1),"
    " ('data3', 2, 1)"
)
