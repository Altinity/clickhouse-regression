import random as default_random

from helpers.common import check_clickhouse_version, current


class DataType:
    def __init__(
        self,
        name,
        supports_low_cardinality=True,
        is_valid_map_key=True,
        is_numeric=True,
        is_unsigned=False,
        is_extended_precision=False,
        max=None,
        min=None,
    ):
        self.name = name
        self.supports_low_cardinality = supports_low_cardinality
        self.is_valid_map_key = is_valid_map_key
        self.is_numeric = is_numeric
        self.is_unsigned = is_unsigned
        self.is_extended_precision = is_extended_precision
        self.max = max
        self.min = min

    def max_value(self):
        return f"to{self.name}({self.max})"

    def min_value(self):
        return f"to{self.name}({self.min})"


# Ints
class Int(DataType):
    def __init__(self, name, max, min, is_unsigned=False, is_extended_precision=False):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=True,
            is_unsigned=is_unsigned,
            is_extended_precision=is_extended_precision,
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return f"to{self.name}({random.randint(self.min, self.max)})"

    def zero_or_null_value(self):
        return f"to{self.name}(0)"


class Int8(Int):
    def __init__(self):
        super().__init__("Int8", max=127, min=-128)


class Int16(Int):
    def __init__(self):
        super().__init__("Int16", max=32767, min=-32768)


class Int32(Int):
    def __init__(self):
        super().__init__("Int32", max=2147483647, min=-2147483648)


class Int64(Int):
    def __init__(self):
        super().__init__("Int64", max=9223372036854775807, min=-9223372036854775808)


class Int128(Int):
    def __init__(self):
        super().__init__(
            "Int128",
            is_extended_precision=True,
            max=170141183460469231731687303715884105727,
            min=-170141183460469231731687303715884105728,
        )


class Int256(Int):
    def __init__(self):
        super().__init__(
            "Int256",
            is_extended_precision=True,
            max=57896044618658097711785492504343953926634992332820282019728792003956564819967,
            min=-57896044618658097711785492504343953926634992332820282019728792003956564819968,
        )


# UInts
class UInt(Int):
    def __init__(self, name, max, is_extended_precision=False):
        super().__init__(
            name=name,
            max=max,
            min=0,
            is_unsigned=True,
            is_extended_precision=is_extended_precision,
        )


class UInt8(UInt):
    def __init__(self):
        super().__init__("UInt8", max=255)


class UInt16(UInt):
    def __init__(self):
        super().__init__("UInt16", max=65535)


class UInt32(UInt):
    def __init__(self):
        super().__init__("UInt32", max=4294967295)


class UInt64(UInt):
    def __init__(self):
        super().__init__("UInt64", max=18446744073709551615)


class UInt128(UInt):
    def __init__(self):
        super().__init__(
            "UInt128",
            is_extended_precision=True,
            max=340282366920938463463374607431768211455,
        )


class UInt256(UInt):
    def __init__(self):
        super().__init__(
            "UInt256",
            is_extended_precision=True,
            max=115792089237316195423570985008687907853269984665640564039457584007913129639935,
        )


# Floats
class Float(DataType):
    def __init__(self, name, max, min):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=True,
            is_valid_map_key=False,
        )

    def zero_or_null_value(self):
        return f"to{self.name}(0)"


class Float32(Float):
    def __init__(self):
        super().__init__("Float32", max="3.4028235e38", min="-3.4028235e38")

    def rand_value(self, random):
        return f"toFloat32({random.uniform(float(self.min), float(self.max))})"


class Float64(Float):
    def __init__(self):
        super().__init__(
            "Float64", max="1.7976909999999999e308", min="-1.7976909999999999e308"
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return f"toFloat64({random.uniform(-1.79769, 1.79769)}e{random.randint(0,308)})"


# Decimals
class Decimal(DataType):
    def __init__(self, name, max, min, scale, is_extended_precision=False):
        self.scale = scale
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=False,
            is_valid_map_key=False,
            is_extended_precision=is_extended_precision,
        )

    def max_value(self):
        base_type = self.name.split("(")[0]
        return f"to{base_type}({self.max}, {self.scale})"

    def min_value(self):
        base_type = self.name.split("(")[0]
        return f"to{base_type}({self.min}, {self.scale})"

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        base_type = self.name.split("(")[0]
        return f"to{base_type}({random.uniform(float(self.min), float(self.max))},{self.scale})"

    def zero_or_null_value(self):
        base_type = self.name.split("(")[0]
        return f"to{base_type}(0,{self.scale})"


class Decimal32(Decimal):
    def __init__(self, scale):
        if scale == 9:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (9 - scale) + "." + "9" * scale
        super().__init__(f"Decimal32({scale})", max=limit, min="-" + limit, scale=scale)


class Decimal64(Decimal):
    def __init__(self, scale):
        if scale == 18:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (18 - scale) + "." + "9" * scale
        super().__init__(f"Decimal64({scale})", max=limit, min="-" + limit, scale=scale)


class Decimal128(Decimal):
    def __init__(self, scale):
        if scale == 38:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (38 - scale) + "." + "9" * scale
        super().__init__(
            f"Decimal128({scale})",
            is_extended_precision=True,
            max=limit,
            min="-" + limit,
            scale=scale,
        )


class Decimal256(Decimal):
    def __init__(self, scale):
        if scale == 76:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (76 - scale) + "." + "9" * scale
        super().__init__(
            f"Decimal256({scale})",
            is_extended_precision=True,
            max=limit,
            min="-" + limit,
            scale=scale,
        )


# Date and DateTime
class Date(DataType):
    def __init__(
        self,
        name="Date",
        max="'2149-06-06'",
        min="'1970-01-01'",
        supports_low_cardinality=True,
        is_valid_map_key=True,
    ):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=supports_low_cardinality,
            is_numeric=False,
            is_unsigned=False,
            is_valid_map_key=is_valid_map_key,
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return f"to{self.name}({random.randint(1072549200, 1672549200)})"

    def zero_or_null_value(self):
        return self.min


class Date32(Date):
    def __init__(
        self,
        name="Date32",
        max="'2299-12-31'",
        min="'1900-01-01'",
        supports_low_cardinality=True,
    ):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=supports_low_cardinality,
        )


class DateTime(Date):
    def __init__(
        self,
        name="DateTime",
        max="'2106-02-07 06:28:15'",
        min="'1970-01-01 00:00:00'",
        supports_low_cardinality=True,
        is_valid_map_key=True,
    ):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=supports_low_cardinality,
            is_valid_map_key=is_valid_map_key,
        )


class DateTime64(DateTime):
    def __init__(self, precision):
        self.precision = precision
        super().__init__(
            f"DateTime64({self.precision})",
            max=(
                (
                    "'2283-11-11 23:59:59.99999999'"
                    if check_clickhouse_version("<22.8")(current())
                    else "'2299-12-31 23:59:59.99999999'"
                )
                if precision != 9
                else "'2262-04-11 23:47:16'"
            ),
            min=(
                "'1925-01-01 00:00:00.00000000'"
                if check_clickhouse_version("<22.8")(current())
                else "'1900-01-01 00:00:00.00000000'"
            ),
            supports_low_cardinality=False,
            is_valid_map_key=False,
        )

    def max_value(self):
        return f"toDateTime64({self.max},{self.precision})"

    def min_value(self):
        return f"toDateTime64({self.min},{self.precision})"

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return (
            f"toDateTime64({random.randint(1072549200, 1672549200)},{self.precision})"
        )


# Misc
class String(DataType):
    def __init__(
        self,
        name="String",
        max="'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ'",
        min="''",
    ):
        super().__init__(
            name=name,
            max=max,
            min=min,
            supports_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return (
            f"'{self.max[random.randint(1,len(self.max)-2)] * random.randint(0,100)}'"
        )

    def zero_or_null_value(self):
        return self.min


class FixedString(String):
    def __init__(self, length):
        self.length = length
        if length <= 51:
            max = (
                "'"
                + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ"[0:length]
                + "'"
            )
        else:
            max = (
                "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ"
                + "a" * (length - 51)
                + "'"
            )
        super().__init__(f"FixedString({length})", max=max)

    def max_value(self):
        return f"to{self.name[:-4]}({self.max},{self.length})"

    def min_value(self):
        return f"to{self.name[:-4]}({self.min},{self.length})"

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return f"'{self.max[random.randint(1,len(self.max)-2)] * random.randint(0,self.length)}'"


class Boolean(DataType):
    def __init__(self):
        super().__init__(
            "Bool",
            supports_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
            max="true",
            min="false",
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return "true" if random.randint(0, 1) else "false"

    def zero_or_null_value(self):
        return "false"


class UUID(DataType):
    def __init__(self):
        super().__init__(
            "UUID",
            supports_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
            max="'ffffffff-ffff-ffff-ffff-ffffffffffff'",
            min="'00000000-0000-0000-0000-000000000000'",
        )

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return f"'{hex(random.randint(0,4294967295))[2:]:>08}-{hex(random.randint(0,65535))[2:]:>04}-{hex(random.randint(0,65535))[2:]:>04}-{hex(random.randint(0,65535))[2:]:>04}-{hex(random.randint(0,281474976710655))[2:]:>012}'"

    def zero_or_null_value(self):
        return self.min


# Modifiers
class Nullable(DataType):
    def __init__(self, datatype):
        self.datatype = datatype
        super().__init__(
            f"Nullable({datatype.name})",
            supports_low_cardinality=datatype.supports_low_cardinality,
            is_valid_map_key=False,
            is_numeric=datatype.is_numeric,
            is_unsigned=datatype.is_unsigned,
            max=datatype.max,
            min=datatype.min,
        )

    def max_value(self):
        return self.datatype.max_value()

    def min_value(self):
        return self.datatype.min_value()

    def rand_value(self, random=None):
        if random is None:
            random = default_random
        return self.datatype.rand_value(random=random)

    def zero_or_null_value(self):
        return "Null"


class LowCardinality(DataType):
    def __init__(self, datatype):
        self.datatype = datatype
        super().__init__(
            f"LowCardinality({datatype.name})",
            supports_low_cardinality=False,
            is_valid_map_key=True if isinstance(datatype, String) else False,
            is_numeric=datatype.is_numeric,
            is_unsigned=datatype.is_unsigned,
            max=datatype.max,
            min=datatype.min,
        )

    def max_value(self):
        return self.datatype.max_value()

    def min_value(self):
        return self.datatype.min_value()

    def rand_value(self, random=None):
        return self.datatype.rand_value(random=random)

    def zero_or_null_value(self):
        return self.datatype.zero_or_null_value()


class Tuple(DataType):
    def __init__(
        self,
        datatypes,
    ):
        self.datatypes = datatypes
        super().__init__(
            "Tuple(" + ",".join([datatype.name for datatype in self.datatypes]) + ")",
            supports_low_cardinality=False,
            is_valid_map_key=False,
            is_numeric=False,
            is_unsigned=False,
        )

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return (
            "tuple("
            + ",".join([datatype.max_value() for datatype in self.datatypes])
            + ")"
        )

    def min_value(self):
        """Return the minimum value for the column in string format."""

        return (
            "tuple("
            + ",".join([datatype.min_value() for datatype in self.datatypes])
            + ")"
        )

    def rand_value(self, random=None):
        """Return the random value for the column in string format."""

        return (
            "tuple("
            + ",".join([datatype.rand_value(random) for datatype in self.datatypes])
            + ")"
        )

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return (
            "tuple("
            + ",".join([datatype.zero_or_null_value() for datatype in self.datatypes])
            + ")"
        )


class Map(DataType):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        super().__init__(
            "Map(" + self.key.name + "," + self.value.name + ")",
            supports_low_cardinality=False,
            is_valid_map_key=False,
            is_numeric=False,
            is_unsigned=False,
        )

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return "map(" + self.key.max_value() + "," + self.value.max_value() + ")"

    def min_value(self):
        """Return the minimum value for the column in string format."""

        return "map(" + self.key.min_value() + "," + self.value.min_value() + ")"

    def rand_value(self, random=None):
        """Return the random value for the column in string format."""

        return (
            "map("
            + self.key.rand_value(random)
            + ","
            + self.value.rand_value(random)
            + ")"
        )

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return (
            "map("
            + self.key.zero_or_null_value()
            + ","
            + self.value.zero_or_null_value()
            + ")"
        )


class Array(DataType):
    def __init__(self, datatype):
        self.datatype = datatype
        super().__init__(
            "Array(" + self.datatype.name + ")",
            supports_low_cardinality=False,
            is_valid_map_key=False,
            is_numeric=False,
            is_unsigned=False,
        )

    def max_value(self):
        """Return the maximum value for the column in string format."""

        return "[" + self.datatype.max_value() + "]"

    def min_value(self):
        """Return the minimum values for the column in string format."""

        return "[" + self.datatype.min_value() + "]"

    def rand_value(self, random=None):
        """Return the random values for the column in string format."""

        return "[" + self.datatype.rand_value(random) + "]"

    def zero_or_null_value(self):
        """Return the null or zero value for the column in string format."""

        return "[" + self.datatype.zero_or_null_value() + "]"


def unwrap(datatype):
    """Unwrap to the inner most datatype if needed."""
    if isinstance(datatype, Nullable):
        return unwrap(datatype.datatype)
    if isinstance(datatype, LowCardinality):
        return unwrap(datatype.datatype)
    return datatype


def basic_datatypes():
    return [
        UInt8(),
        UInt16(),
        UInt32(),
        UInt64(),
        UInt128(),
        Int8(),
        Int16(),
        Int32(),
        Int64(),
        Int128(),
        Float32(),
        Float64(),
        Decimal128(scale=38),
        Date(),
        DateTime(),
        DateTime64(3),
        Boolean(),
        String(),
        FixedString(length=51),
        UUID(),
    ]


def common_basic_datatypes():
    return [
        String(),
        FixedString(length=51),
        Date(),
        DateTime(),
        UInt64(),
        Int64(),
        Float32(),
        Float64(),
        Decimal128(scale=38),
    ]
