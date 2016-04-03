#!/usr/bin/env python

from collections import defaultdict
from multiprocessing import Pool
import os
import time

def main():
  num_requests = 1
  start_time = time.time()
  results = defaultdict(int)

  pool = Pool(1)
  results_list = pool.map_async(send_request, range(num_requests))
  pool.close()
  pool.join()

  print 'Took', time.time() - start_time, 'secs to submit', num_requests, 'requests'
  for r in results_list.get():
    results[r] += 1

  for k in sorted(results):
    print results[k], k


def send_request(n):
  pass

print 'starting'
while True:
  main()
  break
  print 'sleep 1'
  time.sleep(0.2)
