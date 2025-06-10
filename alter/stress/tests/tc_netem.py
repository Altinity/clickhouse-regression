#!/usr/bin/env python3
"""
The test steps in this module use tc-netem to apply adverse
network conditions to outgoing packets on a given container.

https://www.man7.org/linux/man-pages/man8/tc-netem.8.html
https://www.man7.org/linux/man-pages/man8/tc.8.html
"""

import time

from testflows.core import *
from testflows.asserts import error

DISTRIBUTIONS = ["uniform", "normal", "pareto", "paretonormal"]


@TestStep
def run_netem(self, node, device, rule):
    """Run a netem rule, then clean it up."""
    cmd = f"tc qdisc add dev {device} root netem {rule}"

    try:
        node.command(cmd, exitcode=0)

        yield

    finally:
        node.command(f"tc qdisc del dev {device} root netem", exitcode=0)


@TestStep(Given)
@Name("packet delay")
def network_packet_delay(
    self,
    node,
    delay_ms=15,
    delay_jitter=5,
    correlation=25,
    distribution="paretonormal",
    device="eth0",
):
    """Apply a randomized delay to network packets."""
    rule = f"delay {delay_ms}ms {delay_jitter}ms {correlation}% distribution {distribution}"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("packet loss")
def network_packet_loss(
    self,
    node,
    percent_loss=25,
    correlation=50,
    device="eth0",
):
    """Drop a certain percentage of network packets."""
    rule = f"loss {percent_loss}% {correlation}%"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("burst loss")
def network_packet_loss_gemodel(
    self,
    node,
    interruption_probability=5,
    recovery_probability=70,
    percent_loss_after_interruption=100,
    percent_loss_after_recovery=5,
    device="eth0",
):
    """
    Create burst losses with the Gilbert-Elliott loss model.
    Switches between good (recovery) and lossy (interruption) states.
    http://www.voiptroubleshooter.com/indepth/burstloss.html

    The average length in packets of the interruption sequence
    is given by: 1/(recovery_probability/100)
    """
    rule = f"loss gemodel {interruption_probability} {recovery_probability} {percent_loss_after_interruption} {percent_loss_after_recovery}"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("packet corruption")
def network_packet_corruption(
    self,
    node,
    percent_corrupt=10,
    correlation=25,
    device="eth0",
):
    """Corrupt a certain percentage of network packets."""
    rule = f"corrupt {percent_corrupt}% {correlation}%"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("packet duplication")
def network_packet_duplication(
    self,
    node,
    percent_duplicated=20,
    correlation=25,
    device="eth0",
):
    """Duplicate a certain percentage of network packets."""
    rule = f"duplicate {percent_duplicated}% {correlation}%"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("packet reordering")
def network_packet_reordering(
    self,
    node,
    delay_ms=100,
    delay_jitter=20,
    percent_reordered=90,
    correlation=50,
    device="eth0",
):
    """Delay network packets, releasing a certain percentage of them early."""
    rule = f"delay {delay_ms}ms {delay_jitter}ms reorder {percent_reordered}% {correlation}%"
    return run_netem(node=node, device=device, rule=rule)


@TestStep(Given)
@Name("packet rate limit")
def network_packet_rate_limit(
    self,
    node,
    rate_mbit=20,
    packet_overhead_bytes=0,
    device="eth0",
):
    """Rate limit network packets."""
    rule = f"rate {rate_mbit}mbit {packet_overhead_bytes}"
    return run_netem(node=node, device=device, rule=rule)
