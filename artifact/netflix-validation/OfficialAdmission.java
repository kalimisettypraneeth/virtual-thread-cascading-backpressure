import com.netflix.concurrency.limits.Limiter;
import com.netflix.concurrency.limits.limit.Gradient2Limit;
import com.netflix.concurrency.limits.limiter.SimpleLimiter;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/** Original adapter around official API. A terminal event owns exactly one upstream callback. */
public final class OfficialAdmission {
    final AtomicLong clock=new AtomicLong();
    final AtomicInteger success=new AtomicInteger(),error=new AtomicInteger(),cancel=new AtomicInteger();
    final SimpleLimiter<Object> limiter=SimpleLimiter.newBuilder().limit(Gradient2Limit.newBuilder()
        .initialLimit(2).minLimit(2).maxConcurrency(2).queueSize(0).build())
        .nanoClock(()->clock.addAndGet(1000000)).build();
    public Lease acquire(){return limiter.acquire(null).map(Lease::new).orElse(null);}
    public final class Lease {
        final Limiter.Listener listener;final AtomicBoolean ended=new AtomicBoolean();
        Lease(Limiter.Listener listener){this.listener=listener;}
        public void success(){if(ended.compareAndSet(false,true)){success.incrementAndGet();listener.onSuccess();}}
        public void error(){if(ended.compareAndSet(false,true)){error.incrementAndGet();listener.onDropped();}}
        public void cancel(){if(ended.compareAndSet(false,true)){cancel.incrementAndGet();listener.onIgnore();}}
    }
    public void assertRestored(){
        if(limiter.getInflight()!=0)throw new AssertionError("inflight leak");
        Lease a=acquire(),b=acquire(),c=acquire();
        if(a==null||b==null||c!=null)throw new AssertionError("capacity not exactly two");
        a.cancel();b.cancel();
        if(limiter.getInflight()!=0)throw new AssertionError("probe leak");
    }
}
