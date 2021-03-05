# python-speed
Simple but effective Python benchmark. python-speed uses four different benchmarks: string/memory, pi calc/math, regex and fibonacci/stack to give the full picture about CPU/memory performance. python-speed tests the performance of a single CPU.

You can use it to measure speed of various Python versions, or to measure speed of various hosting providers. It may uncover weak links - some providers having good CPU but bad memory throughput.

## Usage

```
git clone https://github.com/vprelovac/python-speed.git
cd python-speed
python3 bench.py
```

The output will be time needed to do different tests (in ms). Lower values are better.

## Example: hosting showdown


Using python-speed to benchmark different hosting providers. All instances running Ubuntu 20.04 LTS and python 3.8 was default. 

DigitalOcean $6/mo AMD
```
python3 bench.py 
string: 5200.982441000178
pi calc: 2586.3461019998795
regex: 2393.028546000096
fibonnaci generate:  2007.9667189997963

total:  12188.32380799995
```

DigitalOcean $6/mo Intel
```
python3 bench.py 
string: 11556.846907000363
pi calc: 2780.3279120003026
regex: 2951.313669999763
fibonnaci generate:  2506.3611700002184

total:  19794.849659000647
```

DigitalOcean $5/mo
```
python3 bench.py 
string: 13145.982636000099
pi calc: 3260.851814000034
regex: 3409.4889729999522
fibonnaci generate:  2955.1533290000407

total:  22771.476752000126
```


Linode $5/mo
```
python3 bench.py 
string: 3441.8879259999926
pi calc: 3530.859902000003
regex: 4446.7015299999985
fibonnaci generate:  4629.420477000011

total:  16048.869835000005
```

UpCloud $5/mo
```
python3 bench.py 
string: 1495.373236000006
pi calc: 2604.472407000003
regex: 2679.8153320000038
fibonnaci generate:  2099.722478000018

total:  8879.383453000031
```


## Example: Measure performance of different python versions

Use python-speed to measure Python 2.7 vs Python 3.7 vs Python 3.8 vs pypy performance.


```
python2 bench.py 

python-speed v1.1 using python 2.7.18
('string/mem:', '1331.3', 'ms')
('pi calc/math:', '2823.0', 'ms')
('regex:', '1895.65', 'ms')
('fibonnaci/stack: ', '2283.49', 'ms')
('\ntotal: ', '8333.43', 'ms (lower is better)')


python3.7 bench.py 

python-speed v1.1 using python 3.7.0
string/mem: 3234.91 ms
pi calc/math: 2750.48 ms
regex: 3383.7 ms
fibonnaci/stack:  2434.09 ms

total:  11803.17 ms (lower is better)



python3.8 bench.py 

python-speed v1.1 using python 3.8.5
string/mem: 3173.93 ms
pi calc/math: 2728.48 ms
regex: 2764.86 ms
fibonnaci/stack:  2320.35 ms

total:  10987.62 ms (lower is better)

pypy bench.py 

python-speed v1.1 using python 3.7.9
string/mem: 4056.55 ms
pi calc/math: 3164.39 ms
regex: 1953.89 ms
fibonnaci/stack:  142.2 ms

total:  9317.03 ms (lower is better)

```

We see interesting evolution of Python. Python 2.7 is still fastest overall thanks to superior string/regex performance. Python 3.8 is about 10% faster than 3.7. Pypy is immensely faster working with stack but has slower string performance than vanilla Python.

Edit 03/04/2021: Pypy maintainer responded to the benchmark, and patched pypy. As a result, the latest pypy nightly has better string performance.
