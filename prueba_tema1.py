

def sum_1(n,i,A):
    if i <= n:
        return sum_1(n,i+1,A+(i+1))
    else:
        return A
    
def sum_2(n,A):
    if n > 0:
        return sum_2(n-1,A+n)
    else:
        return A
    
def fibonnaci_1(n, i, A1, A2):
    if n>i:
        return fibonnaci_1(n,i+1,A2,A1+A2)
    else:
        return A2
    
def fibonnaci_2(n,A1,A2):
    if n>0:
        return fibonnaci_2(n-1,A2,A1+A2)
    else:
        return A1

print(sum_1(5,0,0))
print(sum_2(5,0))
print(fibonnaci_1(5,0,0,1))
print(fibonnaci_2(5,0,1))