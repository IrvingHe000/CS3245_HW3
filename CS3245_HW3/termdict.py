class TermItem:
    """
    Represents a token in the dictionary, containing term, doc frequency and pointer to the posting.

    Attributes:
        _term: the word term itself.
        _doc_freq:  document frequency.
        _pointer: line number of the posting in the postings file.
    """
    def __init__(self, term: str, doc_freq: int = 1, pointer: int = -1):
        self._term = term
        self._doc_freq = doc_freq
        self._pointer = pointer

    def get_term(self) -> str:
        return self._term

    def get_doc_freq(self) -> int:
        return self._doc_freq

    def get_pointer(self) -> int:
        return self._pointer

    def set_doc_freq(self, freq: int):
        self._doc_freq = freq

    def increment_freq(self):
        self._doc_freq += 1

    def set_pointer(self, pointer: int):
        self._pointer = pointer

    def __str__(self):
        return "({}, {}, {})".format(self._term, self._doc_freq, self._pointer)


class TermDict:
    """
    Represents a dictionary containing terms and their corresponding doc_freq and pointer to the posting.
    """
    def __init__(self):
        self.dict = {}

    def add_term(self, term: str):
        if term not in self.dict.keys():
            self.dict[term] = TermItem(term, 0)
        self.dict[term].increment_freq()

    def get_term_pointer(self, term: str) -> int:
        if term not in self:
            raise RuntimeError
        return self.dict[term].get_pointer()

    def get_term_freq(self, term: str) -> int:
        if term not in self:
            return -1
        return self.dict[term].get_doc_freq()

    def set_term_freq(self, term: str, freq: int):
        if term not in self:
            raise KeyError
        self.dict[term].set_doc_freq(freq)

    def set_term_pointer(self, term: str, pointer: int):
        if term not in self:
            raise KeyError
        self.dict[term].set_pointer(pointer)

    def __len__(self) -> int:
        return len(self.dict)

    def __contains__(self, term: str) -> bool:
        return term in self.dict.keys()

    def __iter__(self):
        return iter(self.dict)
