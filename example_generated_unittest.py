# handwritten import
# todo: auto generate import from local path
from output.asn1crypto.codes.src.asn1crypto.asn1crypto.parser import parse


# generated unittest
def test_parse():
    assert parse(b"\x13\x00\x041") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00$1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"S\x00\x041") == (1, 0, 19, b"S\x00", b"", b"")
    assert parse(b"S\x00\x04;") == (1, 0, 19, b"S\x00", b"", b"")
    assert parse(b"S\x00\x14;") == (1, 0, 19, b"S\x00", b"", b"")
    assert parse(b"\x13\x00\x045") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x040") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x000") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x004") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x02\x00") == (0, 0, 2, b"\x02\x00", b"", b"")
    assert parse(b"\x13\x001") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x002") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"`\x002") == (1, 1, 0, b"`\x00", b"", b"")
    assert parse(b"`\x00=") == (1, 1, 0, b"`\x00", b"", b"")
    assert parse(b"\x13\x00\x042") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x11\x004") == (0, 0, 17, b"\x11\x00", b"", b"")
    assert parse(b"\x13\x006") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x005") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x04\x00\x042") == (0, 0, 4, b"\x04\x00", b"", b"")
    assert parse(b"\x17\x004") == (0, 0, 23, b"\x17\x00", b"", b"")
    assert parse(b"4\x00\x13") == (0, 1, 20, b"4\x00", b"", b"")
    assert parse(b"\x04\x001") == (0, 0, 4, b"\x04\x00", b"", b"")
    assert parse(b"\x13\x00<") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"s\x00<") == (1, 1, 19, b"s\x00", b"", b"")
    assert parse(b"s\x00<\xf7") == (1, 1, 19, b"s\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x04") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x00") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b'"\x00') == (0, 1, 2, b'"\x00', b"", b"")
    assert parse(b"\x04\x00\x00\x00") == (0, 0, 4, b"\x04\x00", b"", b"")
    assert parse(b"\x01\x00") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x00\x02\x00\x02") == (0, 0, 0, b"\x00\x02", b"\x00\x02", b"")
    assert parse(b"\xef\x00\x041") == (3, 1, 15, b"\xef\x00", b"", b"")
    assert parse(b"\x17\x014") == (0, 0, 23, b"\x17\x01", b"4", b"")
    assert parse(b"\xbf;\x00") == (2, 1, 59, b"\xbf;\x00", b"", b"")
    assert parse(b"\xbf6\x00") == (2, 1, 54, b"\xbf6\x00", b"", b"")
    assert parse(b"\x13\x00\xff") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\xffK") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x0b\x00\xc5\xd8") == (0, 0, 11, b"\x0b\x00", b"", b"")
    assert parse(b"\x01\x00\xff:") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x00\x01\xff:") == (0, 0, 0, b"\x00\x01", b"\xff", b"")
    assert parse(b"\x00\x01\xdf:") == (0, 0, 0, b"\x00\x01", b"\xdf", b"")
    assert parse(b"\x13\x00\x0b1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x0b0") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x0b\x0b") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x0b\x13") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\xff:") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x008") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x9f") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x9f\xda") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"Z\x01\x9dZ") == (1, 0, 26, b"Z\x01", b"\x9d", b"")
    assert parse(b"\xc8\x00\x00\x06") == (3, 0, 8, b"\xc8\x00", b"", b"")
    assert parse(b"\xc8\x00*\x06") == (3, 0, 8, b"\xc8\x00", b"", b"")
    assert parse(b"\xc8\x02*\x06") == (3, 0, 8, b"\xc8\x02", b"*\x06", b"")
    assert parse(b"\xff\xff\x04\x00") == (3, 1, 16260, b"\xff\xff\x04\x00", b"", b"")
    assert parse(b"\x13\x00\xff1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x93\x00") == (2, 0, 19, b"\x93\x00", b"", b"")
    assert parse(b"\x83\x00") == (2, 0, 3, b"\x83\x00", b"", b"")
    assert parse(b"\x00\x00") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\xa2\x00") == (2, 1, 2, b"\xa2\x00", b"", b"")
    assert parse(b"\xdd\x00") == (3, 0, 29, b"\xdd\x00", b"", b"")
    assert parse(b"\x01\x00\xff\n") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x03\x00\xff") == (0, 0, 3, b"\x03\x00", b"", b"")
    assert parse(b"\x01\x00\x00\x00") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x13\x00\x04\x13") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x04\x04") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x03\x00") == (0, 0, 3, b"\x03\x00", b"", b"")
    assert parse(b"\x03\x00\x805") == (0, 0, 3, b"\x03\x00", b"", b"")
    assert parse(b"\xca\x00\xff\xf9") == (3, 0, 10, b"\xca\x00", b"", b"")
    assert parse(b"\xca\x00") == (3, 0, 10, b"\xca\x00", b"", b"")
    assert parse(b")\x01\xef\xff") == (0, 1, 9, b")\x01", b"\xef", b"")
    assert parse(b"(\x00\t\xff") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"(\x00\t\xa1") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"(\x00\t^") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\x13\x00\x13") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x12") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x00") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x061") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\xf91") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\xf9\xff") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\xe0\x00\x00\x00") == (3, 1, 0, b"\xe0\x00", b"", b"")
    assert parse(b"(\x00\x00\x00\x05") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\x13\x00'") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00'\x13\x00") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\xff\xff\xfd\xff\x00\x00") == (
        3,
        1,
        268402560,
        b"\xff\xff\xfd\xff\x00\x00",
        b"",
        b"",
    )
    assert parse(b"\x00\x00\xac\xf9") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\xac") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"M\x00\x00\xac") == (1, 0, 13, b"M\x00", b"", b"")
    assert parse(b"\xff\xff\x01\x00") == (3, 1, 16257, b"\xff\xff\x01\x00", b"", b"")
    assert parse(b"\xff\xff\x05\x00") == (3, 1, 16261, b"\xff\xff\x05\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x1d") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\xf1\x1d") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x10\x00\xf1\x1d") == (0, 0, 16, b"\x10\x00", b"", b"")
    assert parse(b"\x13\x00\n\xb0") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x06\xb0") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x04\x00") == (0, 0, 4, b"\x04\x00", b"", b"")
    assert parse(b"\x13\x00\x04\x13\x000") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x04\x13\x080") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x02\x00\x00\x00Z") == (0, 0, 2, b"\x02\x00", b"", b"")
    assert parse(b"\x00\x00!\x135") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00=\xf5\t\xf9") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00=\xf5\xef\xf9") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\xff`\x00") == (3, 1, 96, b"\xff`\x00", b"", b"")
    assert parse(b"\x00\x00(\x80") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x00(\x80") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b")\x005") == (0, 1, 9, b")\x00", b"", b"")
    assert parse(b"(\x00\x00") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\x00\x00(") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00/") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\xff\xff\xbd\x00\x00\n") == (
        3,
        1,
        2088576,
        b"\xff\xff\xbd\x00\x00",
        b"",
        b"",
    )
    assert parse(b"\x06\x00\x00\x00\x80\x13") == (0, 0, 6, b"\x06\x00", b"", b"")
    assert parse(b"\x00\x00\xff\xf9") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x005") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x005\x00\x005") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x0055") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\xff\xff\x0055") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\xff\xff\x8055") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\xff\xff") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"(\x00\x008") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"(\x00\x006") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"(\x00\x00\xff\xff\xff\xff6") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\xbd\x00\x00\xa7") == (2, 1, 29, b"\xbd\x00", b"", b"")
    assert parse(b"\xbd\x00\x01\xa7") == (2, 1, 29, b"\xbd\x00", b"", b"")
    assert parse(b"\xbd\x00\t\xa7") == (2, 1, 29, b"\xbd\x00", b"", b"")
    assert parse(b"\x00\x00?") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"?\xff\xff\xf9\x00\x00") == (
        0,
        1,
        268434560,
        b"?\xff\xff\xf9\x00\x00",
        b"",
        b"",
    )
    assert parse(b"\x00\x00\x00\x13\x17\x00") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x88\x00\x00\x00\x00\x80") == (2, 0, 8, b"\x88\x00", b"", b"")
    assert parse(b"\x13\x00\x04\xd1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x04\xd1\x04\xd1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x13\x00\x04%\xd1\x04\xd1") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"\x00\x00\x04%\xd1\x04\xd1") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\xff\xff\xff\xff\xff\x00\x00*") == (
        3,
        1,
        34359738240,
        b"\xff\xff\xff\xff\xff\x00\x00",
        b"",
        b"",
    )
    assert parse(b":\x00\x00") == (0, 1, 26, b":\x00", b"", b"")
    assert parse(b"(\x00") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\x00\x00\xff") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"(\x00\xff") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\x00\x00\xff\xf7") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"#\x00\x00\xff\xf7") == (0, 1, 3, b"#\x00", b"", b"")
    assert parse(b"#\x00\x00") == (0, 1, 3, b"#\x00", b"", b"")
    assert parse(b"~\x00") == (1, 1, 30, b"~\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x00\x00\x00\x00\x08") == (
        0,
        0,
        0,
        b"\x00\x00",
        b"",
        b"",
    )
    assert parse(b"\x00\x00\x00\x00\x00\t\x00\x08") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00\x00+\t\x00\x08") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\x00\x00\x00(\x80(\x00\x08") == (0, 0, 0, b"\x00\x00", b"", b"")
    assert parse(b"\xe4\x00\x041") == (3, 1, 4, b"\xe4\x00", b"", b"")
    assert parse(b"\xe4\x00$\x041") == (3, 1, 4, b"\xe4\x00", b"", b"")
    assert parse(b"\xe4\x00$%\xf9\x041") == (3, 1, 4, b"\xe4\x00", b"", b"")
    assert parse(b"\xe4\x00$%\xf9\x042") == (3, 1, 4, b"\xe4\x00", b"", b"")
    assert parse(b"\xe4\x00$%\xf9\x043") == (3, 1, 4, b"\xe4\x00", b"", b"")
    assert parse(b"\xff\xff\x80(\x00") == (
        3,
        1,
        2080808,
        b"\xff\xff\x80(\x00",
        b"",
        b"",
    )
    assert parse(b"\x01\x00\x00\x00\x00\x00") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x01\x00\x00\x00\x10\x00") == (0, 0, 1, b"\x01\x00", b"", b"")
    assert parse(b"\x81\x00\x00\x00\x10\x00") == (2, 0, 1, b"\x81\x00", b"", b"")
    assert parse(b"\x13\x00\x00\x00") == (0, 0, 19, b"\x13\x00", b"", b"")
    assert parse(b"(\x00\x00(\x80") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"(\x00 (\x80") == (0, 1, 8, b"(\x00", b"", b"")
    assert parse(b"\xff;\x00\x00\x00\n") == (3, 1, 59, b"\xff;\x00", b"", b"")
    assert parse(b"\xff;\x00\x00\x00") == (3, 1, 59, b"\xff;\x00", b"", b"")
    assert parse(b"\n\x00\x00") == (0, 0, 10, b"\n\x00", b"", b"")
    assert parse(b"\n\x00\x00H") == (0, 0, 10, b"\n\x00", b"", b"")
    assert parse(b"\n\x00H") == (0, 0, 10, b"\n\x00", b"", b"")
    assert parse(b"\n\x00/H") == (0, 0, 10, b"\n\x00", b"", b"")
    assert parse(b"\xac\x02\x02\x07") == (2, 1, 12, b"\xac\x02", b"\x02\x07", b"")
    assert parse(b"\xff\xff\xff\xff\xf9\x00\x00") == (
        3,
        1,
        34359737472,
        b"\xff\xff\xff\xff\xf9\x00\x00",
        b"",
        b"",
    )
