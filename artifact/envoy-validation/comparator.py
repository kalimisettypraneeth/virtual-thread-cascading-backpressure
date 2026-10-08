"""Reduced Envoy-derived deterministic aggregate-boundary state comparator.

Original Python adaptation of pinned Apache-2.0 source (see provenance.json).
This is modified/reimplemented logic, not the upstream controller or proxy.
Histogram outputs and timer firings are explicit inputs; no CAS concurrency.
"""
from math import sqrt


class Comparator:
    def __init__(self, config):
        self.config = config
        self.sampling = not config.get('fixed_rtt', 0)
        self.limit = config['sampling_concurrency'] if self.sampling else config['minimum']
        self.deferred = 0
        self.minimum_rtt = config.get('fixed_rtt', 0)
        self.epoch = 0
        self.streak = 0
        self.recovery_due = False
        self.requests = {}
        self.samples = []
        self.blocked = 0
        self.gradient = None
        self.now = 0
        self.result = 'initialized'
        if self.sampling:
            self.enter(0)
        else:
            self.update(self.limit)

    @property
    def active(self):
        return self.deferred != 0

    def update(self, value):
        old = self.limit
        self.limit = value
        self.streak = self.streak + 1 if not self.active and old == value == self.config['minimum'] else 0
        if self.sampling and self.streak >= 5:
            self.recovery_due = True

    def enter(self, now):
        if not self.sampling:
            raise ValueError('fixed RTT cannot enter sampling')
        if self.active:
            self.result = 'already-sampling'
            return
        self.deferred = self.limit
        self.update(min(self.limit, self.config['sampling_concurrency']))
        self.samples.clear()
        self.epoch = now

    def window(self, event):
        if self.active:
            self.result = 'sampling-noop'
            return
        if not self.samples:
            self.result = 'empty-noop'
            return
        rtt = event['aggregate']
        if rtt <= 0:
            raise ValueError('positive aggregate required')
        self.samples.clear()
        self.gradient = max(0.5, min(2., self.minimum_rtt * (1 + self.config['buffer']) / rtt))
        scaled = self.limit * self.gradient
        self.update(max(self.config['minimum'], min(self.config['maximum'], int(scaled + sqrt(scaled)))))

    def step(self, event):
        self.result = 'ok'
        op = event['event']
        if 'now' in event:
            if event['now'] < self.now:
                raise ValueError('time moved backwards')
            self.now = event['now']
        if op == 'admit':
            key = event['id']
            if key in self.requests:
                raise ValueError('duplicate live request ID')
            if event.get('health', False) or not event.get('enabled', True):
                self.result = 'bypass'
            elif len(self.requests) >= self.limit:
                self.blocked += 1
                self.result = 'block'
            else:
                self.requests[key] = self.now
                self.result = 'forward'
        elif op in ('complete', 'destroy'):
            start = self.requests.pop(event['id'], None)
            if start is None:
                # Adapter guard, not an upstream controller guarantee.
                self.result = 'already-finished'
            elif op == 'complete':
                if start < self.epoch:
                    self.result = 'stale-excluded'
                else:
                    self.samples.append(self.now - start)
                    if self.active and len(self.samples) >= self.config['request_count']:
                        self.minimum_rtt = event['aggregate']
                        if self.minimum_rtt <= 0:
                            raise ValueError('positive aggregate required')
                        self.samples.clear()
                        self.update(self.deferred)
                        self.deferred = 0
        elif op == 'enter':
            self.enter(self.now)
        elif op == 'window':
            self.window(event)
        elif op == 'fire_recovery':
            if not self.recovery_due:
                raise ValueError('no pending recovery')
            self.recovery_due = False
            self.enter(self.now)
        elif op == 'repeat_window':
            # Shorthand for sequential admit/complete/window, not direct state injection.
            for i in range(event['count']):
                key = f'repeated-{i}'
                self.step({'event': 'admit', 'id': key, 'now': self.now})
                assert self.result == 'forward'
                self.step({'event': 'complete', 'id': key, 'now': self.now + event['aggregate']})
                self.step({'event': 'window', 'aggregate': event['aggregate']})
        else:
            raise ValueError(op)
        return self.snapshot()

    def snapshot(self):
        return dict(limit=self.limit, active=self.active, deferred=self.deferred,
                    minimum_rtt=self.minimum_rtt, epoch=self.epoch, streak=self.streak,
                    recovery_due=self.recovery_due, outstanding=len(self.requests),
                    samples=len(self.samples), blocked=self.blocked,
                    gradient=self.gradient, result=self.result)
