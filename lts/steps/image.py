"""ClickHouse image reference helpers shared by the LTS sub-suites."""

import re


def split_image(image):
    """Split a Docker image reference into ``(name, tag, digest)``.

    ``registry.example:5000/team/clickhouse`` has no tag: a ``:`` only starts
    a tag when it comes after the last ``/``. ``tag`` and ``digest`` are
    ``None`` when absent.
    """
    name, _, digest = image.partition("@")
    tag = None
    last = name.rsplit("/", 1)[-1]
    if ":" in last:
        name, tag = name.rsplit(":", 1)
    return name, tag, digest or None


def clickhouse_version_from_image(image):
    """Return the ClickHouse version encoded in an image tag, or ``None``.

    ``altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest`` gives
    ``26.3.13.10001``. Moving or non-numeric tags such as ``latest`` or
    ``head`` give ``None``, because they say nothing about the version.
    """
    _, tag, _ = split_image(image)
    if not tag:
        return None
    if tag.startswith("0-"):
        tag = tag[2:]
    match = re.match(r"(\d+\.\d+(?:\.\d+){0,2})", tag)
    return match.group(1) if match else None


def check_supported_image(image):
    """Return an error message if the LTS runners cannot use ``image``.

    The runners are built on the ClickHouse image and need its Debian/Ubuntu
    userland (``apt-get``) and ``/entrypoint.sh``, which Alpine images lack.
    """
    _, tag, _ = split_image(image)
    if tag and "alpine" in tag:
        return (
            f"{image} is an Alpine image; the LTS runners need an Ubuntu-based "
            "ClickHouse image (apt-get and /entrypoint.sh)"
        )
    return None
