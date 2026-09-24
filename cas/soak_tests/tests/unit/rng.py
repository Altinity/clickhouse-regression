from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import seeded_stream, splitmix64


@TestScenario
@Name("splitmix64 is deterministic and 64-bit")
def splitmix64_is_deterministic_and_64bit(self):
    with When("I hash 0 twice"):
        a = splitmix64(0)
        b = splitmix64(0)
    with Then("the values match, stay in 64 bits, and differ for other seeds"):
        assert a == b, error()
        assert 0 <= a < 2**64, error()
        assert splitmix64(1) != splitmix64(2), error()


@TestScenario
@Name("splitmix64 known vector")
def splitmix64_known_vector(self):
    with Then("seed 0 matches the SplitMix64 first output"):
        assert splitmix64(0) == 16294208416658607535, error()


@TestScenario
@Name("seeded stream is reproducible")
def seeded_stream_reproducible(self):
    with Then("the same seed yields the same stream"):
        assert list(seeded_stream(42, 5)) == list(seeded_stream(42, 5)), error()
        assert list(seeded_stream(42, 5)) != list(seeded_stream(43, 5)), error()


@TestFeature
@Name("rng")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
