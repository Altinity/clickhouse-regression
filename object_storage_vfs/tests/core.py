#!/usr/bin/env python3
from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *

# RQ_SRS_038_DiskObjectStorageVFS_Core_Delete
# RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel
# RQ_SRS_038_DiskObjectStorageVFS_Core_AddReplica
# RQ_SRS_038_DiskObjectStorageVFS_Core_DropReplica
# RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication


@TestFeature
@Name("core")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
