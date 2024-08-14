#!/usr/bin/env python3
from gettext import find
import os
import sys
from testflows.core import *
from testflows.core.name import clean

append_path(sys.path, "..")

from helpers.common import experimental_analyzer
from helpers.cluster import create_cluster, check_clickhouse_version
from helpers.argparser import argparser, CaptureClusterArgs
from aes_encryption.requirements import *

issue_18249 = "https://github.com/ClickHouse/ClickHouse/issues/18249"
issue_18250 = "https://github.com/ClickHouse/ClickHouse/issues/18250"
issue_18251 = "https://github.com/ClickHouse/ClickHouse/issues/18251"
issue_24029 = "https://github.com/ClickHouse/ClickHouse/issues/24029"
issue_39987 = "https://github.com/ClickHouse/ClickHouse/issues/39987"
issue_40826 = "https://github.com/ClickHouse/ClickHouse/issues/40826"
issue_65116 = "https://github.com/ClickHouse/ClickHouse/issues/65116"

xfails = {
    # decrypt
    "/aes encryption/decrypt/invalid parameters/null in ciphertext": [
        (Fail, issue_39987)
    ],
    # encrypt
    "encrypt/"
    + clean("invalid key or iv length for mode/mode=\"'aes-")
    + "???"
    + clean("-gcm'\", key_len=")
    + "??"
    + clean(", iv_len=12, aad=True/iv is too short"): [(Fail, "known issue")],
    "encrypt/"
    + clean("invalid key or iv length for mode/mode=\"'aes-")
    + "???"
    + clean("-gcm'\", key_len=")
    + "??"
    + clean(", iv_len=12, aad=True/iv is too long"): [(Fail, "known issue")],
    "encrypt/invalid plaintext data type/"
    + clean(
        "data_type='IPv6', value=\"toIPv6('2001:0db8:0000:85a3:0000:0000:ac1f:8001')\""
    ): [(Fail, "known issue as IPv6 is implemented as FixedString(16)")],
    # encrypt_mysql
    "encrypt_mysql/key or iv length for mode/"
    + clean("mode=\"'aes-")
    + "???"
    + clean("-ecb'\", key_len=")
    + "??"
    + clean(", iv_len=None"): [(Fail, issue_18251)],
    "encrypt_mysql/invalid parameters/iv not valid for mode": [(Fail, issue_18251)],
    "encrypt_mysql/invalid plaintext data type/"
    + clean(
        "data_type='IPv6', value=\"toIPv6('2001:0db8:0000:85a3:0000:0000:ac1f:8001')\""
    ): [(Fail, "known issue as IPv6 is implemented as FixedString(16)")],
    # decrypt_mysql
    "decrypt_mysql/key or iv length for mode/"
    + clean("mode=\"'aes-")
    + "???"
    + clean("-ecb'\", key_len=")
    + "??"
    + clean(", iv_len=None:"): [(Fail, issue_18251)],
    # compatibility
    "compatibility/insert/encrypt using materialized view/:": [(Fail, issue_18249)],
    "compatibility/insert/decrypt using materialized view/:": [(Error, issue_18249)],
    "compatibility/insert/aes encrypt mysql using materialized view/:": [
        (Fail, issue_18249)
    ],
    "compatibility/insert/aes decrypt mysql using materialized view/:": [
        (Error, issue_18249)
    ],
    "compatibility/select/decrypt unique": [(Fail, issue_18249)],
    "compatibility/mysql/:engine/decrypt/"
    + clean("mysql_datatype='TEXT'")
    + "/:": [(Fail, issue_18250)],
    "compatibility/mysql/:engine/decrypt/"
    + clean("mysql_datatype='VARCHAR(100)'")
    + "/:": [(Fail, issue_18250)],
    "compatibility/mysql/:engine/encrypt/"
    + clean("mysql_datatype='TEXT'")
    + "/:": [(Fail, issue_18250)],
    "compatibility/mysql/:engine/encrypt/"
    + clean("mysql_datatype='VARCHAR(100)'")
    + "/:": [(Fail, issue_18250)],
    # reinterpretAsFixedString for UUID stopped working
    "decrypt/decryption/mode=:datatype=UUID:": [(Fail, issue_24029)],
    "encrypt/:/mode=:datatype=UUID:": [(Fail, issue_24029)],
    "decrypt/invalid ciphertext/mode=:/"
    + clean("invalid ciphertext=reinterpretAsFixedString(toUUID")
    + ":": [(Fail, issue_24029)],
    "encrypt_mysql/encryption/mode=:datatype=UUID:": [(Fail, issue_24029)],
    "decrypt_mysql/decryption/mode=:datatype=UUID:": [(Fail, issue_24029)],
    "decrypt_mysql/invalid ciphertext/mode=:/"
    + clean("invalid ciphertext=reinterpretAsFixedString(toUUID")
    + ":": [(Fail, issue_24029)],
    # aes-128-cfb128 not supported in 22.8
    "*/:cfb128:": [(Fail, issue_40826)],
    "performance/:/:": [(Fail, issue_65116, check_clickhouse_version(">=24.4"))],
}


@TestFeature
@Name("aes encryption")
@ArgumentParser(argparser)
@Specifications(SRS_008_ClickHouse_AES_Encryption_Functions)
@Requirements(
    RQ_SRS008_AES_Functions("1.0"), RQ_SRS008_AES_Functions_DifferentModes("1.0")
)
@XFails(xfails)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """ClickHouse AES encryption functions regression module."""
    nodes = {
        "clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3"),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And(
        "I set a flag for performance suite based on the value of thread fuzzer",
        description="We don't run performance suite if the thread fuzzer is enabled",
    ):
        if not cluster.thread_fuzzer:
            flag = TE
        else:
            flag = SKIP

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    with Pool(5) as pool:
        try:
            Feature(
                run=load("aes_encryption.tests.encrypt", "feature"),
                flags=TE,
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load("aes_encryption.tests.decrypt", "feature"),
                flags=TE,
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load("aes_encryption.tests.encrypt_mysql", "feature"),
                flags=TE,
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load("aes_encryption.tests.decrypt_mysql", "feature"),
                flags=TE,
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load("aes_encryption.tests.compatibility.feature", "feature"),
                flags=TE,
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load("aes_encryption.tests.performance", "feature"),
                flags=flag,
                parallel=True,
                executor=pool,
            )
        finally:
            join()


if main():
    regression()
