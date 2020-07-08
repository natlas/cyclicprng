# CyclicPRNG

A cyclical PRNG implementation that can provably generate every number in the cycle exactly once before restarting. For more information on why this was built and how it works, see the corresponding [natlas documentation](https://github.com/natlas/natlas/wiki/Host-Coverage-Scanning-Strategy).

## Mathematical Background

In short, CyclicPRNG uses a multiplicative cyclic group of prime order, and computes the factorization of the order of the group to obtain possible subgroup orders. CyclicPRNG uses these subgroup orders for generator testing, and finds random generators. CyclicPRNG uses these generators to determine the order to traverse the cycle.

## Installation

```bash
pipenv install cyclicprng
```

## Usage

### Initializing a Reordering PRNG

```python
from cyclicprng import CyclicPRNG
cycle_size = 10
c = CyclicPRNG(cycle_size)
first_cycle = [c.get_random() for _ in range(cycle_size)]
second_cycle = [c.get_random() for _ in range(cycle_size)]
assert first_cycle != second_cycle
```

### Initializing a Consistent PRNG

```python
from cyclicprng import CyclicPRNG
cycle_size = 10
c = CyclicPRNG(cycle_size, consistent=True)
first_cycle = [c.get_random() for _ in range(cycle_size)]
second_cycle = [c.get_random() for _ in range(cycle_size)]
assert first_cycle == second_cycle
```

### Registering Event Handlers

CyclicPRNG allows you to register event handlers to receive messages when the PRNG restarts. Optionally, an event handler could be provided at initialization to also receive an `init` event.

The two events emitted by CyclicPRNG are: `init` and `restart`.

```python
>>> from cyclicprng import CyclicPRNG
>>> cycle_size = 5
>>> c = CyclicPRNG(cycle_size, event_handler=print)
init
>>> for i in range(cycle_size):
...     print(c.get_random())
...
2
3
1
5
restart
4
>>> c.unregister_event_handler(print)
>>> c.notify
[]
>>> c.register_event_handler(print)
>>> c.notify
[<built-in function print>]
>>> c.clear_event_handlers()
>>> c.notify
[]
```

You may notice that the `restart` event triggers before the last value is returned. This happens because the cycle automatically restarts when it reaches the final value in the cycle, right before that value is returned to the caller.

### Edge Cases

The following edge cases exist for CyclicPRNG:

* `size < 1` -> Raise ValueError
* `size = 1` -> Always return 1
* `size = 2` -> The generator is always 2 (equivalent to consistent=true)

## Performance

I've included these performance numbers based on tests on my development desktop. As such, they may not be indicative of performance on your machine.

### Initialization

On my desktop, CyclicPRNG repeatedly initializes with a size of 2^128 (the size of the IPv6 address space) in 0.03-0.04 seconds. I've included results from 10 sample inits below.

```python
>>> import timeit
>>> ip6_timer = timeit.Timer(
...         "CyclicPRNG(340282366920938463463374607431768211456)",
...         setup="from cyclicprng import CyclicPRNG",
...     )
>>>
>>> ip6_timer.repeat(10, 1)
[0.03722329996526241, 0.0364310999866575, 0.03413929999805987, 0.034686600090935826, 0.03407520009204745, 0.033979699946939945, 0.034076200099661946, 0.03446660004556179, 0.03457159991376102, 0.03437739983201027]
```

### Getting The Next Number

In a similar test, 10 subsequent calls to `get_random()` all measured in the range of `3e-6` to `7e-6` (3 to 7 microseconds). This would iterate the entire IPv4 address space (2^32) in a little over 8 hours.

```python
>>> random_timer = timeit.Timer(
...     "c.get_random()",
...     setup="from cyclicprng import CyclicPRNG; c=CyclicPRNG(340282366920938463463374607431768211456)"
... )
>>> random_timer.repeat(10, 1)
[5.499925464391708e-06, 7.0999376475811005e-06, 5.600042641162872e-06, 6.4999330788850784e-06, 5.499925464391708e-06, 4.200031980872154e-06, 6.200047209858894e-06, 6.7998189479112625e-06, 5.899928510189056e-06, 3.00002284348011e-06]
```

## Testing

CyclicPRNG uses pytest for testing. You can run tests yourself by cloning this repo and setting up like so:

```bash
git clone https://github.com/natlas/cyclicprng.git
cd cyclicprng/
pipenv install --dev
pipenv run pytest tests.py
```

## License

```text
   Copyright 2020 The Natlas Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
