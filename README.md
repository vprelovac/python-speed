# python-bench
Simple but effective Python benchmark. Use it to measure speed of various Python versions, or to measure speed of various hosting providers.

## Usage

```
python bench.py
```

## Examples

Use python-bench to measure that Python 3.8 is about 10% faster than 3.7. pypy is immensely faster working with stack but has slower string performance than vanilla Python.

```
python3.7 bench.py 

string: 2670.0545439962298
pi calc: 2536.7995460983366
regex: 3206.1590410303324
fibonnaci generate:  2416.4477509912103

total:  10829.46088211611


python3.8 bench.py 

string: 2533.86879095342
pi calc: 2524.6768220094964
regex: 2537.656887085177
fibonnaci generate:  2285.8045920729637

total:  9882.007092121057


pypy3.7 bench.py

string: 6090.247004991397
pi calc: 2811.791994026862
regex: 2218.3589100604877
fibonnaci generate:  132.45823606848717

total:  11252.856145147234

```
