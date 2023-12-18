#!/usr/bin/env python3
from testflows.core import *

from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_IncompatibleSettings("1.0"))
def incompatible_settings(self):
    pass


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_PreservesData("1.0"))
def data_preservation(self):
    pass


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Migration("1.0"))
def migration(self):
    pass


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_DeleteInParallel("1.0"))
def parallel_delete(self):
    pass


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_SharedSettings("1.0"))
def shared_settings(self):
    pass


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("1.0"))
def performance(self):
    pass


@TestOutline(Feature)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def outline(self):
    pass
