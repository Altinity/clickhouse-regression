import random
import string


def random_json(max_depth=3, max_length=5):
    """
    Generate a random JSON object with random types, respecting the given max depth and length.

    :param max_depth: Maximum depth of the JSON object.
    :param max_length: Maximum number of key-value pairs per object.
    :return: (Generated JSON object, Path-to-Type dictionary)
    """
    type_map = {}

    def generate_object(depth=0, prefix=""):
        """Recursive function to generate JSON with tracking of types."""
        if depth >= max_depth:
            value = random_value()
            type_map[prefix] = get_clickhouse_type(value)
            return value

        json_object = {}
        num_keys = random.randint(1, max_length)

        for _ in range(num_keys):
            key = random_key()
            path = f"{prefix}.{key}" if prefix else key

            if random.random() < 0.3:
                json_object[key] = generate_object(depth + 1, path)
            else:
                value = random_value()
                json_object[key] = value
                type_map[path] = get_clickhouse_type(value)

        return json_object

    json_obj = generate_object()
    return json_obj, type_map


def random_value():
    """Generate a random value of a supported JSON type with homogeneous arrays."""
    types = [
        lambda: random.randint(-1000, 1000),  # Int64
        lambda: round(random.uniform(-1000, 1000), 2),  # Float64
        lambda: "".join(
            random.choices(string.ascii_letters, k=random.randint(5, 10))
        ),  # String
        lambda: random.choice([True, False]),  # Bool
        lambda: generate_homogeneous_array(),  # Array of a single type
    ]
    return random.choice(types)()


def generate_homogeneous_array(max_length=10):
    """Generate an array where all elements are of a compatible supertype."""

    type_group = random.choice(["numeric", "string"])

    if type_group == "numeric":
        element_types = [
            lambda: random.randint(-1000, 1000),  # Int64
            lambda: round(random.uniform(-1000, 1000), 2),  # Float64
            lambda: random.choice([True, False]),  # Bool
        ]
    else:
        element_types = [
            lambda: "".join(
                random.choices(string.ascii_letters, k=random.randint(5, 10))
            )  # String
        ]

    element_type = random.choice(element_types)

    return [element_type() for _ in range(random.randint(0, max_length))]


def get_clickhouse_type(value):
    """Determine ClickHouse JSON type for a given Python value."""
    if isinstance(value, bool):
        return "Bool"
    elif isinstance(value, int):
        return "Int64"
    elif isinstance(value, float):
        return "Float64"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, list):
        return f"Array({get_clickhouse_type(value[0])})" if value else "Array(String)"
    elif isinstance(value, dict):
        return "JSON"
    else:
        return "String"


def random_key():
    """Generate a random key name."""
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
