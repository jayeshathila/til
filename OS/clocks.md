# Type of clocks in linux
There are roughly two type of clocks in most OS.
1. CLOCK_MONOTONIC
2. CLOCK_REALTIME

## CLOCK_MONOTONIC
It is a Clock that cannot be set and represents monotonic time since some unspecified starting point. This clock should be used for calculating elapsed time.

## CLOCK_REALTIME
It is a Clock that is more human readable. It keeps on adjusting itself to offset for physical errors in machine's clock with NTP servers. One flaw with these clocks is that it can jump forward and if used to compute elapsed time you might get negative time. (Future has gone).

## Usage
If your application is time difference sensitive you might want to use monotonic clock else realtime one.
> In JAVA `System.nanoTime()` resembles monotonic clock and `System.currentTimeMillis()` resembles realtime clock.

> In python you can use `time.clock_gettime(time.CLOCK_MONOTONIC)` or `time.clock_gettime(time.CLOCK_REALTIME)`
