# -*- coding: utf-8 -*-
import time

from testflows.core import *
from testflows.core.name import basename
from testflows.asserts import values, error, snapshot

from aes_encryption.requirements.requirements import *
from aes_encryption.tests.common import *


@TestOutline
def encrypt_decrypt_stress(
    self,
    key,
    mode=None,
    iv=None,
    aad=None,
    exitcode=0,
    step=When,
):
    """Use the encrypt and decrypt functions on a number sequence."""
    params = [key]
    if iv is not None:
        params.append(iv)
    if aad is not None:
        params.append(aad)

    sql = f"""SELECT DISTINCT toString(number) = decrypt({mode}, encrypt({mode}, toString(number), {", ".join(params)}), {", ".join(params)})
              FROM numbers_mt(1000000)"""

    return current().context.node.query(sql, step=step, exitcode=exitcode)


@TestScenario
@Requirements(RQ_SRS008_AES_Functions_Check_Performance("1.0"))
def encryption_decryption(self):
    """Check that all modes of encrypt and decrypt finish in a reasonable time."""
    key = f"{'1' * 36}"
    iv = f"{'2' * 16}"
    aad = "some random aad"

    for mode, key_len, iv_len, aad_len in modes:
        if mode == "'aes-128-ecb'":
            expected_time = 0.25
        else:
            expected_time = 0.1

        with Example(f"""mode={mode.strip("'")} iv={iv_len} aad={aad_len}"""):
            t_start = time.time()
            encrypt_decrypt_stress(
                key=f"'{key[:key_len]}'",
                mode=mode,
                iv=(None if not iv_len else f"'{iv[:iv_len]}'"),
                aad=(None if not aad_len else f"'{aad}'"),
            )
            t_elapsed = time.time() - t_start

            with Then("I check encryption time"):
                assert t_elapsed < expected_time, error()


@TestOutline
def encrypt_decrypt_mysql_stress(
    self,
    key,
    mode=None,
    iv=None,
    exitcode=0,
    step=When,
):
    """Use the aes_encrypt_mysql and aes_decrypt_mysql functions on a number sequence."""
    params = [key]
    if iv is not None:
        params.append(iv)

    sql = f"""SELECT DISTINCT toString(number) = aes_decrypt_mysql({mode}, aes_encrypt_mysql({mode}, toString(number), {", ".join(params)}), {", ".join(params)})
              FROM numbers_mt(1000000)"""

    return current().context.node.query(sql, step=step, exitcode=exitcode)


@TestScenario
@Requirements(RQ_SRS008_AES_Functions_Check_Performance("1.0"))
def encryption_decryption_mysql(self):
    """Check that all modes of aes_encrypt_mysql and aes_decrypt_mysql finish in a reasonable time."""
    key = f"{'1' * 36}"
    iv = f"{'2' * 16}"
    aad = "some random aad"

    for mode, key_len, iv_len in mysql_modes:
        if mode == "'aes-128-ecb'":
            expected_time = 0.25
        else:
            expected_time = 0.1

        with Example(f"""mode={mode.strip("'")} key={key_len} iv={iv_len}"""):
            t_start = time.time()
            encrypt_decrypt_mysql_stress(
                key=f"'{key[:key_len]}'",
                mode=mode,
                iv=(None if not iv_len else f"'{iv[:iv_len]}'"),
            )
            t_elapsed = time.time() - t_start

            with Then("I check encryption time"):
                assert t_elapsed < expected_time, error()


@TestFeature
@Name("performance")
@Requirements(RQ_SRS008_AES_Encrypt_Function("1.0"))
def feature(self, node="clickhouse1"):
    """Check the behavior of the `encrypt` function."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)