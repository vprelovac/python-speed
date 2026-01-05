"""
python-speed: A benchmark suite for comparing Python performance.

Usage:
    python bench.py                    # Run all benchmarks with defaults
    python bench.py --runs 10          # 10 iterations per benchmark
    python bench.py --benchmark pi,fib # Run only pi and fibonacci
    python bench.py --json             # Output JSON for automation
    python bench.py --factor 2.0       # Scale workload (default 1.0)
"""

import argparse
import gc
import json
import platform
import re
import sys
from dataclasses import dataclass, field
from math import sqrt
from multiprocessing import Pool, cpu_count
from pathlib import Path
from statistics import mean, median, stdev
from timeit import default_timer as timer

VERSION = "2.0"
DEFAULT_RUNS = 3
DEFAULT_WARMUP = 1
DEFAULT_FACTOR = 1.0


@dataclass
class BenchmarkResult:
    """Holds timing data for a single benchmark."""

    name: str
    times: list[float] = field(default_factory=list)

    @property
    def mean_ms(self) -> float:
        return mean(self.times) * 1000 if self.times else 0.0

    @property
    def std_ms(self) -> float:
        return stdev(self.times) * 1000 if len(self.times) > 1 else 0.0

    @property
    def min_ms(self) -> float:
        return min(self.times) * 1000 if self.times else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.times) * 1000 if self.times else 0.0

    @property
    def median_ms(self) -> float:
        return median(self.times) * 1000 if self.times else 0.0

    def to_dict(self) -> dict:
        return {
            "mean": round(self.mean_ms, 2),
            "std": round(self.std_ms, 2),
            "min": round(self.min_ms, 2),
            "max": round(self.max_ms, 2),
            "median": round(self.median_ms, 2),
            "runs": len(self.times),
        }


def run_benchmark(
    func: callable,
    runs: int = DEFAULT_RUNS,
    warmup: int = DEFAULT_WARMUP,
    quiet: bool = False,
) -> BenchmarkResult:
    """Run a benchmark function multiple times with warmup and GC control."""
    name = func.__name__.replace("bench_", "")

    if not quiet:
        print(f"{name}: ", end="", flush=True)

    # Warmup runs (discarded)
    for i in range(warmup):
        if not quiet:
            print("w", end="", flush=True)
        func()

    # Timed runs
    times = []
    for i in range(runs):
        if not quiet:
            print(".", end="", flush=True)
        gc.collect()
        gc.disable()
        try:
            start = timer()
            func()
            elapsed = timer() - start
            times.append(elapsed)
        finally:
            gc.enable()

    if not quiet:
        print(f" {mean(times) * 1000:.1f} ms")

    return BenchmarkResult(name=name, times=times)


# =============================================================================
# String/Memory Benchmark
# =============================================================================


def reverse_loop(s: str) -> str:
    """Reverse string by character iteration."""
    result = ""
    for c in s:
        result = c + result
    return result


def reverse_recursive(s: str) -> str:
    """Reverse string recursively."""
    if len(s) == 0:
        return s
    return reverse_recursive(s[1:]) + s[0]


def reverse_slice(s: str) -> str:
    """Reverse string with slice."""
    return s[::-1]


def create_bench_string(data: str, factor: float):
    """Factory for string benchmark."""
    iterations = int(factor * 160)

    def bench_string():
        for _ in range(iterations):
            _ = data.lower()
            _ = data.replace("is", "was").replace("1", "2")
            _ = reverse_loop(data[1000:13250])
            _ = reverse_recursive(reverse_recursive(data[1000:1800]))
            _ = reverse_slice(data)
            _ = "|".join(data.split(" "))

    return bench_string


# =============================================================================
# Pi Calculation Benchmark (Bailey-Borwein-Plouffe)
# =============================================================================


def compute_pi(n: int) -> None:
    """Compute n digits of pi using the BBP spigot algorithm."""
    acc = 0
    den = 1
    num = 1

    i = 0
    k = 0
    while i < n:
        k += 1
        # next_term
        k2 = k * 2 + 1
        acc = acc + num * 2
        acc = acc * k2
        den = den * k2
        num = num * k

        if num > acc:
            continue

        # extract_digit(3)
        tmp = (num * 3 + acc) // den
        # extract_digit(4)
        tmp2 = (num * 4 + acc) // den

        if tmp != tmp2:
            continue

        # eliminate_digit
        acc = (acc - den * tmp) * 10
        num = num * 10
        i += 1


def mat_multiply(iterations: int):
    """Matrix multiplication benchmark."""
    x = [[12, 7, 3], [4, 5, 6], [7, 8, 9]]
    y = [[5, 8, 1, 2], [6, 7, 3, 0], [4, 5, 9, 1]]

    for _ in range(iterations):
        result = [
            [sum(a * b for a, b in zip(x_row, y_col)) for y_col in zip(*y)]
            for x_row in x
        ]
    return result


def create_bench_math(factor: float):
    """Factory for math benchmark (pi + matrix multiplication)."""
    digits = int(factor * 3750)
    mat_iterations = int(factor * 4000)

    def bench_math():
        compute_pi(digits)
        mat_multiply(mat_iterations)

    return bench_math


# =============================================================================
# Regex Benchmark
# =============================================================================

REGEX_PATTERNS = [
    r"[\w\.+-]+@[\w\.-]+\.[\w\.-]+",  # Email
    r"[\w]+://[^/\s?#]+[^\s?#]+(?:\?[^\s#]*)?(?:#[^\s]*)?",  # URL
    r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])",  # IP
    r"^(?:[^cfdrp].*|.[^a].*|..[^n].*|.{4,}|.{0,2})$",  # Custom
]


def create_bench_regex(data: str, factor: float):
    """Factory for regex benchmark."""
    iterations = int(factor * 30)
    # Pre-compile patterns
    compiled = [re.compile(p) for p in REGEX_PATTERNS]

    def bench_regex():
        for _ in range(iterations):
            for regex in compiled:
                re.findall(regex, data)

    return bench_regex


# =============================================================================
# Fibonacci/Recursion Benchmark
# =============================================================================


def fib(n: int) -> int:
    """Naive recursive fibonacci - tests call stack performance."""
    if n <= 1:
        return 1
    return fib(n - 1) + fib(n - 2)


def create_bench_fib(factor: float):
    """Factory for fibonacci benchmark."""
    n1 = int(factor * 33)
    n2 = int(factor * 31)

    def bench_fib():
        fib(n1)
        fib(n2)

    return bench_fib


# =============================================================================
# Multiprocessing Benchmark (Spectral Norm)
# =============================================================================


def eval_a(i: int, j: int) -> float:
    """Element of the infinite matrix A."""
    ij = i + j
    return ij * (ij + 1) // 2 + i + 1


def a_sum(args: tuple) -> float:
    """Compute sum for A*v."""
    u, i = args
    return sum(u_j / eval_a(i, j) for j, u_j in enumerate(u))


def at_sum(args: tuple) -> float:
    """Compute sum for A^T*v."""
    u, i = args
    return sum(u_j / eval_a(j, i) for j, u_j in enumerate(u))


def multiply_atav(pool: Pool, u: list) -> list:
    """Compute A^T * A * v using multiprocessing."""
    r = range(len(u))
    tmp = pool.map(a_sum, [(u, i) for i in r])
    return pool.map(at_sum, [(tmp, i) for i in r])


def spectral_norm(pool: Pool, n: int) -> float:
    """Compute spectral norm approximation."""
    u = [1.0] * n

    for _ in range(10):
        v = multiply_atav(pool, u)
        u = multiply_atav(pool, v)

    vbv = vv = 0.0
    for ue, ve in zip(u, v):
        vbv += ue * ve
        vv += ve * ve

    return sqrt(vbv / vv)


def create_bench_multiprocess(factor: float, pool: Pool):
    """Factory for multiprocessing benchmark."""
    n = int(factor * 450)

    def bench_multiprocess():
        spectral_norm(pool, n)

    return bench_multiprocess


# =============================================================================
# Dictionary Benchmark
# =============================================================================


def create_bench_dict(factor: float):
    """Factory for dictionary operations benchmark."""
    size = int(factor * 65000)
    lookup_iterations = int(factor * 265)

    def bench_dict():
        # Creation via comprehension
        d = {i: i * 2 for i in range(size)}

        # Lookups
        for _ in range(lookup_iterations):
            for k in range(0, size, 10):
                _ = d[k]

        # Iteration
        for _ in range(lookup_iterations):
            for k, v in d.items():
                _ = k + v

        # Update/merge
        d2 = {i: i * 3 for i in range(size // 2, size + size // 2)}
        d.update(d2)

        # Deletion
        for k in list(d.keys())[::2]:
            del d[k]

    return bench_dict


# =============================================================================
# List Benchmark
# =============================================================================


def create_bench_list(factor: float):
    """Factory for list operations benchmark."""
    size = int(factor * 85000)
    iterations = int(factor * 85)

    def bench_list():
        for _ in range(iterations):
            # Append
            lst = []
            for i in range(size):
                lst.append(i)

            # Sort
            lst.sort(reverse=True)

            # Comprehension with filter
            lst = [x * 2 for x in lst if x % 3 == 0]

            # Extend
            lst.extend(range(1000))

            # Pop from end
            while len(lst) > 100:
                lst.pop()

            # Insert at beginning (expensive)
            for i in range(50):
                lst.insert(0, i)

    return bench_list


# =============================================================================
# Object/Class Benchmark
# =============================================================================


class _BenchPoint:
    """Simple class for benchmarking object operations."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def dot(self, other: "_BenchPoint") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z


class _BenchPointNoSlots:
    """Class without __slots__ for comparison."""

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


def create_bench_object(factor: float):
    """Factory for object/class operations benchmark."""
    size = int(factor * 6400)
    iterations = int(factor * 64)

    def bench_object():
        for _ in range(iterations):
            # Object creation (with slots)
            points = [_BenchPoint(i, i + 1, i + 2) for i in range(size)]

            # Attribute access
            total = 0.0
            for p in points:
                total += p.x + p.y + p.z

            # Method calls
            for p in points:
                _ = p.magnitude()

            # Object interaction
            for i in range(len(points) - 1):
                _ = points[i].dot(points[i + 1])

            # Creation without slots (different memory pattern)
            points2 = [_BenchPointNoSlots(i, i, i) for i in range(size // 2)]
            for p in points2:
                _ = p.x

    return bench_object


# =============================================================================
# Float Benchmark (Mandelbrot-inspired)
# =============================================================================


def create_bench_float(factor: float):
    """Factory for floating point operations benchmark."""
    width = int(factor * 400)
    height = int(factor * 300)
    max_iter = int(factor * 400)

    def bench_float():
        # Mandelbrot-like computation (heavy float ops)
        for y in range(height):
            for x in range(width):
                # Map to complex plane
                c_re = (x - width / 2) * 4 / width
                c_im = (y - height / 2) * 4 / height

                z_re, z_im = 0.0, 0.0
                for _ in range(max_iter):
                    if z_re * z_re + z_im * z_im > 4.0:
                        break
                    # z = z^2 + c
                    z_re, z_im = z_re * z_re - z_im * z_im + c_re, 2 * z_re * z_im + c_im

    return bench_float


# =============================================================================
# JSON Benchmark
# =============================================================================


def create_bench_json(factor: float):
    """Factory for JSON serialization benchmark."""
    import json as json_module

    size = int(factor * 1200)
    iterations = int(factor * 200)

    # Create test data structure
    test_data = [
        {
            "id": i,
            "name": f"item_{i}",
            "active": i % 2 == 0,
            "score": i * 1.5,
            "tags": [f"tag_{j}" for j in range(5)],
            "metadata": {"created": i * 1000, "updated": i * 1000 + 500},
        }
        for i in range(size)
    ]

    def bench_json():
        for _ in range(iterations):
            # Serialize
            s = json_module.dumps(test_data)
            # Deserialize
            _ = json_module.loads(s)

    return bench_json


# =============================================================================
# Exception Handling Benchmark
# =============================================================================


def create_bench_except(factor: float):
    """Factory for exception handling benchmark.

    Tests:
    - try/except overhead when no exception raised (happy path)
    - try/except overhead when exceptions ARE raised (hot path exceptions)
    - Exception creation and propagation cost
    - Nested exception handlers
    """
    iterations_no_raise = int(factor * 5000000)
    iterations_raise = int(factor * 800000)
    iterations_nested = int(factor * 250000)

    class CustomError(Exception):
        pass

    def might_raise(do_raise: bool):
        if do_raise:
            raise CustomError("error")
        return 42

    def bench_except():
        # 1. Happy path - no exceptions raised
        # Tests SETUP_FINALLY/POP_BLOCK bytecode overhead
        total = 0
        for i in range(iterations_no_raise):
            try:
                total += i
            except Exception:
                pass

        # 2. Hot path exceptions - exceptions in tight loop
        # Major variance between CPython versions and PyPy
        count = 0
        for _ in range(iterations_raise):
            try:
                might_raise(True)
            except CustomError:
                count += 1

        # 3. Nested exception handlers
        for _ in range(iterations_nested):
            try:
                try:
                    try:
                        raise CustomError("inner")
                    except CustomError:
                        raise CustomError("middle")
                except CustomError:
                    raise CustomError("outer")
            except CustomError:
                pass

        # 4. Exception with traceback capture
        for _ in range(iterations_nested):
            try:
                raise ValueError("with traceback")
            except ValueError:
                pass

    return bench_except


# =============================================================================
# Generator/Iterator Benchmark
# =============================================================================


def create_bench_generator(factor: float):
    """Factory for generator and iterator benchmark.

    Tests:
    - Generator function overhead
    - Generator expressions vs list comprehensions
    - itertools chains
    - Lazy vs eager evaluation
    - yield from delegation
    """
    from itertools import chain, filterfalse, islice, takewhile

    size = int(factor * 50000)
    iterations = int(factor * 80)

    def count_up(n: int):
        """Simple generator."""
        i = 0
        while i < n:
            yield i
            i += 1

    def transform_chain(iterable):
        """Generator with yield from."""
        yield from (x * 2 for x in iterable)
        yield from (x * 3 for x in iterable)

    def nested_generators(n: int):
        """Deeply nested generator delegation."""
        if n <= 0:
            yield 0
        else:
            yield from nested_generators(n - 1)
            yield n

    def bench_generator():
        for _ in range(iterations):
            # 1. Basic generator consumption
            total = 0
            for x in count_up(size):
                total += x

            # 2. Generator expression vs list comprehension
            # Generator (lazy)
            gen = (x * 2 for x in range(size))
            total = sum(gen)

            # 3. itertools chain operations
            a = range(size // 3)
            b = range(size // 3)
            c = range(size // 3)
            total = sum(chain(a, b, c))

            # 4. itertools with predicates
            total = sum(takewhile(lambda x: x < size // 2, range(size)))
            total = sum(islice(filterfalse(lambda x: x % 2, range(size)), size // 4))

            # 5. yield from delegation
            total = sum(transform_chain(range(size // 4)))

            # 6. Nested yield from (tests delegation depth)
            total = sum(nested_generators(100))

    return bench_generator


# =============================================================================
# Big Integer Benchmark
# =============================================================================


def create_bench_bigint(factor: float):
    """Factory for arbitrary precision integer benchmark.

    Tests:
    - Large integer arithmetic (Python's unlimited precision)
    - Factorial computation
    - Large prime operations
    - Bit manipulation on big ints
    """
    factorial_n = int(factor * 1200)
    iterations = int(factor * 150)
    prime_bits = int(factor * 1024)

    def factorial(n: int) -> int:
        """Compute n! iteratively."""
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def is_probable_prime(n: int, k: int = 10) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Test with first k primes as witnesses
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][:k]
        for a in witnesses:
            if a >= n:
                continue
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def bench_bigint():
        for _ in range(iterations):
            # 1. Factorial - creates very large integers
            f = factorial(factorial_n)

            # 2. Operations on large factorials
            _ = f // (10**100)
            _ = f % (10**50)

            # 3. Multiplication of large integers
            _ = f * f

            # 4. Bit operations on big ints
            _ = f >> 1000
            _ = f & ((1 << 2048) - 1)
            _ = f | (1 << 3000)

            # 5. Modular exponentiation (used in crypto)
            base = 2**256 + 12345
            exp = 2**128
            mod = 2**521 - 1  # Mersenne prime
            _ = pow(base, exp, mod)

            # 6. Primality testing with big numbers
            candidate = (1 << prime_bits) + 12345
            _ = is_probable_prime(candidate)

            # 7. Integer division and modulo on large numbers
            divisor = 10**200 + 7
            _ = f // divisor
            _ = f % divisor

    return bench_bigint


# =============================================================================
# Async/Await Benchmark
# =============================================================================


def create_bench_async(factor: float):
    """Factory for asyncio benchmark.

    Tests:
    - Coroutine creation and execution overhead
    - Task switching performance
    - asyncio.gather concurrency
    - Async iteration
    - Event loop overhead
    """
    import asyncio

    iterations = int(factor * 7500)
    task_count = int(factor * 5000)
    gather_size = int(factor * 250)
    async_iter_size = int(factor * 50000)

    async def noop_coro():
        """Minimal coroutine - measures creation/scheduling overhead."""
        return 1

    async def chain_coro(n: int) -> int:
        """Chain of awaits - measures await overhead."""
        if n <= 0:
            return 0
        return n + await chain_coro(n - 1)

    async def yield_control():
        """Yield to event loop."""
        await asyncio.sleep(0)

    class AsyncCounter:
        """Async iterator for testing async for loops."""

        def __init__(self, n: int):
            self.n = n
            self.i = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.i >= self.n:
                raise StopAsyncIteration
            self.i += 1
            return self.i

    class AsyncContextManager:
        """Async context manager for testing async with."""

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    async def run_async_benchmark():
        # 1. Raw coroutine creation and execution
        for _ in range(iterations):
            coro = noop_coro()
            await coro

        # 2. Chained awaits (measures await dispatch)
        for _ in range(iterations // 10):
            await chain_coro(50)

        # 3. Task creation and gathering
        for _ in range(iterations // 20):
            tasks = [asyncio.create_task(noop_coro()) for _ in range(gather_size)]
            await asyncio.gather(*tasks)

        # 4. Task switching via sleep(0)
        for _ in range(task_count):
            await yield_control()

        # 5. Async iteration
        total = 0
        async for val in AsyncCounter(async_iter_size):
            total += val

        # 6. Async context managers
        for _ in range(iterations):
            async with AsyncContextManager():
                pass

        # 7. Mixed workload - simulates real async code patterns
        async def worker(n: int) -> int:
            await asyncio.sleep(0)
            return n * 2

        for _ in range(iterations // 40):
            tasks = [asyncio.create_task(worker(i)) for i in range(gather_size // 2)]
            results = await asyncio.gather(*tasks)

    def bench_async():
        asyncio.run(run_async_benchmark())

    return bench_async


# =============================================================================
# Set Operations Benchmark
# =============================================================================


def create_bench_set(factor: float):
    """Factory for set operations benchmark.

    Tests:
    - Set creation and membership testing
    - Union, intersection, difference, symmetric_difference
    - Set comprehensions
    - Frozen sets
    """
    size = int(factor * 25000)
    iterations = int(factor * 50)
    membership_tests = int(factor * 100000)

    def bench_set():
        for _ in range(iterations):
            # 1. Set creation
            s1 = set(range(size))
            s2 = set(range(size // 2, size + size // 2))

            # 2. Membership testing (O(1) average)
            count = 0
            for i in range(membership_tests):
                if i in s1:
                    count += 1

            # 3. Set operations
            union = s1 | s2
            intersection = s1 & s2
            difference = s1 - s2
            sym_diff = s1 ^ s2

            # 4. In-place operations
            s3 = set(range(size))
            s3 |= set(range(size, size + 1000))
            s3 &= set(range(500, size + 500))
            s3 -= set(range(600, 700))

            # 5. Set comprehension
            s4 = {x * 2 for x in range(size) if x % 3 == 0}

            # 6. Subset/superset checks
            small = set(range(100))
            _ = small <= s1
            _ = s1 >= small
            _ = small.isdisjoint(set(range(size, size + 100)))

            # 7. Frozen set (hashable, usable as dict key)
            fs1 = frozenset(range(1000))
            fs2 = frozenset(range(500, 1500))
            _ = fs1 | fs2
            _ = fs1 & fs2

            # 8. Set of tuples (common pattern)
            pairs = {(i, i + 1) for i in range(size // 10)}
            _ = (50, 51) in pairs

    return bench_set


# =============================================================================
# System Info
# =============================================================================


def get_system_info() -> dict:
    """Collect system information."""
    return {
        "platform": platform.system().lower(),
        "arch": platform.machine(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_impl": platform.python_implementation(),
        "cpu_count": cpu_count(),
    }


# =============================================================================
# Output Formatters
# =============================================================================


def format_console(results: list[BenchmarkResult], config: dict, system: dict) -> str:
    """Format results for console output."""
    lines = []

    # Header
    header = (
        f"python-speed v{VERSION} | "
        f"Python {system['python_version']} ({system['python_impl']}) | "
        f"{system['platform']} {system['arch']} | "
        f"{system['cpu_count']} cores"
    )
    lines.append(header)
    lines.append(
        f"Config: {config['runs']} runs, {config['warmup']} warmup, factor={config['factor']}"
    )
    lines.append("")

    # Results - show median (robust) and min (best case)
    name_width = max(len(r.name) for r in results)
    lines.append(f"{'benchmark'.ljust(name_width)}  {'median':>9}  {'± std':>8}  {'min':>9}  {'max':>9}")
    lines.append("-" * (name_width + 42))

    for r in results:
        name = r.name.ljust(name_width)
        lines.append(
            f"{name}  {r.median_ms:8.1f}  ± {r.std_ms:5.1f}  {r.min_ms:8.1f}  {r.max_ms:8.1f}"
        )

    # Total
    total_median = sum(r.median_ms for r in results)
    total_std = sqrt(sum(r.std_ms**2 for r in results))
    total_min = sum(r.min_ms for r in results)
    total_max = sum(r.max_ms for r in results)

    lines.append("-" * (name_width + 42))
    lines.append(
        f"{'total'.ljust(name_width)}  {total_median:8.1f}  ± {total_std:5.1f}  {total_min:8.1f}  {total_max:8.1f}  ms"
    )
    lines.append("")
    lines.append("(lower is better, min = best run)")

    return "\n".join(lines)


def format_json(results: list[BenchmarkResult], config: dict, system: dict) -> str:
    """Format results as JSON."""
    output = {
        "version": VERSION,
        "system": system,
        "config": config,
        "benchmarks": {r.name: r.to_dict() for r in results},
        "total": {
            "mean": round(sum(r.mean_ms for r in results), 2),
            "std": round(sqrt(sum(r.std_ms**2 for r in results)), 2),
        },
    }
    return json.dumps(output, indent=2)


# =============================================================================
# Main
# =============================================================================

AVAILABLE_BENCHMARKS = [
    "string",
    "math",
    "regex",
    "fib",
    "dict",
    "list",
    "object",
    "float",
    "json",
    "except",
    "generator",
    "bigint",
    "async",
    "set",
    "multiprocess",
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Python performance benchmark suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Number of timed runs per benchmark (default: {DEFAULT_RUNS})",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=DEFAULT_WARMUP,
        help=f"Number of warmup runs (default: {DEFAULT_WARMUP})",
    )
    parser.add_argument(
        "--factor",
        type=float,
        default=DEFAULT_FACTOR,
        help=f"Workload scaling factor (default: {DEFAULT_FACTOR})",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default=None,
        help=f"Comma-separated list of benchmarks to run. Available: {', '.join(AVAILABLE_BENCHMARKS)}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (total only)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine which benchmarks to run
    if args.benchmark:
        selected = [b.strip() for b in args.benchmark.split(",")]
        invalid = set(selected) - set(AVAILABLE_BENCHMARKS)
        if invalid:
            print(f"Error: Unknown benchmarks: {', '.join(invalid)}", file=sys.stderr)
            print(f"Available: {', '.join(AVAILABLE_BENCHMARKS)}", file=sys.stderr)
            sys.exit(1)
    else:
        selected = AVAILABLE_BENCHMARKS

    # Load test data
    script_dir = Path(__file__).parent
    test_file = script_dir / "test_file"
    if not test_file.exists():
        print(f"Error: Test data file not found: {test_file}", file=sys.stderr)
        sys.exit(1)
    data = test_file.read_text()

    # Collect system info
    system = get_system_info()

    # Config for output
    config = {
        "runs": args.runs,
        "warmup": args.warmup,
        "factor": args.factor,
    }

    results = []
    # Suppress progress for JSON output
    quiet_progress = args.json

    # Run selected benchmarks
    if "string" in selected:
        bench = create_bench_string(data, args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "math" in selected:
        bench = create_bench_math(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "regex" in selected:
        bench = create_bench_regex(data, args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "fib" in selected:
        bench = create_bench_fib(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "dict" in selected:
        bench = create_bench_dict(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "list" in selected:
        bench = create_bench_list(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "object" in selected:
        bench = create_bench_object(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "float" in selected:
        bench = create_bench_float(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "json" in selected:
        bench = create_bench_json(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "except" in selected:
        bench = create_bench_except(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "generator" in selected:
        bench = create_bench_generator(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "bigint" in selected:
        bench = create_bench_bigint(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "async" in selected:
        bench = create_bench_async(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "set" in selected:
        bench = create_bench_set(args.factor)
        results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    if "multiprocess" in selected:
        # Pool created OUTSIDE timing
        with Pool(processes=4) as pool:
            bench = create_bench_multiprocess(args.factor, pool)
            results.append(run_benchmark(bench, args.runs, args.warmup, quiet_progress))

    # Output results
    if args.json:
        print(format_json(results, config, system))
    elif args.quiet:
        total = sum(r.mean_ms for r in results)
        print(f"{total:.1f} ms")
    else:
        print()  # Blank line after progress
        print(format_console(results, config, system))


if __name__ == "__main__":
    main()
