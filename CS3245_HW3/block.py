from termdict import TermDict

BLK_POSTINGS_FORMAT = "{no}.posting"
BLK_DICT_FORMAT = "{no}.dict"


class Block:
    """
    Represents a block in indexing. Records the block's block number, stores dictionary of the block,
    and the location of block dictionary and postings on the disk.
    """
    def __init__(self, blk_no: int, dictionary: TermDict):
        self.blk_no = blk_no
        self.dictionary = dictionary
        self.dict_name = BLK_DICT_FORMAT.format(no=blk_no)
        self.postings_name = BLK_POSTINGS_FORMAT.format(no=blk_no)
