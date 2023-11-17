import sys
import random


def corrupt_file(file_path, num_bytes_to_flip):
    with open(file_path, "rb") as file:
        data = bytearray(file.read())

    for _ in range(num_bytes_to_flip):
        byte_index = random.randint(0, len(data) - 1)
        bit_index = random.randint(0, 7)
        data[byte_index] ^= 1 << bit_index

    with open(file_path, "wb") as file:
        file.write(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python corrupt_file.py <file_path> <num_bytes_to_flip>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_bytes_to_flip = int(sys.argv[2])

    corrupt_file(file_path, num_bytes_to_flip)
    print(f"Corrupted {num_bytes_to_flip} bytes in {file_path}")
