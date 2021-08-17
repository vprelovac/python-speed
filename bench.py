import sys
import re
from timeit import default_timer as timer
from itertools import repeat
from math import sqrt
from multiprocessing import Pool


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

def reverse_recursion(s):
    if len(s) == 0:
        return s
    else:
        return reverse_recursion(s[1:]) + s[0]
        
def reverse_5(s):
    return s[::-1]
        
def strb(data):
     for i in range(0, 130):
         temp=data.lower()
         temp=data.replace("is", "was").replace("1","2")
         temp=reverse_1(data[1000:13250])
         temp=reverse_recursion(reverse_recursion(data[1000:1800]))
         temp=reverse_5(data)
         temp='|'.join(data.split(' '))
         
def mat():
 X = [[12,7,3],
    [4 ,5,6],
    [7 ,8,9]]
    # 3x4 matrix
 Y = [[5,8,1,2],
    [6,7,3,0],
    [4,5,9,1]]
 result = [[0,0,0,0],
         [0,0,0,0],
         [0,0,0,0]]
 for x in range(10000):        
  for i in range(len(X)):
   # iterate through columns of Y
   for j in range(len(Y[0])):
       # iterate through rows of Y
       for k in range(len(Y)):
           result[i][j] += X[i][k] * Y[k][j]
   result = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*Y)] for X_row in X]          
 return result                  

def eval_A(i, j):
    ij = i + j
    return ij * (ij + 1) // 2 + i + 1


def A_sum(u, i):
    return sum(u_j / eval_A(i, j) for j, u_j in enumerate(u))


def At_sum(u, i):
    return sum(u_j / eval_A(j, i) for j, u_j in enumerate(u))


def multiply_AtAv(u):
    r = range(len(u))

    tmp = pool.starmap(
        A_sum,
        zip(repeat(u), r)
    )
    return pool.starmap(
        At_sum,
        zip(repeat(tmp), r)
    )
    
    
def mp_test():
    n = int(500)
    u = [1] * n

    for _ in range(10):
        v = multiply_AtAv(u)
        u = multiply_AtAv(v)

    vBv = vv = 0

    for ue, ve in zip(u, v):
        vBv += ue * ve
        vv  += ve * ve

    result = sqrt(vBv/vv)

if __name__ == '__main__':       
  print("python-speed v1.3 using python v%d.%d.%d" %(sys.version_info[0],sys.version_info[1],sys.version_info[2]))
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
    pi(9000)
    mat()
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('pi calc/math:',str(round(elapsed_time * 1e3, 2)), 'ms')
    

    
    start_time = timer()
    for i in range(0, 125):
        # Email
        f=measure(data, '[\w\.+-]+@[\w\.-]+\.[\w\.-]+', i)

        # URI
        g=measure(data, '[\w]+://[^/\s?#]+[^\s?#]+(?:\?[^\s#]*)?(?:#[^\s]*)?', i)

        # IP
        h=measure(data, '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])', i)
        
        d=measure(data, '^(?:[^cfdrp].*|.[^a].*|..[^n].*|.{4,}|.{0,2})$',i)
    
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('regex:',str(round(elapsed_time * 1e3, 2)), 'ms')
    

    start_time = timer()	
    fib(34)
    fib(32)
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('fibonnaci/stack: ',str(round(elapsed_time * 1e3, 2)), 'ms')
    
    start_time = timer()
    with Pool(processes=4) as pool:
        mp_test()
    elapsed_time = timer() - start_time
    total+=elapsed_time
    print('multiprocess:', str(round(elapsed_time * 1e3, 2)), 'ms')
    
    
    
    print('\ntotal: ', str(round(total * 1e3, 2)), 'ms (lower is better)')
