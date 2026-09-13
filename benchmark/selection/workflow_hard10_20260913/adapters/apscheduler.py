from copy import deepcopy
from datetime import datetime, timezone
from apscheduler.job import Job
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger


def schedule_runs(jobs, operations, *, start):
    def dt(text):
        value = datetime.fromisoformat(text.replace('Z', '+00:00'))
        if value.tzinfo is None:
            raise ValueError('timestamps must have offsets')
        return value
    def stamp(value):
        return value.astimezone(timezone.utc).isoformat() if value is not None else None
    beginning = dt(start)
    def trigger(spec):
        opts = deepcopy(spec)
        kind = opts.pop('type')
        zone = opts.pop('timezone', 'UTC')
        if kind == 'or':
            return OrTrigger([trigger(s) for s in opts['triggers']])
        for key in ('start_date', 'end_date', 'run_date'):
            if key in opts:
                opts[key] = dt(opts[key])
        if kind == 'date':
            return DateTrigger(timezone=zone, **opts)
        opts.setdefault('start_date', beginning)
        if kind == 'interval':
            return IntervalTrigger(timezone=zone, **opts)
        if kind == 'cron':
            return CronTrigger(timezone=zone, **opts)
        raise ValueError('unknown trigger')
    live = {}
    def add(row, now):
        job = Job.__new__(Job)
        job.id = row['id']
        job.trigger = trigger(row['trigger'])
        job.coalesce = row.get('coalesce', True)
        job.misfire_grace_time = row.get('grace', 1)
        job.next_run_time = None if row.get('paused', False) else job.trigger.get_next_fire_time(None, now)
        live[job.id] = job
    for row in jobs:
        if row['id'] in live:
            raise ValueError('duplicate job id')
        add(row, beginning)
    trace = []
    for op in operations:
        events = []
        kind = op['op']
        if kind == 'poll':
            now = dt(op['now'])
            due = sorted((j for j in live.values() if j.next_run_time is not None and j.next_run_time <= now),
                         key=lambda j: (j.next_run_time, j.id))
            for job in due:
                times = job._get_run_times(now)
                dispatched = times[-1:] if job.coalesce else times
                for when in dispatched:
                    missed = job.misfire_grace_time is not None and (now - when).total_seconds() > job.misfire_grace_time
                    events.append({'id': job.id, 'time': stamp(when), 'status': 'missed' if missed else 'ready'})
                following = job.trigger.get_next_fire_time(times[-1], now)
                if following is None:
                    del live[job.id]
                else:
                    job.next_run_time = following
        elif kind == 'pause':
            live[op['id']].next_run_time = None
        elif kind == 'resume':
            job = live[op['id']]
            job.next_run_time = job.trigger.get_next_fire_time(None, dt(op['now']))
            if job.next_run_time is None:
                del live[job.id]
        elif kind == 'remove':
            del live[op['id']]
        elif kind == 'replace':
            add(op['job'], dt(op['now']))
        else:
            raise ValueError('unknown operation')
        trace.append({'events': events, 'next': {k: stamp(v.next_run_time) for k, v in sorted(live.items())}})
    return trace
