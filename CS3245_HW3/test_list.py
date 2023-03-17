from sortedskiplist import SortedSkipList
from sortedskiplist import union
from sortedskiplist import intersect
from sortedskiplist import complement


def test():
    l1 = SortedSkipList()
    l2 = SortedSkipList()

    for i in [0, 5, 7, 1, 2, 9, 11, 6]:
        l1.add_val(i)
    for i in [11, 13, 15, 14, 12, 6]:
        l2.add_val(i)

    print("list1: ", l1)
    print("list2: ", l2)

    l1.build_skip(True)
    l2.build_skip(True)

    r1 = intersect(l1, l2)
    print(r1)

    r2 = union(l1, l2)
    print(r2)

    l3 = SortedSkipList()
    l4 = SortedSkipList()
    for i in range(10):
        l3.add_val(i)
    for i in range(0, 10, 2):
        l4.add_val(i)
    print("l3: ", l3)
    print("l4: ", l4)
    r3 = complement(l4, l3)
    print(r3)

    # l3.build_skip_from_list([1, 3, 5, 7])
    l3.build_skip(clear_all=True)
    print(l3.skip_to_str())

    l5 = SortedSkipList()
    for i in [1, 2, 3]:
        l5.add_val(i)
    l5.build_skip(True)
    print(l5.skip_to_str())

if __name__ == "__main__":
    test()
