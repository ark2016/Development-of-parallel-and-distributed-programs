import threading
import random

class RWLock:
    def __init__(self):
        self._readers = 0
        self._writers = 0
        self._lock = threading.Lock()
        self._read_ok = threading.Condition(self._lock)
        self._write_ok = threading.Condition(self._lock)

    def acquire_read(self):
        with self._lock:
            # Wait until no writers
            while self._writers > 0:
                self._read_ok.wait()
            self._readers += 1

    def release_read(self):
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_ok.notify_all()

    def acquire_write(self):
        with self._lock:
            # Wait until no readers or writers
            while self._readers > 0 or self._writers > 0:
                self._write_ok.wait()
            self._writers = 1

    def release_write(self):
        with self._lock:
            self._writers = 0
            # Notify all waiting readers
            self._read_ok.notify_all()
            # Notify one waiting writer
            self._write_ok.notify_all()

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class ThreadSafeLinkedList:
    def __init__(self):
        self.head = None
        self.rwlock = RWLock()

    def contains(self, value):
        # Must be called under read lock
        cur = self.head
        while cur is not None:
            if cur.val == value:
                return True
            cur = cur.next
        return False

    def append_if_not_present(self, value):
        # First acquire read lock and check
        self.rwlock.acquire_read()
        present = self.contains(value)
        self.rwlock.release_read()
        if present:
            return
        # Now acquire write lock and check again before inserting
        self.rwlock.acquire_write()
        # Double check
        if not self.contains(value):
            # Insert at the end
            if self.head is None:
                self.head = Node(value)
            else:
                cur = self.head
                while cur.next is not None:
                    cur = cur.next
                cur.next = Node(value)
        self.rwlock.release_write()

def worker_task(lst, count):
    # Generate random numbers and try to insert if not present
    for _ in range(count):
        num = random.randint(0, 1000)
        lst.append_if_not_present(num)

if __name__ == "__main__":
    n = 4  # number of threads
    count_per_thread = 1000
    ts_list = ThreadSafeLinkedList()
    threads = []
    for i in range(n):
        t = threading.Thread(target=worker_task, args=(ts_list, count_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify no duplicates
    seen = set()
    cur = ts_list.head
    duplicates_found = False
    while cur is not None:
        if cur.val in seen:
            duplicates_found = True
            break
        seen.add(cur.val)
        cur = cur.next

    if duplicates_found:
        print("Duplicates found!")
    else:
        print("No duplicates found!")
