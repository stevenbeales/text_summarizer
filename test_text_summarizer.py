import pytest
import text_summarizer


def test_parse_no_arguments():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        text_summarizer.parse_arguments()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2


def test_parse_existing_file():
    assert text_summarizer.parse_data_from_input(
        './summary.txt').strip().startswith('C')


def test_parse_missing_file():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        text_summarizer.parse_data_from_input('missing file')
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == None


def test_parse_existing_url():
    assert text_summarizer.parse_data_from_input(
        'http://www.google.com').find("Terms")


def test_parse_missing_url():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        text_summarizer.parse_data_from_input('http://not a url')
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == None


def test_sanitize_input():
    assert text_summarizer.sanitize_input('\r\n\t') == ' '


def test_word_wrap_summary():
    assert text_summarizer.word_wrap_summary("""
    1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890 1234567890
    """
                                             ).find('\n')
