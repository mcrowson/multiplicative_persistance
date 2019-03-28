import csv
import itertools as it
import logging
import multiprocessing as mp
from collections import defaultdict
from datetime import datetime
from functools import reduce
from operator import mul

STEPS_TO_FIND = 12  # Mimimum number of steps for logging messages
MINIMUM_DIGITS = 1  # Minimum digits to start analyzing
MULTI_PROCESS = False  # Multiprocessing approach. Faster for digit lengths over ~ 70, Slower for less than
# Multiprocess approach does not generate frequencies csv
MAXIMUM_NUMBERS_TO_ANALYZE = 10000000 # Only calc steps for X numbers from generator, set None to look infinitely

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fh = logging.FileHandler('out.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)

counts = defaultdict()

def combs(minimum_digits):
    # Generates ordered combinations of numbers according to a few rules
    # No 0, 1, or 5
    # No 2/3 or 2/4 or 3/3 combos
    front_numbers = '23'  # One, both, or none of these
    back_numbers = '46789'   # Unlimited amounts of all
    
    front_choices = list(range(0, len(front_numbers) + 1))

    for digit_count in it.count(minimum_digits):  # would go to infinity
        logger.info("Analyzing {} Digit Numbers".format(digit_count))
        for fc1 in front_choices:
            if fc1 > digit_count:
                break  # Off case that there are more front numbers than desired digits
            for f in it.combinations(front_numbers, fc1):
                if ('2' in f and '4' in f) or ('2' in f and '3' in f):
                    continue
                front_pieces = len(f)
                digits_to_fill = max([0, digit_count - front_pieces])
                for b in it.combinations_with_replacement(back_numbers, digits_to_fill):
                    res = f + b
                    yield ''.join(res)
        
def n_to_tuple(x):
    # Convert number into tuple of digits
    # 12345 -> (1, 2, 3, 4, 5)
    return tuple(map(int, str(x)))


def mult_all(n_tuple):
    # Multiply a tuple of numbers together
    # (1, 2, 3, 4, 5) -> 120
    return reduce(mul, n_tuple, 1)


def reduced_steps(n):
    # Calculate steps in multiplicative persistence
    steps = 0
    while n >= 10:
        steps += 1
        n_tuple = n_to_tuple(n)
        n = mult_all(n_tuple)
    return steps


def consume_queue(generator_queue):
    # For Multiprocessing=True
    # Generator that consumes items in the queue
    while True:
        item = generator_queue.get()
        if item is StopIteration: break
        yield item


def process_thread(generator_queue, process_count):
    # For Multiprocessing=True
    # Takes items from queue and counts their steps
    for item in consume_queue(generator_queue):
        steps = reduced_steps(int(item))
        if steps >= STEPS_TO_FIND:
            # Found answer, stop all consumers
            logger.info("Found {} in {} steps".format(item, steps))
            [generator_queue.put(StopIteration) for _ in range(process_count)] # Stop the consumers


def load_queue(q, p_count):
    # For Multiprocessing=True
    # Separate process for loading items in the queue
    for i, n in enumerate(combs(MINIMUM_DIGITS)):
        if i == MAXIMUM_NUMBERS_TO_ANALYZE:
            [q.put(StopIteration) for _ in range(p_count)]
            return
        q.put(int(n))


def main():
    s = datetime.now()
    logger.info("Starting at {}".format(s))
    
    if MULTI_PROCESS:
        # Multi Process
        p_count = mp.cpu_count()
        q = mp.Queue(10)  # Keep buffer of items in queue
        q_loader = mp.Process(target=load_queue, args=(q, p_count)) 

        processes = [mp.Process(target=process_thread, args=(q,p_count)) for _ in range(p_count)]
        [p.start() for p in processes]
        q_loader.start()
        
        for p in processes:
            # Wait on all processes to stop due to a find
            p.join()

        q_loader.terminate()  # End the queue loader

    else:
    
        # Single Process for debugging
        for i, n in enumerate(combs(MINIMUM_DIGITS)):
            if i == MAXIMUM_NUMBERS_TO_ANALYZE:
                break  
            steps = reduced_steps(int(n))

            
            # Create dict of dict of step counts for each digit length
            d_count = len(str(n))
            if d_count not in counts:
                counts[d_count] = defaultdict(int)
            counts[d_count][steps] += 1
            
            if steps >= STEPS_TO_FIND:
                logger.info("Found {} in {} steps".format(n, steps))
                break  # Stop looking

        '''
        Below we create a CSV of the step frequencies at different
        digit lenghts
        '''
        with open("step_frequencies.csv", 'w') as f:
            fields = ['digits'] + list(range(1, 15))
            writer = csv.writer(f)
            writer.writerow(fields)
            for k, v in counts.items():
                r = [k] + [v.get(i) for i in range(1,15)]
                writer.writerow(r)
    
    
    logger.info("Took {}".format(datetime.now() - s))


if __name__ == "__main__":
    main()
