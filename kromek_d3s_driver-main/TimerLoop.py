import datetime
import time

# A Very Simple even loop where the only events are timeouts.


def _empty_func(name, now):
    print("firing empty cb for " + name + " at time " + str(now))
    return False


class TimerLoop(object):
    def __init__(self):
        self.handlers = {}
        self.default_period = 1
        self.loop_count = 0
        self.last_tick = datetime.datetime.now()

    def addHandler(self, func, period, sid=None):
        if not sid:
            sid = "handler_" + str(len(self.handlers.keys()) + 1)
        if not func:
            func = _empty_func
        if not period:
            period = self.default_period

        handler = {
            "sid": sid,
            "func": func,
            "period": datetime.timedelta(seconds=period),
            "last_success": datetime.datetime.fromtimestamp(0),
            "last_attempt": datetime.datetime.fromtimestamp(0),
        }

        self.handlers[sid] = handler
        return sid

    def removeHandler(self, sid):
        if not sid:
            return False
        if sid not in self.handlers:
            return False
        del self.handlers[sid]
        return True

    def tick(self):
        now = datetime.datetime.now()

        request_stop = False
        for sid in self.handlers:
            period = self.handlers[sid]["period"]
            last = self.handlers[sid]["last_success"]
            if (now - last) > period:
                func = self.handlers[sid]["func"]
                try:
                    frv = func(sid, now)
                    self.handlers[sid]["last_success"] = now
                    if frv and isinstance(frv, bool):
                        request_stop = request_stop or frv

                except Exception as e:
                    print("Exception calling callback for " + sid)
                    print(e)

                self.handlers[sid]["last_attempt"] = now
        self.loop_count += 1
        self.last_tick = now

        return request_stop

    def run(self, tick_len=0.5):
        running = True
        while running:
            stop = self.tick()
            if stop:
                running = False
            time.sleep(tick_len)
