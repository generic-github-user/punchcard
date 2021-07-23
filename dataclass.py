#!/usr/bin/env python
# coding: utf-8

# # Punchcard

# ## Introduction

# This toolkit provides flexible and efficient data structures that abstract common manipulations, providing mappings, serialization, restructuring, convenience methods/wrappers, memoization, and more. Numerous convenience methods and data processing utilities are integrated into the class and universally accessible.
# 
# The core motivation is reducing the headaches often faced when iterating (and executing functions) over deeply nested and/or irregular data structures, which often results in boilerplate code and poorly standardized/optimized subroutines. The tools included in punchcard aim for brevity, intuitiveness, and developer productivity.
# 
# It is also designed to be highly computationally efficient, delegating operations to vectorized libraries like NumPy when doing so will provide a clear speedup. Some other optimizations planned or currently in progress include:
# 
#  - Automatic memoization/caching for every (or nearly every) function that is easy to work with out-of-the-box but can be fully tweaked and customized
#  - Just-in-time (JIT) compilation for repetitive operations on large data structures
#  - Meta-optimizers and meta-heuristics that select appropriate algorithms and third-party tools for a specific type of problem (e.g., search operations, data processing, dynamic programming)
#  - Storing generators in place of realized data/values when possible, and attempting to infer generators otherwise
#  - If possible, using online algorithms that only require a small subset of the entire dataset to be stored in memory at any given time during evaluation (e.g., $max(x_0 \dots x_n)$ only needs to store $x_i$ and the current largest value)
#  - Automatically restructuring internal representations of the data to facilitate more efficient computing of results
#  - Allowing fine-tuning of time-complexity and space-complexity tradeoff (as well as other similar high-level decisions), and handling the choice automatically when no particular direction is given
# 
# The main tool is the `DataObject` class, a high-level wrapper that stores, manipulates, and interfaces with data. It includes a thorough set of data structure-agnostic operations and functions. Compatibility with NumPy and similar libraries will be integrated to the maximum possible extent.
# 
# Some planned features include:
# 
#  - Interactive exploration (and manipulation) of data structures and specific datasets
#  - Integration with Matplotlib, Seaborn, quickplot, and other visualization tools
#  - Handling of highly complex data structures, such as ones containing circular references and nonuniform nesting

# In[641]:


import string
import operator
import uuid
import requests
import pprint
import math
import itertools
import functools
import numpy as np
from IPython import display
import copy
from bs4 import BeautifulSoup
import zlib
import sys


# In[12]:


# A()+dx
# display.display_html('<h2>Test</h2>', raw=True)
display.Math(
    str([f'{i}x' for i in range(0, 10)]).replace("'", ''),
#     raw=True
)

# datatype standardization + compact representations of data structures/schemas?
# todo: data compression by algorithmic encoding (e.g., storing the integers 1 to 1 million as the iterator that generates that set of numbers)
# todo: add support for "sparse" data structures that store indices and some values instead of all values 


# In[1393]:


class Cache:
    def __init__(self):
        self.entries = {}


# In[1394]:


class DataObject:
    itertypes = [list, tuple]
#     Global cache, mainly for generators
    cache = Cache()
    def __init__(self, data, generator=None, dtype=None):
        self.data = data
        self.view = data
        self.cache = Cache()
#         function caching handler? - generate functions at init time or dynamically look up
        self.generator = generator
        
        if dtype:
            self.dtype = dtype
        else:
            self.dtype = type(self.data).__name__
        
        if type(self.data) in dx.itertypes:
            self.hash = self.hash_list(self.data)
        elif type(self.data) is np.ndarray:
#             self.hash = hash(self.data.tostring())
            self.hash = hash(self.data.tobytes())
        else:
            self.hash = hash(self.data)
        self.id = uuid.uuid4().hex
dx = DataObject


# In[1395]:


range(100).stop


# In[1396]:


# This is intended to be used as a decorator on class methods of the DataObject class
# Applying it to a given function (e.g., using the @dMethod syntax) will assign a reference to that function in the DataObject class

# why does this only work when memoization is disabled?
def dMethod(func, aliases=[]):
    if type(aliases) is str:
        aliases = [aliases]
    for name in [func.__name__[1:]] + aliases:
        setattr(DataObject, name, func)
#         setattr(DataObject, name, func.__get__(dx))
#         def class_method
    return func
# todo: add memoize parameter to parametrized decorator
def memoize(func):
    print(f'Wrapping function: {func}')
#     @functools.wraps
    def wrapper(self, *inputs, **namedinputs):
#         print(f'Wrapper inputs: {inputs, namedinputs}', self)
#         hash_value = hash(tuple(map(tuple, [func]+list(inputs))))
        dx_state = [self.data, self.generator]
        hash_value = hash(tuple(map(repr, [func] + dx_state + list(inputs))))
    # dynamic/granular memoization?
        if hash_value in self.cache.entries:
            print(f'Value cached at {hash_value}')
            return self.cache.entries[hash_value]
        else:
            print('No value cached for these inputs; evaluating...')
            result = func(self, *inputs, **namedinputs)
            print(f'Storing computed value at {hash_value}')
            self.cache.entries[hash_value] = result
            return result
    wrapper.__name__ = func.__name__
    return wrapper


# In[1517]:


repr(np.random.normal(0, 1, [5, 5]))


# In[1487]:


def memoize_static(func):
    def wrapper(*inputs, **namedinputs):
#         hash_value = hash(tuple(map(tuple,[func]+list(inputs))))
        hash_value = hash(tuple(map(repr, [func]+list(inputs))))
        if hash_value in dx.cache.entries:
            return dx.cache.entries[hash_value]
        else:
            result = func(*inputs, **namedinputs)
            dx.cache.entries[hash_value] = result
            return result
    wrapper.__name__ = func.__name__
    return wrapper


# In[1399]:


# Decorator "factory" that generates the actual (parametrized) decorator applied to the function; see https://stackoverflow.com/questions/10176226/how-do-i-pass-extra-arguments-to-a-python-decorator for a more detailed explanation
def dMethod_(*params, **namedparams):
    def method_decorator(func):
        return dMethod(func, *params, **namedparams)
    return method_decorator

# meta-decorators


# In[1400]:


functools.wraps


# In[1401]:


@dMethod
@memoize
def mhash_list(self, x):
    h = sum(hash(y) if type(y) not in [list] else self.hash_list(y) for y in x)
    return h
# make sure to update dependent methods


# In[1402]:


q = dx([])


# In[1403]:


# order of decorators?
@dMethod
# @functools.wraps
@memoize
def mcast(self, dtype):
    if type(self.data) in dx.itertypes:
        return dx(list(map(dtype, self.data)))
    else:
        return dx(dtype(self.data))


# In[1405]:


# id(f.cast)


# In[1406]:


id(mcast)


# In[1408]:


# f.hash_list


# In[1409]:


# dx.mcast


# In[1411]:


# mcast(f, int)


# In[1413]:


# f.cache.entries


# In[1414]:


f = dx([])
f
# #### string

# In[1416]:


@dMethod_(aliases=['str', 'stringify'])
@memoize
def mstring(self, plain=False, **kwargs):
    format_options = dict(indent=4, compact=True, width=30)
    format_options |= kwargs
    if plain:
        return pprint.pformat(self.data, **format_options)
    else:
        info = {
            'dtype': self.dtype,
            'data': self.data,
            'generator': self.generator
        }
    #         pprint.pformat()
    #         pprint.pformat(b, indent=4)
    #         json.dumps(b, indent=4)

        rep = '\n'.join(f'{a}: {pprint.pformat(b, **format_options)}' for a, b in info.items())
        return rep
# In[1436]:


@dMethod
def mmp(self, F, *args, **kwargs):
    print(F, args)
    tempfunc = lambda z: F(z, *args, **kwargs)
    self.data = list(map(tempfunc, self.data))
    return self
