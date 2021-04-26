from collections import deque


def find132pattern(nums):
    list = [[]]
    for i in range(len(nums)):
        for j in range(len(list)):
            list.append(list[j] + [nums[i]])
    for l in list:
        if len(l) == 3:
            if l[0] < l[2] < l[1]:
                print("true")
                return
    print("false")


def queue_test():
    """python队列"""
    queue = deque()
    queue.append(1)
    queue.append(2)
    print(queue.popleft())
    print(queue.popleft())


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


def tree():
    """树状结构"""
    n1 = TreeNode(1)
    n2 = TreeNode(2)
    n3 = TreeNode(3)
    n4 = TreeNode(4)
    n5 = TreeNode(5)
    n3.left = n4
    n3.right = n5
    n4.left = n1
    n4.right = n2


class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None


def reversePrint(head):
    arr = []
    while head:
        arr.append(head.val)
        head = head.next
    return arr[::-1]


class CQueue(object):
    def __init__(self):
        self.list1 = []
        self.list2 = []

    def appendTail(self, value):
        """末尾插入一条记录"""
        self.list1.append(value)

    def deleteHead(self):
        """删除开头的元素，不存在返回-1"""
        if self.list2:
            return self.list2.pop()
        if not self.list1:
            return -1
        while self.list1:
            self.list2.append(self.list1.pop())
        return self.list2.pop()


def isNumber(s: str):
    """判断是否是数值"""
    s = s.strip()
    l = len(list(s))
    if l == 0:
        return False
    f = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'e', 'E', '+', '-', '.']
    for c in s:
        if c not in f:
            return False
    if s.count('+') > 0 and not s.find('+') == 0:
        return False
    if s.count('-') > 0 and (not s.find('-') == 0 and (s.find('e-') == -1 or s.find('E-') == -1)):
        return False
    if s.count('-') > 0 and not s.find('-') == l-1:
        return False
    if s.count('e') > 1 or s.count('E') > 1 or s.count('.') > 1:
        return False
    if s.count('e') > 0 and (s.find('e') == 0 or s.find('e') == l-1):
        return False
    if s.count('E') > 0 and (s.find('E') == 0 or s.find('E') == l-1):
        return False
    if s.count('.') > 0 and s.find('.') == l-1:
        return False
    return True


def reverseList(head):
    """反转链表"""

    pass


if __name__ == "__main__":
    # find132pattern([1, 2, 3, 4, 5, 1])
    # queue_test()
    # tree()
    l1 = ListNode(1)
    l2 = ListNode(2)
    l3 = ListNode(3)
    l4 = ListNode(4)
    l5 = ListNode(5)
    l5.next = None
    l4.next = l5
    l3.next = l4
    l2.next = l3
    l1.next = l2

    l = l1
    while True:
        if l.next:
            print(l.val)
            l = l.next
        else:
            print(l.val)
            break

    while True:
        if l.next:
            print(l.val)
        else:
            print(l.val)
            break
