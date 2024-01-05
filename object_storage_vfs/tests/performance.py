#!/usr/bin/env python3
from testflows.core import *

from s3.tests.zero_copy_replication import (
    performance_insert,
    performance_select,
    performance_alter,
)

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestFeature
@Name("performance")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("1.0"))
def feature(self):
    self.context.zero_copy_replication_settings = {"allow_object_storage_vfs": "1"}

    with Given("I have S3 disks configured"):
        s3_config()

    Scenario(run=performance_insert)
    Scenario(run=performance_select)
    Scenario(run=performance_alter)
