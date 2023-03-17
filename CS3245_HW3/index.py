#!/usr/bin/python3
import linecache
import os
import pickle
import shutil
import string

import nltk
import sys
import getopt
from collections import OrderedDict
from typing import List
from typing.io import TextIO

import test_index
from termdict import TermDict
from pair import Pair
from sortedskiplist import SortedSkipList
from sortedskiplist import union
from block import Block
from block import BLK_DICT_FORMAT
from block import BLK_POSTINGS_FORMAT

TMP_DIR = "tmp"
BLOCK_SIZE = 50000
TEST_SIZE = -1  # change test size to -1 to index the whole corpus
all_doc_ids = SortedSkipList()
ALL_DOC_IDS_FILE = "all-ids.txt"


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def get_tmp_path(file_name: str) -> str:
    """
    Appends tmp directory to file_name
    """
    return os.path.join(TMP_DIR, file_name)


def clean_up():
    """
    Cleans up tmp files used for storing intermediate results.
    """
    if os.path.isdir(TMP_DIR):
        files = os.listdir(TMP_DIR)
        for file in files:
            os.remove(os.path.join(TMP_DIR, file))
        os.rmdir(TMP_DIR)


def generate_word_tokens(file: TextIO) -> set:
    """
    Generate a set of word tokens from input file.
    """
    content = file.read()
    sent_tokens = nltk.sent_tokenize(content)
    word_tokens = set()
    for sent in sent_tokens:
        words = nltk.word_tokenize(sent)
        for word in words:
            # if word.isalpha():
            word = word.strip(string.punctuation + "\n" + " ")
            if word == "":
                continue
            word_tokens.add(word.lower())
    return word_tokens


def stem(tokens: set) -> set:
    """
    Stems tokens using Porter Stemmer.
    """
    STEMMER = nltk.stem.porter.PorterStemmer()
    stemmed_tokens = set()
    for token in tokens:
        stemmed_tokens.add(STEMMER.stem(token))
    return stemmed_tokens


def create_blocks(in_dir: str) -> List[Block]:
    """
    Generates a list of term-id pairs, when the size of the list equals to BLOCK_SIZE,
    groups pairs and converts them to a block.
    A list of resulting blocks is returned.
    """
    file_list = os.listdir(in_dir)
    blocks = []  # a queue representing blocks to be merged
    pairs = []  # a list of term - doc_id pair
    cnt = 0
    blk_cnt = 0
    for file_name in file_list:
        cnt += 1
        all_doc_ids.add_val(int(file_name))
        if cnt == TEST_SIZE:
            break
        try:
            path = os.path.join(in_dir, file_name)
            with open(path, "rt") as f:
                tokens = generate_word_tokens(f)
                tokens = stem(tokens)
            for token in tokens:
                if len(pairs) == BLOCK_SIZE:
                    block = pairs_to_block(pairs, blk_cnt)
                    blocks.append(block)
                    blk_cnt += 1
                    pairs = []
                pairs.append(Pair(token, int(file_name)))
        except FileNotFoundError:
            print("Cannot find file" + file_name)
    if len(pairs) != 0:  # leftover
        blk = pairs_to_block(pairs, blk_cnt)
        blocks.append(blk)
        blk_cnt += 1
    with open(ALL_DOC_IDS_FILE, "wt") as f:
        f.write(str(all_doc_ids))
    return blocks


def pairs_to_block(pairs: list, blk_no: int) -> Block:
    """
    Convert a list of pairs of maximum BLOCK_SIZE to a block,
    writes the block to the disk and returns relevant information about the block.
    """
    blk_dict = TermDict()
    blk_postings = {}
    for pair in pairs:
        if pair.key not in blk_dict:
            blk_dict.add_term(pair.key)
            assert pair.key not in blk_postings.keys()
            blk_postings[pair.key] = SortedSkipList()
        blk_postings[pair.key].add_val(pair.doc_id)

    blk_postings = OrderedDict(sorted(blk_postings.items()))
    blk = Block(blk_no, blk_dict)
    write_blk(blk, blk_postings)
    return blk


def write_blk(blk: Block, postings: OrderedDict):
    """
    Writes a block to the disk.
    """
    blk_no = blk.blk_no
    line_no = 0
    if not os.path.isdir(TMP_DIR):
        os.mkdir(TMP_DIR)
    postings_name = get_tmp_path(BLK_POSTINGS_FORMAT.format(no=blk_no))
    dict_name = get_tmp_path(BLK_DICT_FORMAT.format(no=blk_no))
    try:
        with open(postings_name, "wt") as f:
            for term, posting in postings.items():
                line = term + " " + str(posting) + os.linesep
                f.write(line)
                line_no += 1
                posting.build_skip()
                line = posting.skip_to_str() + os.linesep
                f.write(line)
                blk.dictionary.set_term_pointer(term, line_no)
                line_no += 1
                blk.dictionary.set_term_freq(term, len(posting))
    except FileNotFoundError:
        raise RuntimeWarning("Cannot write posting for blk " + str(blk_no))
    try:
        with open(dict_name, "wb") as f:
            pickle.dump(blk.dictionary, f)
    except FileNotFoundError:
        raise RuntimeWarning("Cannot write dictionary for blk " + str(blk_no))


def load_blk_dict(blk: Block) -> TermDict:
    """
    Loads dictionary of a block from memory.
    """
    file_name = get_tmp_path(blk.dict_name)
    with open(file_name, "rb") as f:
        dummy = pickle.load(f)
        return dummy


def load_blk_line(blk: Block, line_no: int) -> SortedSkipList:
    """
    Loads a specified line of a block from the file.
    """
    file_name = get_tmp_path(blk.postings_name)
    line = linecache.getline(file_name, line_no)
    line = line.strip("\r\n")
    line = line.strip("\n")
    assert line != ""
    term, posting = line.split(" ", 1)
    posting = posting.split(" ")
    posting_list = SortedSkipList()
    for doc_id in posting:
        posting_list.add_val(doc_id)
    line = linecache.getline(file_name, line_no+1)
    line = line.strip("\r\n")
    line = line.strip("\n")
    skips = line.split(" ")
    # skips = [int(skip) for skip in skips]
    posting_list.build_skip_from_list(skips)
    return posting_list


def merge_blocks(blocks: List[Block]) -> Block:
    """
    Merges a list of blocks into one final block.
    """
    blk_cnt = len(blocks)
    while len(blocks) != 1:
        n = len(blocks)
        i = 0
        while i != n:
            blk1 = blocks.pop(0)
            if i + 1 != n:
                blk2 = blocks.pop(0)
                blocks.append(merge_two_blocks(blk1, blk2, blk_cnt))
                blk_cnt += 1
                i += 2
            else:
                blocks.append(blk1)
                i += 1
    return blocks[0]


def merge_two_blocks(blk1: Block, blk2: Block, result_blk_no: int) -> Block:
    """
    Merges two blocks blk1 and blk2, returns the merged block.
    """
    dict1 = load_blk_dict(blk1)
    dict2 = load_blk_dict(blk2)
    result_dict = TermDict()

    for term in dict1:
        result_dict.add_term(term)
        dict1_freq = dict1.get_term_freq(term)
        dict2_freq = dict2.get_term_freq(term) if term in dict2 else 0
        result_dict.set_term_freq(term, dict1_freq + dict2_freq)
    for term in dict2:
        if term not in result_dict:
            assert term not in dict1
            result_dict.add_term(term)
            result_dict.set_term_freq(term, dict2.get_term_freq(term))
    result_blk = Block(result_blk_no, result_dict)

    posting_file_name = get_tmp_path(result_blk.postings_name)
    with open(posting_file_name, "wt") as f:
        line_cnt = 0
        for term in sorted(result_dict.dict):
            line_cnt += 1
            if term not in dict1.dict:
                assert term in dict2
                line = term + " " + str(load_blk_line(blk2, dict2.get_term_pointer(term))) + os.linesep
                line += linecache.getline(blk2.postings_name, dict2.get_term_pointer(term)+1) + os.linesep
            elif term not in dict2.dict:
                assert term in dict1
                line = term + " " + str(load_blk_line(blk1, dict1.get_term_pointer(term))) + os.linesep
                line += linecache.getline(blk1.postings_name, dict1.get_term_pointer(term)+1) + os.linesep
            else:  # term appear in both blocks
                assert term in dict1 and term in dict2
                posting1 = load_blk_line(blk1, dict1.get_term_pointer(term))
                posting2 = load_blk_line(blk2, dict2.get_term_pointer(term))
                posting = union(posting1, posting2)
                posting.build_skip()
                line = term + " " + str(posting) + os.linesep
                line += posting.skip_to_str() + os.linesep
            result_blk.dictionary.set_term_pointer(term, line_cnt)
            line_cnt += 1
            f.write(line)
    dict_file_name = get_tmp_path(result_blk.dict_name)
    with open(dict_file_name, "wb") as f:
        pickle.dump(result_dict, f)
    return result_blk


def migrate_final_blk(final_blk: Block, out_dict: str, out_postings: str):
    """
    Copy the final merged block's dictionary and postings to be the index output dictionary and postings.
    """
    dict_file = get_tmp_path(final_blk.dict_name)
    postings_file = get_tmp_path(final_blk.postings_name)
    shutil.copyfile(dict_file, out_dict)
    shutil.copyfile(postings_file, out_postings)


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below
    clean_up()
    blocks = create_blocks(in_dir)
    final_blk = merge_blocks(blocks)
    migrate_final_blk(final_blk, out_dict, out_postings)
    # test_index.test(out_dict, out_postings)
    # clean_up()

    print("\nindex finished.")
    print("results have been written to '{}' and '{}'".format(out_dict, out_postings))


def main():
    input_directory = output_file_dictionary = output_file_postings = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-i':  # input directory
            input_directory = a
        elif o == '-d':  # dictionary file
            output_file_dictionary = a
        elif o == '-p':  # postings file
            output_file_postings = a
        else:
            assert False, "unhandled option"

    if input_directory is None or output_file_postings is None or output_file_dictionary is None:
        usage()
        sys.exit(2)

    build_index(input_directory, output_file_dictionary, output_file_postings)


if __name__ == "__main__":
    main()
