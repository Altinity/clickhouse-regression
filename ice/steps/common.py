from testflows.core import *

from helpers.common import getuid


def sanitize(s):
    for ch in "(),'= ":
        s = s.replace(ch, "_")
    return s


def generate_database_name(datatype):
    return f"iceberg_db_{sanitize(datatype.name.lower())}_{getuid()}"
