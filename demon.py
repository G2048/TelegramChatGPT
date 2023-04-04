import os
import time
import sys
import argparse
import atexit


class Daemon():
    """Class for Creating and maintaining Demon process"""

    def __init__(self, pidfile):
        self.pidfile = f'/var/lock/{pidfile}d'
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
        open(self.pidfile, 'w').write(pid)
        atexit.register(self.delpid)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin,'r')
        so = open(self.stdout,'a+')
        se = open(self.stderr,'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        self.fn()


    def delpid(self):
        """Only remove pidfile"""
        os.remove(self.pidfile)


    @staticmethod
    def create_child():
        try:
            pid = os.fork()
            if pid:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('Create daemon is failed!\n')
            sys.stderr.write(f'Error: {e.errno} {e.strerror}\n')
            sys.exit(1)


    def start(self, fn):
        """You must specify a function to be called when the daemon is started"""

        self.fn = fn
        if os.path.exists(self.pidfile):
            sys.stderr.write(f'{self.pidfile} already exists. Daemon is already running!\n')
            self.stop()
        else:
            self.demonification()


    def stop(self):
        """Stop the existing daemon"""

        atexit.register(self.delpid)
        if os.path.exists(self.pidfile):
            try:
                pid = int(open(self.pidfile).read())
            except OSError as e:
                sys.stderr.write(f'Error: {e}\n')
                sys.exit(1)
        else:
            sys.stderr.write('Pid file don\'t exist!\n')
            sys.exit(1)


        try:
            os.kill(pid, 15)
            sys.stdout.write(f'Daemon with pid {pid} was terminated!\n')
        except OSError as e:
            os.kill(pid, 9)
            sys.stderr.write(f'Error {pid}\n')
            sys.stderr.write(f'Send kill -9 to process {pid}\n')
            sys.exit(1)



if __name__ == '__main__':
    RAWHELP = """Create and manipulating the Daemon process.\n
    Test running: sudo python3 daemon.py -d
    Test kill: sudo python3 daemon.py -k
    Watch daemon from log: tail -f testd.log
    """
    parser = argparse.ArgumentParser(description=RAWHELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    exgroup = parser.add_mutually_exclusive_group(required=True)
    exgroup.add_argument('-d', '--daemonize', action='store_true', help='Demonize a function')
    exgroup.add_argument('-k', '--kill', action='store', const='testd', nargs='?', help='Specify a process name...')
    args = parser.parse_args()


    import logging
    FORMAT = '%(asctime)s::%(name)s::%(levelname)s::%(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, filename='testd.log')


    def testd():
        while True:
            logging.info('Daemon is running!')
            time.sleep(5)


    if args.daemonize:
        Daemon('test').start(testd)
    else:
        Daemon(args.kill).stop()
