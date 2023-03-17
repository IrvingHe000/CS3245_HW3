#!/usr/bin/python3
import os
import re
import nltk
from nltk.tokenize import word_tokenize
import sys
import getopt
import pickle
from sortedskiplist import SortedSkipList
from sortedskiplist import union
from sortedskiplist import intersect
from sortedskiplist import complement
from termdict import TermDict

dictionary = TermDict()
STEMMER = nltk.stem.porter.PorterStemmer()
line_start_bytes = []
all_doc_ids = SortedSkipList()
ALL_DOC_IDS_FILE = "all-ids.txt"


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def build_line_start_bytes(file_name):
    with open(file_name, "rt") as file:
        global line_start_bytes
        offset = 0
        for line in file:
            line_start_bytes.append(offset)
            offset += len(line)
        file.seek(0)  # reset


def get_posting_list(term, posting_file) -> SortedSkipList:
    posting_list = SortedSkipList()
    try:
        pointer = dictionary.get_term_pointer(term)  # line-number in the file is one-indexed
    except:
        return posting_list
    with open(posting_file, "rt") as f:
        f.seek(line_start_bytes[pointer - 1])
        line = f.readline()
        doc_ids = line.split(" ")
        assert doc_ids[0] == term
        for i in range(1, len(doc_ids)):
            posting_list.add_val(int(doc_ids[i]))
        f.seek(line_start_bytes[pointer])
        skips = f.readline()
        skips = skips.split(" ")
        posting_list.build_skip_from_list(skips)
        return posting_list


def load_all_doc_ids():
    global all_doc_ids
    with open(ALL_DOC_IDS_FILE, "rt") as f:
        line = f.readline()
        doc_ids = line.split(" ")
        for doc_id in doc_ids:
            all_doc_ids.add_val(int(doc_id))


def clean_up(results_file):
    with open(results_file, "wt") as f:
        pass


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    clean_up(results_file)
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    with open(dict_file, "rb") as file:
        global dictionary
        dictionary = pickle.load(file)
    build_line_start_bytes(postings_file)
    load_all_doc_ids()

    with open(queries_file, "rt") as file:
        for line in file.readlines():
            query = line.strip()
            tokens = word_tokenize(query)
            tokens = list(map(lambda token: STEMMER.stem(token) if token != "AND" and token != "OR" and
                              token != "NOT" else token, tokens))
            result = search(tokens, postings_file)
            with open(results_file, "at") as result_f:
                result_f.write(str(result) + os.linesep)


def search(query, index_file):
    # tokenize query and apply Boolean operators
    terms = query
    stack = []
    current_operation = None
    is_not = None
    is_sub_query = False
    subQuery = []
    for term in terms:
        print(term)
        if is_sub_query:
            if term == ")":
                subResult = search(subQuery, index_file)

                if is_not:
                    subResult = complement(subResult, all_doc_ids)
                    is_not = False
                if current_operation is None:
                    stack.append(subResult)
                elif current_operation == "AND":
                    posting_list1 = stack.pop()
                    result = intersect(posting_list1, subResult)
                    stack.append(result)
                elif current_operation == "OR":
                    posting_list1 = stack.pop()
                    result = union(posting_list1, subResult)
                    stack.append(result)

                subQuery = []
                is_sub_query = False
            else:
                subQuery.append(term)
        else:
            if term == "AND":
                current_operation = "AND"
            elif term == "OR":
                current_operation = "OR"
            elif term == "NOT":
                is_not = True
            elif term == "(":
                subQuery = []
                is_sub_query = True
            else:
                posting_list2 = get_posting_list(term, index_file)
                if is_not:
                    is_not = False
                    posting_list2 = complement(posting_list2, all_doc_ids)

                if current_operation is None:
                    stack.append(posting_list2)
                elif current_operation == "AND":
                    posting_list1 = stack.pop()
                    result = intersect(posting_list1, posting_list2)
                    stack.append(result)
                elif current_operation == "OR":
                    posting_list1 = stack.pop()
                    result = union(posting_list1, posting_list2)
                    stack.append(result)

    # return final result
    return stack[0]


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
