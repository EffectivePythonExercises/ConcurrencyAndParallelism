import os
import time
import subprocess
from rich import print


def run_subprocess(*args):
    print(args)
    result = subprocess.run(args, capture_output=True, encoding='utf-8')

    result.check_returncode()
    print('result.stdout'.center(50, '='))
    print(f'{result.stdout}')


def poll_subprocess():
    proc = subprocess.Popen(['sleep', '1'])
    while proc.poll() is None:
        time.sleep(.1)
        print('Working...')

    print(f'Task end. Status: {proc.poll()}')


def multiple_subprocess_open():
    start = time.monotonic()
    sleep_procs = []
    for _ in range(10):
        proc = subprocess.Popen(['sleep', '1'])
        sleep_procs.append(proc)

    for proc in sleep_procs:
        proc.communicate()

    end = time.monotonic()
    delta = end - start
    print(f'Jobs have completed in: {delta: .3}')


def run_encrypt(data):
    env = os.environ.copy()
    env['password'] = 'zxkcjvl43jr90asjgl;kxzcvjbl;zxkvcjlk'
    proc = subprocess.Popen(
        'openssl enc -pbkdf2 -pass env:password'.split(' '),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    proc.stdin.write(data)
    proc.stdin.flush()
    return proc


def test_encrypt_data():
    procs = []
    for _ in range(10):
        data = os.urandom(10)
        proc = run_encrypt(data)
        procs.append(proc)

    for proc in procs:
        out, _ = proc.communicate()
        print(out)


def run_hash(input_stdin):
    return subprocess.Popen(
        'openssl dgst -whirlpool -binary'.split(' '),
        stdin=input_stdin,
        stdout=subprocess.PIPE
    )


def test_run_hash():
    encrypt_procs = []
    hash_procs = []
    for _ in range(10):
        data = os.urandom(100)

        encrypt_proc = run_encrypt(data)
        encrypt_procs.append(encrypt_proc)

        hash_proc = run_hash(encrypt_proc.stdout)
        hash_procs.append(hash_proc)

        # 자식이 입력 스트림에 들어오는 데이터를 소비하고 communicate() 메서드가
        # 불필요하게 자식으로부터 오는 입력을 훔쳐가지 못하게 만든다.
        # 또한 다운스트림 프로세스가 죽으면 SIGPIPE를 upstream 프로세스에 전달한다
        encrypt_proc.stdout.close()
        encrypt_proc.stdout = None

    for proc in encrypt_procs:
        proc.communicate()
        assert proc.returncode == 0
    for proc in hash_procs:
        out, _ = proc.communicate()
        print(out)


def set_timeout_to_child_processes():
    proc = subprocess.Popen(['sleep', '10'])
    try:
        proc.communicate(timeout=0.1)
    except subprocess.TimeoutExpired:
        proc.terminate()  # SIGTERM -15 (Exit code 143)
        proc.wait()

    print(f'Task end. Status: {proc.poll()}')
