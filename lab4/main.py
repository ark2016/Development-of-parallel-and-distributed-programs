import threading
import time
import random


class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork):
        threading.Thread.__init__(self)
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork

    def run(self):
        while not stop_event.is_set():
            self.think()
            self.eat()

    def think(self):
        print(f"{self.name} is thinking.")
        time.sleep(random.uniform(1, 3))  # Время размышлений

    def eat(self):
        left_fork, right_fork = self.left_fork, self.right_fork
        while True:
            left_fork.acquire(True) # Накладываем блокировку на левую вилку
            locked = right_fork.acquire(False)
            if locked:
                break
            left_fork.release() # Если не удалось взять правую вилку, освобождаем левую вилку
            print(f"{self.name} is swapping forks.")
            left_fork, right_fork = right_fork, left_fork

        self.dine()
        right_fork.release()
        left_fork.release()

    def dine(self):
        print(f"{self.name} is eating.")
        time.sleep(random.uniform(1, 3))  # Время приема пищи
        print(f"{self.name} finished eating and put down the forks.")


def main():
    global stop_event
    stop_event = threading.Event()

    N = int(input("Enter number of philosophers: "))
    forks = [threading.Lock() for _ in range(N)]
    philosophers = [Philosopher(f"Philosopher {i}", forks[i], forks[(i + 1) % N]) for i in range(N)]

    for p in philosophers:
        p.start()

    time.sleep(10)  # Контрольное время
    stop_event.set()

    for p in philosophers:
        p.join()


if __name__ == "__main__":
    main()
