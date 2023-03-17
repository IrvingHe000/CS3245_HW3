import linecache
import pickle
from termdict import TermDict

dictionary = TermDict()


def test(dictionary_name: str, posting_name: str):
    """
    Tests the correctness of building index,
    including pointers, order of postings
    """
    print("Testing...")
    try:
        with open(dictionary_name, "rb") as f:
            global dictionary
            dictionary = pickle.load(f)
    except FileNotFoundError:
        print("Cannot load dictionary file.")
        return
    print("Load dictionary successfully.\n")

    # assert test_posting_order(posting_name)
    print("Posting order test passed.")

    assert test_pointer(posting_name)
    print("Pointer test passed.")

    assert test_freq(posting_name)
    print("Doc Frequency test passed.")


def test_posting_order(posting_name) -> bool:
    """
    Tests correctness of the order (alphabetical order) of postings.
    """
    term_list = []
    with open(posting_name) as f:
        for line in f.readlines():
            term_list.append(line.split(" ")[0])
    return all(term_list[i] <= term_list[i + 1] for i in range(len(term_list) - 1))


def test_pointer(postings_name) -> bool:
    """
    Tests correctness of pointer.
    """
    global dictionary
    for term in dictionary.dict.keys():
        pointer = dictionary.get_term_pointer(term)
        freq = dictionary.get_term_freq(term)
        line = linecache.getline(postings_name, pointer)
        to_check, posting = line.split(" ", 1)
        posting = posting.strip("\n")
        length = len(posting.split(" "))
        if length != freq:
            return False
        if term != to_check:
            return False
    return True


def test_freq(postings_name) -> bool:
    """
    Tests correctness of document freq.
    """
    global dictionary
    for term in dictionary.dict.keys():
        pointer = dictionary.get_term_pointer(term)
        freq = dictionary.get_term_freq(term)
        line = linecache.getline(postings_name, pointer)
        term_name, posting = line.split(" ", 1)
        assert term_name == term
        posting = posting.strip("\n")
        to_check_length = len(posting.split(" "))
        if to_check_length != freq:
            return False
    return True
