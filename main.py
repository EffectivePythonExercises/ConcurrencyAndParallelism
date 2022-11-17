from cnp.subprocesses import (
    run_subprocess,
    poll_subprocess,
    multiple_subprocess_open,
    test_encrypt_data,
    test_run_hash,
    set_timeout_to_child_processes
)
from cnp.use_threads import (
    test_vanilla_elapsed_factorize,
    test_threaded_elapsed_factorize,
    call_slow_systemcall
)
from cnp.use_lock import (run_thread_counter, run_thread_locking_counter)
from cnp.use_queue import (
    commence_task_flow,
    commence_task_flow_with_queue,
    commence_task_flow_with_queue_cleaner,
)
from cnp.conway.grid import (
    test_count_neighbors, test_game_logic, test_step_cell, test_column_printer
)
from cnp.conway.lockinggrid import test_column_printer_with_threading
from cnp.conway.queuedgrid import test_column_printer_with_queue
from cnp.conway.queuedlockinggrid import test_column_printer_with_phased_pipeline
from cnp.conway.threadpoolgrid import test_column_printer_with_pool
from cnp.conway.asyncgrid import test_column_printer_with_asyncio

from cnp.asyncio_porting.guess import main as guess_main
from cnp.asyncio_porting.async_guess import run_main_async

def run_many_subprocesses():
    cmdline_argsets = (
        ('echo', 'Hello world from child process!'), ('cat', '/etc/resolv.conf'),
        'ls -lah'.split(' ')
    )

    for carg in cmdline_argsets:
        run_subprocess(*carg)


def subprocesses():
    run_many_subprocesses()
    poll_subprocess()
    multiple_subprocess_open()
    test_encrypt_data()
    test_run_hash()
    set_timeout_to_child_processes()


def use_threads():
    test_vanilla_elapsed_factorize()

    test_threaded_elapsed_factorize()


def use_locks():
    run_thread_counter()
    run_thread_locking_counter()


def use_queue():
    commence_task_flow()
    commence_task_flow_with_queue()
    commence_task_flow_with_queue_cleaner()


def conway_grid():

    # test_count_neighbors()
    # test_game_logic()
    # test_step_cell()

    # test_column_printer()
    # test_column_printer_with_threading(err_redirection=True)
    # test_column_printer_with_queue()
    # test_column_printer_with_phased_pipeline()
    test_column_printer_with_pool()
    # test_column_printer_with_asyncio()

def asyncio_porting():
    # guess_main()
    run_main_async()
    

if __name__ == '__main__':
    # subprocesses()
    # call_slow_systemcall()

    # use_threads()

    # use_queue()

    # conway_grid()

    asyncio_porting()