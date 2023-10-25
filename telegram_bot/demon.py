import os
import time
import sys
import argparse
import atexit
import signal
import logging


class Daemon():
    """Class for Creating and maintaining Demon process"""

    def __init__(self, filename):
        self.pidfile = f'/var/lock/{filename}d'
        self.stdin = '/dev/null'
        self.stdout = '/dev/null'
        self.stderr = '/dev/null'


    def demonification(self):
        """Fork, magic and run the function"""
        self.create_child()
        os.chdir('/')
        os.setsid()
        os.umask(0)
        self.create_child()
        pid = str(os.getpid())
        logging.info(f'Demon was created! Pid is: {pid}')
        open(self.pidfile, 'w').write(pid)
        logging.debug(f'{self.pidfile}')
        atexit.register(self.delpid)
        signal.signal(signal.SIGCHLD, self.handle_signal)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin,'r')
        so = open(self.stdout,'a+')
        se = open(self.stderr,'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        logging.debug(f'Start function {self.fn}')
        self.fn(*self.fn_args)


    def delpid(self):
        """Only remove pidfile"""
        try:
            os.remove(self.pidfile)
        except FileNotFoundError as e:
            logging.error(e)
            sys.stderr.write(f'{e}\n')



    @staticmethod
    def handle_signal(signum, frame):
        pass


    @staticmethod
    def create_child():
        try:
            pid = os.fork()
            if pid:
                sys.exit(0)
        except OSError as e:
            logging.error('Create daemon is failed!')
            logging.error(f'Error: {e.errno} {e.strerror}')
            sys.stderr.write('Create daemon is failed!\n')
            sys.stderr.write(f'Error: {e.errno} {e.strerror}\n')
            sys.exit(1)


    def start(self, fn, *args):
        """You must specify a function to be called when the daemon is started"""

        self.fn = fn
        self.fn_args = args
        if os.path.exists(self.pidfile):
            logging.warning(f'{self.pidfile} already exists. Daemon is already running!')
            sys.stderr.write(f'{self.pidfile} already exists. Daemon is already running!\n')
            self.stop()
        else:
            logging.debug(self.fn_args)
            self.demonification()


    def stop(self):
        """Stop the existing daemon"""

        if os.path.exists(self.pidfile):
            try:
                pid = int(open(self.pidfile).read())
            except OSError as e:
                logging.error(f'Error: {e}')
                sys.stderr.write(f'Error: {e}\n')
                sys.exit(1)
        else:
            logging.warning('Pid file don\'t exist!')
            sys.stderr.write('Pid file don\'t exist!\n')
            return -1


        try:
            os.kill(pid, 15)
            logging.warning(f'Daemon with pid {pid} was terminated!')
            sys.stdout.write(f'Daemon with pid {pid} was terminated!\n')
            self.delpid()
        except OSError as e:
            os.kill(pid, 9)
            logging.warning(f'Send kill -9 to process {pid}')
            sys.stderr.write(f'Error {pid}\n')
            sys.stderr.write(f'Send kill -9 to process {pid}\n')
            sys.exit(1)
        finally:
            if os.path.exists(f'/proc/{pid}'):
                os.kill(pid, 9)
                logging.warning(f'Send kill -9 to process {pid}')
                sys.stderr.write(f'Send kill -9 to process {pid}\n')



if __name__ == '__main__':
    RAWHELP = """Create and manipulating the Daemon process.\n
    Test running: sudo python3 daemon.py -d
    Test kill: sudo python3 daemon.py -k
    Watch daemon from log: tail -f testd.log
    """
    parser = argparse.ArgumentParser(description=RAWHELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    exgroup = parser.add_mutually_exclusive_group(required=True)
    exgroup.add_argument('-d', '--daemonize', action='store_true', help='Demonize a function')
    exgroup.add_argument('-k', '--kill', action='store', const='test', nargs='?', help='Specify a process name...')
    args = parser.parse_args()


    FORMAT = '%(asctime)s::%(name)s::%(levelname)s::%(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename='testd.log')


    def handle_signal(signum, frame):
        logging.info(f'Signal {signum} is handling!')


    def testd():
        while True:
            logging.info('Daemon is running!')
            time.sleep(5)


    signal.signal(15, handle_signal)
    if args.daemonize:
        Daemon('test').start(testd)
    else:
        Daemon(args.kill).stop()
