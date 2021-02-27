import sys
import re
from timeit import default_timer as timer
#import pandas as pd
#import numpy as np

def measure(data, pattern, num):
    
    regex = re.compile(pattern)
    matches = re.findall(regex, data)
    return matches


def numb():
 np.random.seed(42)
 size = 100
 A, B = np.random.random((size, size)), np.random.random((size, size))
 C, D = np.random.random((size * 128,)), np.random.random((size * 128,))
 E = np.random.random((int(size / 2), int(size / 4)))
 F = np.random.random((int(size / 2), int(size / 2)))
 F = np.dot(F, F.T)
 G = np.random.random((int(size / 2), int(size / 2)))

 # Matrix multiplication
 N = 7
 for i in range(N):
     np.dot(A, B)
 del A, B

 # Vector multiplication
 N = 1000
 for i in range(N):
     np.dot(C, D)
 del C, D

 # Singular Value Decomposition (SVD)
 N = 2
 for i in range(N):
     np.linalg.svd(E, full_matrices = False)
 del E

 # Cholesky Decomposition
 N = 2
 for i in range(N):
     np.linalg.cholesky(F)

 # Eigendecomposition
 for i in range(N):
     np.linalg.eig(G)
    
def fib(n):
  if n <= 1: return 1
  return fib(n - 1) + fib(n - 2)
    

def extract_Digit(nth):
    global tmp1, tmp2, acc, den, num
    tmp1 = num * nth
    tmp2 = tmp1 + acc
    tmp1 = tmp2 // den

    return tmp1


def eliminate_Digit(d):
    global acc, den, num
    acc = acc - den * d
    acc = acc * 10
    num = num * 10


def next_Term(k):
    global acc, den, num
    k2=k*2+1
    acc = acc + num * 2
    acc = acc * k2
    den = den * k2
    num = num * k


def pi(n=100):
    global tmp1, tmp2, acc, den, num

    tmp1 = 0
    tmp2 = 0

    acc = 0
    den = 1
    num = 1


    i=0
    k=0
    while i<n:
        k+=1
        next_Term(k)

        if num > acc:
            continue


        d=extract_Digit(3)
        if d!=extract_Digit(4):
            continue


        tt=chr(48+d)
        i+=1
        eliminate_Digit(d)        

def reverse_1(s):
    reversed_output = ""
    for c in s:
        reversed_output = c + reversed_output
    return reversed_output

def reverse_5(s):
    return s[::-1]
        
def strb(data):
     for i in range(0, 130):
         temp=data.lower()
         temp=temp.replace("is", "was")
         temp=reverse_1(data[1000:14250])
         temp=reverse_5(temp)

         temp='|'.join(data.split(' '))
         

print("python-speed v1.1 using python v%d.%d.%d" %(sys.version_info[0],sys.version_info[1],sys.version_info[2]))
with open("test_file") as file:
    
    total=0
    data = file.read()

#    start_time = timer()
#    for i in range(0,70):
#     numb()
#    elapsed_time = timer() - start_time
#    total+=elapsed_time
#    print('np:',str(elapsed_time * 1e3))
    
#    start_time = timer()
#    for i in range(0,300):
#     df = pd.DataFrame([x.split(';') for x in data.split('\n')])
#     df = pd.concat([df for _ in range(5)])
#     df=df.drop_duplicates()
#     df=df.dropna()
#     df=df.groupby(level=0)
#    elapsed_time = timer() - start_time
#    total+=elapsed_time
#    print('df:',str(elapsed_time * 1e3))
    
    
    start_time = timer()
    for i in range(3):
     strb(data)
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('string/mem:', str(round(elapsed_time * 1e3, 2)), 'ms')
    
    
    start_time = timer()
    pi(9300)
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('pi calc/math:',str(round(elapsed_time * 1e3, 2)), 'ms')
    

    
    start_time = timer()
    for i in range(0, 120):
        # Email
        f=measure(data, '[\w\.+-]+@[\w\.-]+\.[\w\.-]+', i)

        # URI
        g=measure(data, '[\w]+://[^/\s?#]+[^\s?#]+(?:\?[^\s#]*)?(?:#[^\s]*)?', i)

        # IP
        h=measure(data, '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])', i)
    
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('regex:',str(round(elapsed_time * 1e3, 2)), 'ms')
    

    start_time = timer()	
    fib(35)
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('fibonnaci/stack: ',str(round(elapsed_time * 1e3, 2)), 'ms')
    
    print('\ntotal: ', str(round(total * 1e3, 2)), 'ms (lower is better)')
