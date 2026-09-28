"""Unit tests for lts.steps.image.

Run from the repository root:

    python3 -m unittest discover -s lts/steps/tests -t .
"""

import unittest

from lts.steps.image import check_supported_image, clickhouse_version_from_image, split_image


class ImageTestCase(unittest.TestCase):
    def test_split_image(self):
        cases = {
            "altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest": (
                "altinityinfra/clickhouse-server",
                "0-26.3.13.10001.altinitytest",
                None,
            ),
            "clickhouse/clickhouse-server": ("clickhouse/clickhouse-server", None, None),
            "registry.example:5000/team/clickhouse": (
                "registry.example:5000/team/clickhouse",
                None,
                None,
            ),
            "registry.example:5000/team/clickhouse:26.3": (
                "registry.example:5000/team/clickhouse",
                "26.3",
                None,
            ),
            "clickhouse/clickhouse-server@sha256:abc": (
                "clickhouse/clickhouse-server",
                None,
                "sha256:abc",
            ),
            "clickhouse/clickhouse-server:26.3@sha256:abc": (
                "clickhouse/clickhouse-server",
                "26.3",
                "sha256:abc",
            ),
        }
        for image, expected in cases.items():
            with self.subTest(image=image):
                self.assertEqual(split_image(image), expected)

    def test_clickhouse_version_from_image(self):
        cases = {
            "altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest": "26.3.13.10001",
            "altinityinfra/clickhouse-server:26.3.13.10001.altinitystable": "26.3.13.10001",
            "clickhouse/clickhouse-server:26.3": "26.3",
            "clickhouse/clickhouse-server:latest": None,
            "clickhouse/clickhouse-server:head": None,
            "clickhouse/clickhouse-server": None,
            "registry.example:5000/team/clickhouse": None,
            "clickhouse/clickhouse-server@sha256:abc": None,
        }
        for image, expected in cases.items():
            with self.subTest(image=image):
                self.assertEqual(clickhouse_version_from_image(image), expected)

    def test_alpine_is_rejected(self):
        self.assertIsNotNone(
            check_supported_image("altinityinfra/clickhouse-server:0-26.3.13.10001.altinitystable-alpine")
        )
        self.assertIsNone(
            check_supported_image("altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest")
        )


if __name__ == "__main__":
    unittest.main()
