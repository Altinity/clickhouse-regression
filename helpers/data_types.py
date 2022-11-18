import random


class DataType:
    def __init__(
        self,
        type,
        name=None,
        is_low_cardinality=True,
        is_valid_map_key=True,
        is_numeric=True,
        is_unsigned=False,
        max=None,
        min=None,
    ):
        self.type = type
        self.name = name if name else type.lower()
        self.is_low_cardinality = is_low_cardinality
        self.is_valid_map_key = is_valid_map_key
        self.is_numeric = is_numeric
        self.is_unsigned = is_unsigned
        self.max = max
        self.min = min

    def max_value(self):
        return f"to{self.type}({self.max})"

    def min_value(self):
        return f"to{self.type}({self.min})"


# Ints
class Int(DataType):
    def __init__(self, type, max, min, is_unsigned=False):
        super().__init__(
            type=type,
            max=max,
            min=min,
            is_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=True,
            is_unsigned=is_unsigned,
        )

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"to{self.type}({random.randint(self.min, self.max)})"

    def zero_or_null_value(self):
        return f"to{self.type}(0)"


class Int8(Int):
    def __init__(self):
        super().__init__(type="Int8", max=127, min=-128)


class Int16(Int):
    def __init__(self):
        super().__init__(type="Int16", max=32767, min=-32768)


class Int32(Int):
    def __init__(self):
        super().__init__(type="Int32", max=2147483647, min=-2147483648)


class Int64(Int):
    def __init__(self):
        super().__init__(
            type="Int64", max=9223372036854775807, min=-9223372036854775808
        )


class Int128(Int):
    def __init__(self):
        super().__init__(
            type="Int128",
            max=170141183460469231731687303715884105727,
            min=-170141183460469231731687303715884105728,
        )


class Int256(Int):
    def __init__(self):
        super().__init__(
            type="Int256",
            max=57896044618658097711785492504343953926634992332820282019728792003956564819967,
            min=-57896044618658097711785492504343953926634992332820282019728792003956564819968,
        )


# UInts
class UInt(Int):
    def __init__(self, type, max):
        super().__init__(type=type, max=max, min=0, is_unsigned=True)


class UInt8(UInt):
    def __init__(self):
        super().__init__(type="UInt8", max=255)


class UInt16(UInt):
    def __init__(self):
        super().__init__(type="UInt16", max=65535)


class UInt32(UInt):
    def __init__(self):
        super().__init__(type="UInt32", max=4294967295)


class UInt64(UInt):
    def __init__(self):
        super().__init__(type="UInt64", max=18446744073709551615)


class UInt128(UInt):
    def __init__(self):
        super().__init__(type="UInt128", max=340282366920938463463374607431768211455)


class UInt256(UInt):
    def __init__(self):
        super().__init__(
            type="UInt256",
            max=115792089237316195423570985008687907853269984665640564039457584007913129639935,
        )


# Floats
class Float(DataType):
    def __init__(self, type, max, min):
        super().__init__(
            type=type,
            max=max,
            min=min,
            is_low_cardinality=True,
            is_valid_map_key=False,
        )

    def zero_or_null_value(self):
        return f"to{self.type}(0)"


class Float32(Float):
    def __init__(self):
        super().__init__(type="Float32", max="3.4028235e38", min="-3.4028235e38")

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"toFloat32({random.uniform(float(self.min), float(self.max))})"


class Float64(Float):
    def __init__(self):
        super().__init__(
            type="Float64", max="1.7976909999999999e308", min="-1.7976909999999999e308"
        )

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"toFloat64({random.uniform(-1.79769, -1.79769)}e{random.randint(0,308)})"


# Decimals
class Decimal(DataType):
    def __init__(self, type, name, max, min, scale):
        self.scale = scale
        super().__init__(
            type=type,
            name=name,
            max=max,
            min=min,
            is_low_cardinality=False,
            is_valid_map_key=False,
        )

    def max_value(self):
        return f"to{self.type}({self.max}, {self.scale})"

    def min_value(self):
        return f"to{self.type}({self.min}, {self.scale})"

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"to{self.type}({random.uniform(float(self.min), float(self.max))}, {self.scale})"

    def zero_or_null_value(self):
        return f"to{self.type}(0, {self.scale})"


class Decimal32(Decimal):
    def __init__(self, scale):
        if scale == 9:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (9 - scale) + "." + "9" * scale
        super().__init__(
            type=f"Decimal32({scale})",
            name="decimal32_" + str(scale),
            max=limit,
            min="-" + limit,
            scale=scale
        )


class Decimal64(Decimal):
    def __init__(self, scale):
        if scale == 18:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (18 - scale) + "." + "9" * scale
        super().__init__(
            type=f"Decimal64({scale})",
            name="decimal64_" + str(scale),
            max=limit,
            min="-" + limit,
            scale=scale
        )


class Decimal128(Decimal):
    def __init__(self, scale):
        if scale == 38:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (38 - scale) + "." + "9" * scale
        super().__init__(
            type=f"Decimal128({scale})",
            name="decimal128_" + str(scale),
            max=limit,
            min="-" + limit,
            scale=scale
        )


class Decimal256(Decimal):
    def __init__(self, scale):
        if scale == 76:
            limit = "0." + "9" * (scale - 1)
        else:
            limit = "9" * (76 - scale) + "." + "9" * scale
        super().__init__(
            type=f"Decimal32({scale})",
            name="decimal32_" + str(scale),
            max=limit,
            min="-" + limit,
            scale=scale
        )


# Date and DateTime
class Date(DataType):
    def __init__(self, type="Date", name=None, max="'2149-06-06'", min="'1970-01-01'"):
        super().__init__(
            type=type,
            name=name,
            max=max,
            min=min,
            is_low_cardinality=True,
            is_numeric=False,
            is_unsigned=False,
            is_valid_map_key=True,
        )

    def rand_value(self, seed=None):
        random.seed(seed)
        return self.max if random.randint(0, 1) else self.min

    def zero_or_null_value(self):
        return self.min


class Date32(Date):
    def __init__(self, type="Date32", max="'2299-12-31'", min="'1900-01-01'"):
        super().__init__(type=type, max=max, min=min)


class DateTime(Date):
    def __init__(
        self, type="DateTime", max="'2106-02-07 06:28:15'", min="'1970-01-01 00:00:00'"
    ):
        super().__init__(type=type, max=max, min=min)


class DateTime64(Date):
    def __init__(self, precision):
        super().__init__(
            type=f"DateTime64({precision})",
            name=f"datetime64_{precision}",
            max="'2299-12-31 23:59:59.99999999'"
            if precision != 9
            else "'2262-04-11 23:47:16'",
            min="'1900-01-01 00:00:00'",
        )


# Misc
class String(DataType):
    def __init__(
        self,
        type="String",
        name=None,
        max="'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ'",
        min="''",
    ):
        super().__init__(
            type=type,
            name=name,
            max=max,
            min=min,
            is_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
        )

    def rand_value(self, seed=None):
        random.seed(seed)
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
                + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ"[
                    0:length
                ]
                + "'"
            )
        else:
            max = (
                "'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ"
                + "a" * (length - 51)
                + "'"
            )
        super().__init__(
            type=f"FixedString({length})", name=f"fixedstring_{length}", max=max
        )

    def max_value(self):
        return f"to{self.type}({self.max},{self.length})"

    def min_value(self):
        return f"to{self.type}({self.min},{self.length})"

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"'{self.max[random.randint(1,len(self.max)-2)] * random.randint(0,self.length)}'"


class Boolean(DataType):
    def __init__(self):
        super().__init__(
            type="Bool",
            is_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
            max="true",
            min="false",
        )

    def rand_value(self, seed=None):
        random.seed(seed)
        return "true" if random.randint(0, 1) else "false"

    def zero_or_null_value(self):
        return "false"


class UUID(DataType):
    def __init__(self):
        super().__init__(
            type="UUID",
            is_low_cardinality=True,
            is_valid_map_key=True,
            is_numeric=False,
            max="'ffffffff-ffff-ffff-ffff-ffffffffffff'",
            min="'00000000-0000-0000-0000-000000000000'",
        )

    def rand_value(self, seed=None):
        random.seed(seed)
        return f"'{hex(random.randint(0,4294967295))[2:]}-{hex(random.randint(0,65535))[2:]}-{hex(random.randint(0,65535))[2:]}-{hex(random.randint(0,65535))[2:]}-{hex(random.randint(0,281474976710655))[2:]}'"

    def zero_or_null_value(self):
        return self.min


# Modifiers
class Nullable(DataType):
    def __init__(self, data_type):
        self.data_type = data_type
        super().__init__(
            type=f"Nullable({data_type.type})",
            name="nullable_" + data_type.name,
            is_low_cardinality=data_type.is_low_cardinality,
            is_valid_map_key=False,
            is_numeric=data_type.is_numeric,
            is_unsigned=data_type.is_unsigned,
            max=data_type.max,
            min=data_type.min,
        )

    def max_value(self):
        return self.data_type.max_value()

    def min_value(self):
        return self.data_type.min_value()

    def rand_value(self, seed=None):
        return self.data_type.rand_value(seed=seed)

    def zero_or_null_value(self):
        return "Null"


class LowCardinality(DataType):
    def __init__(self, data_type):
        self.data_type = data_type
        super().__init__(
            type=f"LowCardinality({data_type.type})",
            name="low_card_" + data_type.name,
            is_low_cardinality=True,
            is_valid_map_key=True if isinstance(data_type, String) else False,
            is_numeric=data_type.is_numeric,
            is_unsigned=data_type.is_unsigned,
            max=data_type.max,
            min=data_type.min,
        )

    def max_value(self):
        return self.data_type.max_value()

    def min_value(self):
        return self.data_type.min_value()

    def rand_value(self, seed=None):
        return self.data_type.rand_value(seed=seed)

    def zero_or_null_value(self):
        return self.data_type.zero_or_null_value()


basic_data_types = [
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
    Date32(),
    DateTime(),
    Boolean(),
    String(),
    FixedString(length=51),
    UUID(),
]

common_basic_data_types = [
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
