class Pair:
    """
    Represents a term-doc_id pair when building index.
    Attributes:
        key: the term word
        doc_id: document id
    """
    def __init__(self, key: str, doc_id: int):
        self.key = key
        self.doc_id = doc_id

    def get_key(self) -> str:
        return self.key

    def get_doc_id(self) -> int:
        return self.doc_id

    def equal(self, pair) -> bool:
        return self.key == pair.get_key() and self.doc_id == pair.get_doc_id()

    def __str__(self) -> str:
        return "(" + self.key + "," + str(self.doc_id) + ")"
