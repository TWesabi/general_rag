def add(a: int, b: int) -> int | float:
    c = a + b
    return c


def test_output_type():
    a = 1
    b = 1

    c = add(a, b)

    assert isinstance(c, int)


def test_output_value():
    a = 1
    b = 1

    c = add(a, b)

    assert c == 2
