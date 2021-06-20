import pytest

from phone_parser import find_phones


@pytest.mark.parametrize(
    "raw_text",
    [
        "84951112233",
        "+74951112233",
        "phone: 84951112233",
        "телефон: 8(495)111-22-33",
    ]
)
def test_find_phones_ok(raw_text):
    phones = list(find_phones(raw_text))
    assert len(phones) == 1


@pytest.mark.parametrize(
    "raw_text",
    [
        "8495111223",
        "+7495111223",
        "phone",
        "телефон",
        "телефон: 11133"
    ]
)
def test_find_phones_error(raw_text):
    phones = list(find_phones(raw_text))
    assert len(phones) == 0
