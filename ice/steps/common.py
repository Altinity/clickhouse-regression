from testflows.core import *

from helpers.common import getuid


def generate_database_name(datatype):
    """Generate a unique database name for the given datatype."""
    return f"iceberg_db_{datatype.name.lower().replace('(', '_').replace(')', '_').replace(',', '_')}_{getuid()}"
