# python-speed
Simple but effective Python benchmark. Consisting of four different benchmarks: string/memory, pi calc/math, regex and fibonacci/stack to measure overall CPU/memory performance. You can use it to measure speed of various Python versions, or to measure speed of various hosting providers. It is curious how some providers will have good CPU but bad memory throughput.

## Usage

```
git clone https://github.com/vprelovac/python-speed.git
cd python-speed
python3 bench.py
```

Lower values are better.

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


## Example: Measure different python versions

Use python-speed to measure Python 3.8 vs Python 3.7 vs pypy performance.


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

Python 3.8 is about 10% faster than 3.7. pypy is immensely faster working with stack but has slower string performance than vanilla Python.
