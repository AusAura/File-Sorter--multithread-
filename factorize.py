from multiprocessing import Pool, current_process, cpu_count
from time import time
import logging

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

numbers_to_check = range(10_651_060)

def factorize_sync(numbers: list) -> list:
    timer = time()
    perfect_numbers = {}
    for number1 in numbers:
        if number1 == 0:
            continue
        perfect_numbers[number1] = []
        for number2 in numbers_to_check:
            if number2 == 0:
                continue
            if number1 % number2 == 0:
                perfect_numbers[number1].append(number2)
    
    delta_time =  time() - timer
    return perfect_numbers, delta_time

perfect_numbers = {}

def factorize_multipr(number: int) -> list:
    logger.debug(f"pid={current_process().pid}, number={number}")
    if number == 0:
        perfect_numbers[0] = 0
        return perfect_numbers
    
    perfect_numbers[number] = []
    for number2 in numbers_to_check:
        if number2 == 0:
                continue
        if number % number2 == 0:
            perfect_numbers[number].append(number2)
        
    return perfect_numbers

if __name__ == '__main__':
    result = factorize_sync(numbers_to_check)
    print("SYNC NUMBERS: ", result[0])
    sync_res = f"SYNC RESULT: {result[1]}"

    with Pool(processes=cpu_count()) as pool:
        timer = time()
        returned_dict = pool.map(factorize_multipr, numbers_to_check)
        for dict in returned_dict:
            perfect_numbers.update(dict)
        print('ASYNC NUMBERS: ', perfect_numbers)
        delta_time = time() - timer

    process_async_res = f"ASYNC RESULT WITH {cpu_count()} PROCESSES: {delta_time}"

    print(sync_res)
    print(process_async_res)