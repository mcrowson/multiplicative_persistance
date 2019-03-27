from functools import reduce, lru_cache
import itertools as it
import multiprocessing as mp
from operator import mul
from datetime import datetime
import logging

STEPS_TO_FIND = 11
MINIMUM_DIGITS = 1

MULTI_PROCESS = False

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

def combs(minimum_digits):
    # Generate numeric combinations accirding to pattern '^(2{0,1}3{0,1}6{0,1}7*8*9*|3{0,1}4{0,1}6{0,1}7*8*9*)$'
    # Smaller search area than all possible numbers
    front_numbers = '2346'
    back_numbers = '789' 
    
    #min_l = max([1, minimum_digits - len(front_numbers)])  # makes sure we hit all combinations of 233 including max front and back
    front_choices = list(range(0, len(front_numbers) + 1))

    for digit_count in it.count(minimum_digits):  # would go to infinity
        logger.info("Analyzing {}".format(digit_count))
        for fc1 in front_choices:
            if fc1 > digit_count:
                break

            for f in it.combinations(front_numbers, fc1):
                if '2' in f and '4' in f:
                    continue
                front_pieces = len(f)
                digits_to_fill = max([0, digit_count - front_pieces])
                for b in it.combinations_with_replacement(back_numbers, digits_to_fill):
                    res = f + b
                    yield ''.join(res)
        

@lru_cache(maxsize=2**20)  # About 1 mil, docs say to use power of 2
def n_to_tuple(x):
    # Convert number into tuple of digits
    return tuple(map(int, str(x)))


@lru_cache(maxsize=2**20)  # About 1 mil, docs say to use a power of 2
def mult_all(n_tuple):
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
    # Queue consumer generator
    while True:
        item = generator_queue.get()
        if item is StopIteration: break
        yield item


def process_thread(generator_queue, process_count):
    # Takes items from queue and processes until it finds steps
    for item in consume_queue(generator_queue):
        steps = reduced_steps(int(item))
        if steps == STEPS_TO_FIND:
            # Found answer, stop all consumers
            logger.info("Found {} in {} steps".format(item, steps))
            [generator_queue.put(StopIteration) for _ in range(process_count)] # Stop the consumers


def load_queue(q, p_count):
    for n in combs(MINIMUM_DIGITS):
        q.put(int(n))


def main():
    s = datetime.now()
    logger.info("Starting at {}".format(s))
    
    if MULTI_PROCESS:
        # Multi Process
        p_count = mp.cpu_count()
        q = mp.Queue(10)  # Keep buffer of items in queue
        q_loader = mp.Process(target=load_queue, args=(q, p_count))
        q_loader.start()

        processes = [mp.Process(target=process_thread, args=(q,p_count)) for _ in range(p_count)]
        [p.start() for p in processes]
        
        for p in processes:
            # Wait on all processes to stop due to a find
            p.join()

        q_loader.terminate()

    else:
    
        # Single Process
        for n in combs(MINIMUM_DIGITS):
            steps = reduced_steps(int(n))
            if steps == STEPS_TO_FIND:
                logger.info("Found {} in {} steps".format(n, steps))
                break
    
    
    logger.info("Took {}".format(datetime.now() - s))
    
if __name__ == "__main__":
    main()
    