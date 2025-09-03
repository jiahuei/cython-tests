import octo


def main():
    """Demonstrate the usage of the compiled octo."""

    print("=== octo Demo ===")
    print()

    # Test cases
    test_cases = [(5, 3), (10.5, 2.7), (-5, 8), (0, 0), (100, -50)]

    for a, b in test_cases:
        result = octo.add_numbers(a, b)
        print(f"add_numbers({a}, {b}) = {result}")

    print()
    print("=== Library Information ===")
    print(f"Function name: {octo.add_numbers.__name__}")
    print(f"Function doc: {octo.add_numbers.__doc__}")
    print(f"Module file: {octo.__file__}")


if __name__ == "__main__":
    main()
