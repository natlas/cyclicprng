from threading import Lock
import random
import sympy
from datetime import datetime


mutex = Lock()


def modexp(b, e, m):
    bits = [(e >> bit) & 1 for bit in range(e.bit_length())]
    s = b
    v = 1
    for bit in bits:
        if bit == 1:
            v *= s
            v %= m
        s *= s
        s %= m
    return v


class CyclicPRNG:
    """
        For more information about the existence of this class and why it does what it does,
        see https://github.com/natlas/natlas/wiki/Host-Coverage-Scanning-Strategy
        Edge case behavior:
            size < 1 -> Raise ValueError
            size = 1 -> Always return 1
            size = 2 -> The generator is always 2 (equivalent to consistent=true)
    """

    size = 0
    modulus = 0
    modulus_factors = {}
    generator = 0
    start = 0
    end = 0
    current = 0
    cycle_start_time = None
    completed_cycle_count = 0
    consistent = False
    

    def __init__(
        self, cycle_size: int, consistent: bool = False, event_handler: callable = None
    ):
        """
            Initialize PRNG that restarts after cycle_size calls
        """
        self.notify = []
        self.size = cycle_size
        if self.size < 1:
            raise ValueError(
                "Random Number Generator must be given a positive non-zero integer"
            )
        if event_handler:
            self.register_event_handler(event_handler)

        self._init_cyclic_group()
        self._init_generator()
        self._init_permutation()
        self.cycle_start_time = datetime.utcnow()
        self.consistent = consistent
        self._emit_event("init")

    def register_event_handler(self, func: callable):
        """
            A simple event handler to be notified of events in the cyclic PRNG
            func must be a callable that takes a single parameter
        """
        if not callable(func):
            raise TypeError("Event handler must be callable")
        self.notify.append(func)

    def unregister_event_handler(self, func: callable):
        """
            Removes an event handler from the cyclic PRNG
        """
        if func in self.notify:
            self.notify.remove(func)

    def clear_event_handlers(self):
        """
            Clear all event handlers from the cyclic PRNG
        """
        self.notify.clear()

    def _emit_event(self, event):
        for func in self.notify:
            func(event)

    def _init_cyclic_group(self):
        def next_prime(num):
            num = num + 1 if (num % 2) == 0 else num + 2
            while not sympy.isprime(num):
                num = num + 2
            return num

        self.modulus = next_prime(self.size)
        self.modulus_factors = sympy.factorint(self.modulus - 1)

    def _init_generator(self):
        """
            Find a generator for the whole cyclic group.
        """
        found = False
        base = 0
        """
            If modulus is 3 then the only generator we can use is 2.
            Otherwise we infinite loop because always self.generator == base
        """
        if self.modulus == 3:
            self.generator = 2
            return
        while not found:
            base = random.randint(2, self.modulus - 1)
            found = self.generator != base and all(
                modexp(base, int((self.modulus - 1) / factor), self.modulus) != 1
                for factor in self.modulus_factors
            )
        self.generator = base

    def _cycle_until_in_range(self, element):
        """
            Cycle the element until it is self.size or less
        """
        while element > self.size:
            element = (element * self.generator) % self.modulus
        return element

    def _init_permutation(self):
        """
            Create a new permutation of the scope
        """
        exp = random.randint(2, self.modulus - 1)
        self.end = self._cycle_until_in_range(modexp(self.generator, exp, self.modulus))
        self.start = self._cycle_until_in_range(
            (self.end * self.generator) % self.modulus
        )
        self.current = self.start

    def _restart_cycle(self):
        """
            Restart PRNG Cycle
        """
        if self.consistent:
            self.current = self.start
        else:
            self._init_generator()
            self._init_permutation()
        self.cycle_start_time = datetime.utcnow()
        self.completed_cycle_count += 1
        self._emit_event("restart")

    def get_random(self):
        """
            Gets the next random number from the permutation
        """
        if self.size <= 1:
            return 1
        mutex.acquire()
        value = self.current
        self.current = self._cycle_until_in_range(
            (self.current * self.generator) % self.modulus
        )
        if value == self.end:
            self._restart_cycle()
        mutex.release()
        return value
