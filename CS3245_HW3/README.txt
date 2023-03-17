This is the README file for A0268977Y and A0211246U's submission
Email(s): e1107334@u.nus.edu and e0492516@u.nus.edu

== Python Version ==

We're using Python Version 3.8.15 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

This program has two parts, indexing and searching, and it used a few data
structures.

A SortedSkipList data structure is used to store posting. It is a linked list
with an additional skip pointer, and the order of the items inside is maintained.

A TermDict data structure is used to store term, document frequency  pointer
to the posting list. The pointer is defined as the line number in the postings
file that records the posting list.

Postings are stored in postings.txt in plain text, every two lines record posting and
skip for a term. The first one records complete posting and the second one only records
skip index. It can be randomly accessed by line number. An additional all-ids.txt
file is kept to record all the doc id that has appeared. It is useful for doing
complement (not) operation.

Dictionary is stored in dictionary.txt in TermDict structure. Reading and writing
dictionary is done with pickle load and dump.

For indexing part, the program loops first through all files in the reuters training
data folder. For each file, the program first do preprocessing, which includes
generating work tokens and doing stemming. Preprocessed tokens will create a
Pair along with their corresponding doc_ids. The program sequentially process
tokens and create pairs, when the number of pairs has reached a pre-defined
block size, these pairs will be sorted and written to the disk as a block. The
dictionary of that block is also written to the disk.

After creating blocks for all pairs, the program will do two-way merging to
merge all blocks. A queue is used to record blocks data, which contains block
dictionary and the name of file used to store the block. Each time it pops two
blocks data, loads part of the blocks and appends the merged block until there
is only one final block left. Dictionaries of both blocks are also merged.

For the searching part, the program firstly load the file name and pointer to the position of
that line inside file from dict_file to a TermDict. The program will also load all ids into a file.
Then, the program will read from the query file line by line to get the query. To process the query,
the program uses word_tokenize and stemmer from nltk library to transform the query to a
list containing stemmed components of the query.

Then, the search function will loop through the query list. This function keeps
a stack and two values store whether there is a key word (AND or OR) and NOT before
current term. If there is no key word before it, the program will directly store the
value on the stack. If there is a NOT key word before it, the program will apply complement
function before processing it. If there is a AND or OR key word before the term, after reading
from the postings_file, the program will apply intersect or union function on the posting_list
stored on stack and the current value. If the program enter a '(', it will read until the next
')', and send the sub-query between "()" to the search function again to get the result.
After getting the final result of the query, the program will write the result of query to the
result file.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

* all-ids.txt: a text file used to keep all doc id that has appeared.
* block.py: Block class represents a block's dictionary and file names of actual postings.
* dictionary.txt: TermDict object storing term, document freq, and pointer to posting.
* pair.py: Pair class represents a (term, doc id) pair.
* postings.txt: Stores postings in plain text.
* README.txt: this file.
* sortedskiplist.py: a SortedSkipList data structure implementation.
* termdict.py: a TermDict class, storing (term, document_freq, pointer).
* test_index.py: test correctness of indexing.
* test_list.py: test correctness of SortedSkipList.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0268977Y and A0211246U, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
* Textbook
* Lecture 2, 3, 4, 5 slides
* pickle library documentation (https://docs.python.org/3/library/pickle.html)
* linecache library documentation (https://docs.python.org/3/library/linecache.html)
