"""
Tests for functions in the tb module.
"""

import os

from nose.tools import ok_, eq_

from tracewhack.tb import extract_traceback, extract_tracebacks


def eq_strip_(str_or_list_1, str_or_list_2):
    """
    Just a helper to compare stripped strings.
    """
    if isinstance(str_or_list_1, list):
        str_or_list_1 = [s.strip() for s in str_or_list_1]
    if isinstance(str_or_list_2, list):
        str_or_list_2 = [s.strip() for s in str_or_list_2]
    eq_(str_or_list_1, str_or_list_2)


def read_file(fname):
    """
    Read a test file from the current directory.
    """
    curdir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(curdir, fname)) as fil:
        return fil.read()


def read_file_rn(fname):
    """
    Read a test file, replace \n with \r\n.
    """
    return read_file(fname).replace('\n', '\r\n')


def test_extract_traceback():
    """
    Test the routine to extract a single traceback.
    """
    tb_txt = read_file('simple_tb.txt')
    ok_(tb_txt)
    extracted_tb = extract_traceback(tb_txt)
    ok_(extracted_tb)
    eq_strip_(extracted_tb, read_file('simple_tb_extracted.txt'))

    tb_txt = read_file('simple_tb_2.txt')
    ok_(tb_txt)
    extracted_tb = extract_traceback(tb_txt)
    ok_(extracted_tb)
    eq_strip_(extracted_tb, read_file('simple_tb_2_extracted.txt'))

    tb_w_context_txt = read_file('contextual_tb.txt')
    extracted_tb_w_context = extract_traceback(tb_w_context_txt)
    ok_(extracted_tb_w_context)
    eq_strip_(extracted_tb_w_context,
              read_file('contextual_tb_extracted.txt'))

    not_a_tb_txt = read_file('not_a_tb.txt')
    ok_(extract_traceback(not_a_tb_txt) is None)


def test_extract_tracebacks():
    """
    Test extract_tracebacks.
    """
    # first off, extract_tracebacks should be able to handle \r\n...

    tb_txt = read_file_rn('simple_tb.txt')
    ok_(tb_txt)
    extracted_tb = extract_tracebacks(tb_txt)
    ok_(extracted_tb)
    eq_strip_(extracted_tb, [read_file('simple_tb_extracted.txt')])

    tb_txt = read_file_rn('simple_tb_2.txt')
    ok_(tb_txt)
    extracted_tb = extract_tracebacks(tb_txt)
    ok_(extracted_tb)
    eq_strip_(extracted_tb, [read_file('simple_tb_2_extracted.txt')])

    tb_w_context_txt = read_file_rn('contextual_tb.txt')
    extracted_tb_w_context = extract_tracebacks(tb_w_context_txt)
    ok_(extracted_tb_w_context)
    eq_strip_(extracted_tb_w_context,
              [read_file('contextual_tb_extracted.txt')])

    not_a_tb_txt = read_file_rn('not_a_tb.txt')
    eq_strip_([], extract_tracebacks(not_a_tb_txt))

    # second of all, we should be able to handle multiples tbs per
    # txt.
    tb_txt = read_file('simple_tb.txt')
    tb_2_txt = read_file('simple_tb_2.txt')
    tb_w_context_txt = read_file('contextual_tb.txt')
    two_tb_txt = "%s\n\n%s\n\n%s\n\n%s" % (tb_txt,
                                           not_a_tb_txt,
                                           tb_w_context_txt,
                                           tb_2_txt)
    tbs = extract_tracebacks(two_tb_txt)
    eq_(3, len(tbs))
    tbs = [tb.strip() for tb in tbs]
    ok_(read_file('simple_tb_extracted.txt').strip() in tbs)
    ok_(read_file('contextual_tb_extracted.txt').strip() in tbs)
    ok_(read_file('simple_tb_2_extracted.txt').strip() in tbs)
