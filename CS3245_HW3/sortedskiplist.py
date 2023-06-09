import math
from typing import List


class Node:
    def __init__(self, val, next_node=None, skip=None) -> None:
        self.val = val
        self.next = next_node
        self.skip = skip

    def has_next(self) -> bool:
        return self.skip is None

    def __eq__(self, other) -> bool:
        return self.val == other.val \
            and self.next == other.next \
            and self.skip == other.skip

    def __str__(self) -> str:
        return str(self.val)


class SortedSkipList:

    def __init__(self):
        self._head = Node("dummy")  # a dummy head
        self._tail = self._head
        self._size = 0
        self._items = set()

    def get_head(self) -> Node:
        return self._head.next

    def add_val(self, val: int):
        if val in self:
            return
        self._items.add(val)
        self._add(Node(val))

    def _add(self, to_add: Node) -> None:
        if self._size == 0:
            self._head.next = to_add
            self._tail = to_add
            self._size = 1
        else:
            if to_add.val >= self._tail.val:
                pre_tail = self._tail
                pre_tail.next = to_add
                self._tail = to_add
            else:
                pre = self._head
                while (pre.next is not None) and (pre.next.val < to_add.val):
                    pre = pre.next
                to_add.next = pre.next
                pre.next = to_add
            self._size += 1

    def build_skip(self, clear_all=True):
        if clear_all:
            for node in self:
                node.skip = None

        skip_l = int(math.sqrt(len(self)))
        last_skip = None
        i = 0
        for node in self:
            if i % skip_l == 0:
                if last_skip is not None:
                    last_skip.skip = node
                last_skip = node
            i += 1

    def skip_to_str(self):
        it = self.get_head()
        res = ""
        while it is not None:
            if it.skip is not None:
                res += str(it.val)
                if it.skip.skip is not None:
                    res += " "
            it = it.next
        return res

    def build_skip_from_list(self, skip_list: List):
        self.build_skip()

    def __len__(self) -> int:
        return self._size

    def __contains__(self, item: int) -> bool:
        return item in self._items

    def __iter__(self):
        self._current = self.get_head()
        return self

    def __next__(self):
        if self._current is None:
            raise StopIteration
        else:
            node = self._current
            self._current = self._current.next
            return node

    def __str__(self):
        res = ""
        ptr = self._head.next
        while ptr is not None:
            if ptr.next is not None:
                res = res + str(ptr.val) + " "
            else:
                res = res + str(ptr.val)
            ptr = ptr.next
        return res


def union(list1: SortedSkipList, list2: SortedSkipList) -> SortedSkipList:
    res = SortedSkipList()
    it1 = list1.get_head()
    it2 = list2.get_head()

    while it1 is not None and it2 is not None:
        if it1.val == it2.val:
            res.add_val(it1.val)
            it1 = it1.next
            it2 = it2.next
        elif it1.val < it2.val:
            res.add_val(it1.val)
            it1 = it1.next
        elif it1.val > it2.val:
            res.add_val(it2.val)
            it2 = it2.next
        else:
            raise RuntimeError

    while it1 is not None:
        res.add_val(it1.val)
        it1 = it1.next
    while it2 is not None:
        res.add_val(it2.val)
        it2 = it2.next

    return res


def intersect(list1: SortedSkipList, list2: SortedSkipList) -> SortedSkipList:
    res = SortedSkipList()
    it1 = list1.get_head()
    it2 = list2.get_head()
    while it1 is not None and it2 is not None:
        if it1.val == it2.val:
            res.add_val(it1.val)
            it1 = it1.next
            it2 = it2.next
        elif it1.val < it2.val:
            if it1.skip is not None and it1.skip.val < it2.val:
                it1 = it1.skip
            else:
                it1 = it1.next
        else:  # it1.val > it2.val
            if it2.skip is not None and it2.skip.val < it1.val:
                it2 = it2.skip
            else:
                it2 = it2.next

    return res


def complement(list: SortedSkipList, all_doc: SortedSkipList) -> SortedSkipList:
    res = SortedSkipList()
    it_list = list.get_head()
    it_all = all_doc.get_head()

    while it_all is not None and it_list is not None:
        if it_all.val == it_list.val:
            it_all = it_all.next
            it_list = it_list.next
        elif it_all.val < it_list.val:
            res.add_val(it_all.val)
            it_all = it_all.next
        elif it_all.val > it_list.val:
            raise RuntimeError

    while it_all is not None:
        res.add_val(it_all.val)
        it_all = it_all.next
    assert it_list is None

    return res
