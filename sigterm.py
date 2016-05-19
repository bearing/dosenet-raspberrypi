import sys
import signal

def handler(signum, frame):
    print 'Shutting down...'
    sys.exit(1)


signal.signal(signal.SIGTERM, handler)
