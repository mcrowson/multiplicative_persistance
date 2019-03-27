import timeit

from persistence import *
'''
recuse_time = timeit.timeit('n_to_tuple(12345678999999)', setup='from persistence import n_to_tuple')
print(n_to_tuple(12345678999999))
print(recuse_time)
recuse_time = timeit.timeit('n_to_list(12345678999999)', setup='from persistence import n_to_list')
print(n_to_list(12345678999999))
print(recuse_time)
recuse_time = timeit.timeit('simpl(12345678999999)', setup='from persistence import simpl')
print(simpl(12345678999999))
print(recuse_time)



recuse_time = timeit.timeit('reduced_steps(12345678999999)', setup='from persistence import reduced_steps')
print(reduced_steps(12345678999999))
print(recuse_time)
recuse_time = timeit.timeit('reduced_steps2(12345678999999)', setup='from persistence import reduced_steps2')
print(reduced_steps2(12345678999999))
print(recuse_time)
recuse_time = timeit.timeit('reduced_steps3(12345678999999)', setup='from persistence import reduced_steps3')
print(reduced_steps3(12345678999999))
print(recuse_time)
'''

def more_combs():
    for i, _ in enumerate(combs(200)):
        if i == 100:
            return

recuse_time = timeit.timeit('more_combs()', setup='from __main__ import more_combs')
print(recuse_time)
