"""ClickHouse column list / ``PARTITION BY`` -> PyIceberg ``Schema`` + ``PartitionSpec``.

The generic export-partition modules express destinations as CH DDL strings
(``columns="id Int64, year Int32"``, ``partition_by="year"``). In ``no_catalog``
mode those strings go straight into ``CREATE TABLE ... ENGINE = IcebergS3(...)``
and ClickHouse builds the Iceberg schema server-side from ``getIcebergType`` in
``Storages/ObjectStorage/DataLakes/Iceberg/Utils.cpp``.

In Ice / Glue mode the Iceberg table has to pre-exist in the external catalog
before ClickHouse can point a ``DataLakeCatalog`` database at it (catalog-
backed databases are read-only for DDL on the CH side). We therefore need to
reproduce the same CH -> Iceberg mapping on the Python side so that
``catalog.create_table(schema=..., partition_spec=...)`` materialises the
table, and the subsequent ``EXPORT PARTITION`` lines up field-for-field with
what CH would have written.

Two entry points:

* :func:`ch_columns_to_pyiceberg_schema` — ``"id Int64, year Int32"`` ->
  ``Schema(NestedField(1, "id", LongType(), required=True), ...)``.
* :func:`ch_partition_by_to_pyiceberg_spec` — ``"toYearNumSinceEpoch(event_date)"``
  -> ``PartitionSpec(PartitionField(source_id=..., transform=YearTransform(), ...))``.

Coverage matches what the suite actually uses today. Unsupported inputs raise
:class:`UnsupportedCHTypeError` / :class:`UnsupportedCHPartitionExprError` so
the dispatcher can turn them into descriptive ``skip()`` calls.

The field-id assignment follows Iceberg's convention of monotonically
increasing ids across the whole schema (nested fields included). We also
track a per-column map of ``top-level column name -> Iceberg field id`` so
:func:`ch_partition_by_to_pyiceberg_spec` can look up the ``source_id`` each
partition transform needs without re-parsing the schema.
"""

from dataclasses import dataclass

from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema
from pyiceberg.transforms import (
    BucketTransform,
    DayTransform,
    HourTransform,
    IdentityTransform,
    MonthTransform,
    Transform,
    TruncateTransform,
    YearTransform,
)
from pyiceberg.types import (
    DateType,
    DoubleType,
    FloatType,
    IntegerType,
    ListType,
    LongType,
    MapType,
    NestedField,
    StringType,
    StructType,
    TimestampType,
    UUIDType,
)


# --------------------------------------------------------------------------
# Public exceptions — caller catches these to turn failures into ``skip()``.
# --------------------------------------------------------------------------


class UnsupportedCHTypeError(NotImplementedError):
    """Raised when a ClickHouse type has no translator mapping.

    The message includes the exact type fragment that failed so scenarios
    can include it verbatim in their ``skip()`` reason.
    """


class UnsupportedCHPartitionExprError(NotImplementedError):
    """Raised when a ``PARTITION BY`` expression has no translator mapping."""


# --------------------------------------------------------------------------
# Tokenisation helpers — CH type strings contain balanced parentheses and
# commas, so naive ``str.split(',')`` can't be used. Both entry points feed
# their input through :func:`_split_top_level` which only splits at commas
# that sit at parenthesis depth 0.
# --------------------------------------------------------------------------


def _split_top_level(text, separator=","):
    """Split ``text`` on ``separator`` occurrences that are outside any
    matched ``(...)`` pair.

    Used for "list of columns" and "list of type arguments". The result
    strips whitespace around every piece but preserves whitespace inside
    nested type expressions.
    """
    parts = []
    depth = 0
    current = []
    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == separator and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _strip_outer_parens(text):
    """If ``text`` is entirely wrapped in a single ``(...)`` pair, return the
    inner text. Otherwise return ``text`` unchanged.

    ``(year, region)`` -> ``year, region``; ``foo(a), bar(b)`` stays put.
    """
    text = text.strip()
    if not text.startswith("(") or not text.endswith(")"):
        return text
    depth = 0
    for index, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and index != len(text) - 1:
                return text
    return text[1:-1].strip()


def _split_head_and_args(text):
    """Split ``"Foo(bar, baz)"`` into ``("Foo", "bar, baz")``.

    Returns ``(text, None)`` when there is no top-level ``(...)`` suffix, so
    callers can distinguish a primitive type from a parameterised one.
    """
    text = text.strip()
    open_paren = text.find("(")
    if open_paren == -1 or not text.endswith(")"):
        return text, None
    head = text[:open_paren].strip()
    body = text[open_paren + 1 : -1].strip()
    return head, body


# --------------------------------------------------------------------------
# Type translation.
# --------------------------------------------------------------------------


@dataclass
class _IdCounter:
    """Monotonic counter for Iceberg field ids.

    The Iceberg spec requires every field (top-level *and* nested) to have a
    unique id. We start at 1 (id 0 is reserved for the top-level schema
    itself in some implementations) and hand out ids in source order.
    """

    next_id: int = 1

    def take(self):
        value = self.next_id
        self.next_id += 1
        return value


# CH type name (normalised lower-case) -> Iceberg primitive factory.
#
# UInt32 is mapped to ``IntegerType`` deliberately: CH's ``Utils.cpp``
# ``getIcebergType`` also maps it to Iceberg ``int`` (32-bit signed), even
# though that truncates values above 2^31-1. ``datatypes.py`` covers this
# intentionally via ``accepted: UInt32``.
#
# Int16 / UInt16 go to ``IntegerType`` too — Iceberg has no native 16-bit
# integer, same as CH's own mapping.
_PRIMITIVE_FACTORIES = {
    "int16": IntegerType,
    "uint16": IntegerType,
    "int32": IntegerType,
    "uint32": IntegerType,
    "int64": LongType,
    "uint64": LongType,
    "float32": FloatType,
    "float64": DoubleType,
    "date": DateType,
    "date32": DateType,
    "datetime": TimestampType,
    "string": StringType,
    "uuid": UUIDType,
}


# Types CH deliberately rejects in ``getIcebergType``. We keep the set
# explicit rather than relying on a fall-through so the error message can
# point at the specific CH type.
_CH_REJECTED_PRIMITIVES = {
    "int8",
    "uint8",
    "bool",
    "boolean",
}


def _translate_primitive(head):
    """Return an Iceberg primitive type for a bare CH type name.

    Raises :class:`UnsupportedCHTypeError` for every type CH itself refuses
    in ``getIcebergType``, for the parameterised primitives Iceberg has no
    equivalent for (``FixedString``, ``Decimal``, ``Enum8/16``), and for
    ``LowCardinality`` wrappers.
    """
    key = head.lower()
    if key in _PRIMITIVE_FACTORIES:
        return _PRIMITIVE_FACTORIES[key]()
    if key in _CH_REJECTED_PRIMITIVES:
        raise UnsupportedCHTypeError(
            f"CH type {head!r} is rejected by getIcebergType; "
            f"scenarios exercising it should stay in no_catalog mode"
        )
    raise UnsupportedCHTypeError(f"CH primitive type {head!r} has no Iceberg mapping")


def _translate_type(text, ids):
    """Translate a CH type fragment into an ``(IcebergType, required)`` pair.

    ``required`` follows CH's ``Utils.cpp`` conventions:

    * ``Nullable(T)`` -> ``required=False`` on the inner type.
    * ``Array(T)`` top-level -> ``required=False`` on the list itself (that
      matches the ``Array(T) list non-required`` row of the table in
      ``datatypes.py``).
    * every other primitive / compound -> ``required=True``.

    ``ids`` is an :class:`_IdCounter`; nested fields draw ids from the same
    counter as the surrounding schema so the whole tree is consistent.
    """
    head, body = _split_head_and_args(text)

    if body is None:
        return _translate_primitive(head), True

    key = head.lower()

    if key == "nullable":
        inner_type, _ = _translate_type(body, ids)
        return inner_type, False

    if key == "lowcardinality":
        raise UnsupportedCHTypeError(
            "LowCardinality(T) is not handled by getIcebergType; "
            "scenarios exercising it should stay in no_catalog mode"
        )

    if key == "fixedstring":
        raise UnsupportedCHTypeError(
            "FixedString(N) has no Iceberg mapping in getIcebergType"
        )

    if key == "decimal":
        raise UnsupportedCHTypeError(
            "Decimal(P, S) is not handled by getIcebergType in CH even though "
            "Iceberg has a native ``decimal`` type"
        )

    if key in ("enum8", "enum16"):
        raise UnsupportedCHTypeError(
            f"{head} has no Iceberg mapping in getIcebergType"
        )

    if key == "datetime64":
        # ``DateTime64(p)`` -> Iceberg ``timestamp``. Precision is irrelevant
        # on the translator side (Iceberg stores microseconds as a fixed
        # 64-bit value) and CH's ``getIcebergType`` maps every
        # ``DateTime64(p)`` to the same ``timestamp`` type.
        return TimestampType(), True

    if key == "array":
        element_type, _ = _translate_type(body, ids)
        element_id = ids.take()
        # ``Array(T)`` -> Iceberg ``list<T>`` with element_required=True.
        # The list *field* itself is reported non-required in the
        # ``datatypes.py`` mapping table; required=False is applied at the
        # NestedField layer in ``ch_columns_to_pyiceberg_schema`` below.
        return ListType(
            element_id=element_id,
            element_type=element_type,
            element_required=True,
        ), False

    if key == "map":
        # ``Map(K, V)`` requires exactly two top-level type args.
        args = _split_top_level(body)
        if len(args) != 2:
            raise UnsupportedCHTypeError(
                f"Map requires exactly two type args, got {text!r}"
            )
        key_type, _ = _translate_type(args[0], ids)
        value_type, _ = _translate_type(args[1], ids)
        key_id = ids.take()
        value_id = ids.take()
        return MapType(
            key_id=key_id,
            key_type=key_type,
            value_id=value_id,
            value_type=value_type,
            value_required=True,
        ), True

    if key == "tuple":
        # ``Tuple(x Int32, y String)`` -> ``StructType([NestedField(...), ...])``.
        # Each tuple element is ``<name> <type>`` at top level. Anonymous
        # tuples (``Tuple(Int32, String)`` with no per-element name) are
        # allowed by CH but Iceberg requires a name per struct field; we
        # fall back to ``f"_{index}"`` which matches how CH's own
        # ``getIcebergType`` invents struct field names.
        fields = []
        for index, element in enumerate(_split_top_level(body)):
            head_inner, body_inner = _split_head_and_args(element)
            # ``x Int32`` is not a parameterised type — it's a "name type"
            # pair separated by whitespace.
            split = element.split(None, 1)
            if len(split) == 2 and (body_inner is None or head_inner != element):
                name, type_text = split[0], split[1]
            else:
                name = f"_{index}"
                type_text = element
            inner_type, inner_required = _translate_type(type_text, ids)
            fields.append(
                NestedField(
                    field_id=ids.take(),
                    name=name,
                    field_type=inner_type,
                    required=inner_required,
                )
            )
        return StructType(*fields), True

    raise UnsupportedCHTypeError(f"CH type {text!r} has no Iceberg mapping")


# --------------------------------------------------------------------------
# Public schema entry point.
# --------------------------------------------------------------------------


def ch_columns_to_pyiceberg_schema(columns):
    """Translate a CH column list string into an Iceberg :class:`Schema`.

    ``columns`` is the same string that would appear inside the ``CREATE
    TABLE (...)`` body: a top-level comma-separated list of ``"<name>
    <type>"`` pairs (e.g. ``"id Int64, year Int32, v Nullable(Int64)"``).

    Returns ``(schema, column_id_map)`` where:

    * ``schema`` is a :class:`pyiceberg.schema.Schema` with monotonically
      assigned field ids.
    * ``column_id_map`` maps top-level column *name* -> Iceberg field id,
      for use by :func:`ch_partition_by_to_pyiceberg_spec`.

    Every fragment is translated through :func:`_translate_type`; any
    unmappable type propagates as :class:`UnsupportedCHTypeError` so the
    caller can skip with a specific reason.
    """
    ids = _IdCounter()
    fields = []
    column_id_map = {}
    for entry in _split_top_level(columns):
        name, _, type_text = entry.partition(" ")
        name = name.strip()
        type_text = type_text.strip()
        if not name or not type_text:
            raise UnsupportedCHTypeError(
                f"Column fragment {entry!r} is not '<name> <type>'"
            )
        iceberg_type, required = _translate_type(type_text, ids)
        field_id = ids.take()
        column_id_map[name] = field_id
        fields.append(
            NestedField(
                field_id=field_id,
                name=name,
                field_type=iceberg_type,
                required=required,
            )
        )
    return Schema(*fields), column_id_map


# --------------------------------------------------------------------------
# Partition-by translation.
# --------------------------------------------------------------------------


# CH partition-by function name -> (transform factory, expected arg count).
#
# The two-arg transforms (``icebergBucket(N, col)`` / ``icebergTruncate(N,
# col)``) have CH's ``N`` as their first argument; the transform factory
# takes ``N`` as its own constructor argument, which is why the entries
# below capture ``N`` via a lambda.
_TRANSFORM_FACTORIES = {
    "toyearnumsinceepoch": (lambda: YearTransform(), 1),
    "tomonthnumsinceepoch": (lambda: MonthTransform(), 1),
    "torelativedaynum": (lambda: DayTransform(), 1),
    "torelativehournum": (lambda: HourTransform(), 1),
    # Two-arg transforms are handled separately so we can parse the N.
}


def _parse_transform_expr(expr, column_id_map):
    """Parse a single transform expression into ``(source_column, transform)``.

    Handles:

    * bare identifier -> ``IdentityTransform``;
    * ``toYearNumSinceEpoch(col)`` / ``toMonthNumSinceEpoch(col)`` /
      ``toRelativeDayNum(col)`` / ``toRelativeHourNum(col)``;
    * ``icebergTruncate(N, col)`` / ``icebergBucket(N, col)``.

    Everything else (``intDiv(year, 100)``, ``cityHash64(x) % N`` etc.)
    raises :class:`UnsupportedCHPartitionExprError`.
    """
    head, body = _split_head_and_args(expr)

    if body is None:
        column = head
        if column not in column_id_map:
            raise UnsupportedCHPartitionExprError(
                f"partition column {column!r} is not in the schema"
            )
        return column, IdentityTransform()

    key = head.lower()

    if key in _TRANSFORM_FACTORIES:
        factory, expected_args = _TRANSFORM_FACTORIES[key]
        args = _split_top_level(body)
        if len(args) != expected_args:
            raise UnsupportedCHPartitionExprError(
                f"{head} expects {expected_args} arg(s), got {expr!r}"
            )
        column = args[0].strip()
        if column not in column_id_map:
            raise UnsupportedCHPartitionExprError(
                f"partition column {column!r} is not in the schema"
            )
        return column, factory()

    if key in ("icebergbucket", "icebergtruncate"):
        args = _split_top_level(body)
        if len(args) != 2:
            raise UnsupportedCHPartitionExprError(
                f"{head} expects (N, col), got {expr!r}"
            )
        try:
            width = int(args[0].strip())
        except ValueError:
            raise UnsupportedCHPartitionExprError(
                f"{head} width must be an integer literal, got {args[0]!r}"
            )
        column = args[1].strip()
        if column not in column_id_map:
            raise UnsupportedCHPartitionExprError(
                f"partition column {column!r} is not in the schema"
            )
        transform = (
            BucketTransform(width) if key == "icebergbucket" else TruncateTransform(width)
        )
        return column, transform

    raise UnsupportedCHPartitionExprError(
        f"partition expression {expr!r} has no Iceberg transform mapping"
    )


def ch_partition_by_to_pyiceberg_spec(partition_by, column_id_map):
    """Translate a CH ``PARTITION BY`` string into a :class:`PartitionSpec`.

    Accepts the shapes actually used in the export-partition suite:

    * empty / blank -> unpartitioned spec.
    * ``"year"`` -> single identity transform.
    * ``"(year, region)"`` -> two identity transforms, one per component.
    * ``"toYearNumSinceEpoch(event_date)"`` -> ``year(event_date)``. Same for
      ``toMonthNumSinceEpoch`` / ``toRelativeDayNum`` / ``toRelativeHourNum``.
    * ``"icebergTruncate(4, category)"`` / ``"icebergBucket(8, user_id)"`` ->
      the corresponding parameterised transform.
    * Tuples of the above: ``"(toYearNumSinceEpoch(event_date),
      icebergBucket(16, user_id))"``.

    Unmapped expressions raise :class:`UnsupportedCHPartitionExprError`.

    ``column_id_map`` is the second return value of
    :func:`ch_columns_to_pyiceberg_schema` — we need it to look up each
    transform's ``source_id``.

    Iceberg's ``PartitionField.field_id`` space starts at 1000 by
    convention (the low range is reserved for schema field ids); we follow
    that convention so concurrent tests don't accidentally collide.
    """
    partition_by = (partition_by or "").strip()
    if not partition_by:
        return PartitionSpec()

    partition_by = _strip_outer_parens(partition_by)
    exprs = _split_top_level(partition_by)

    # Iceberg convention: partition field ids live in ``[1000, 2000)``.
    next_partition_id = 1000
    fields = []
    for expr in exprs:
        column, transform = _parse_transform_expr(expr, column_id_map)
        source_id = column_id_map[column]
        name = _partition_field_name(column, transform)
        fields.append(
            PartitionField(
                source_id=source_id,
                field_id=next_partition_id,
                transform=transform,
                name=name,
            )
        )
        next_partition_id += 1
    return PartitionSpec(*fields)


def _partition_field_name(source_column, transform):
    """Return a stable partition-field name for ``(column, transform)``.

    CH's Iceberg writer derives partition-field names from the transform
    kind; we mirror that here so column names stay readable in manifest
    metadata. The mapping is intentionally terse because PyIceberg uses
    this name as the partition column label in ``table.scan().to_arrow()``
    output, and we want it to match what an Iceberg reader would see if
    CH had created the table natively.
    """
    if isinstance(transform, IdentityTransform):
        return source_column
    if isinstance(transform, YearTransform):
        return f"{source_column}_year"
    if isinstance(transform, MonthTransform):
        return f"{source_column}_month"
    if isinstance(transform, DayTransform):
        return f"{source_column}_day"
    if isinstance(transform, HourTransform):
        return f"{source_column}_hour"
    if isinstance(transform, BucketTransform):
        return f"{source_column}_bucket_{transform.num_buckets}"
    if isinstance(transform, TruncateTransform):
        return f"{source_column}_trunc_{transform.width}"
    # Unreachable today, kept for future transforms.
    return f"{source_column}_{type(transform).__name__}"
