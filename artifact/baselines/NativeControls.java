import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Isolated native-control contracts, not a candidate controller or JDBC harness. */
public class NativeControls {
    static final class Lease implements AutoCloseable {
        final Semaphore permits;
        final AtomicBoolean closed = new AtomicBoolean();
        Lease(Semaphore permits) { this.permits = permits; }
        public void close() { if (closed.compareAndSet(false, true)) permits.release(); }
    }
    static final class FixedAdmission {
        final Semaphore permits;
        FixedAdmission(int capacity) {
            if (capacity <= 0) throw new IllegalArgumentException("capacity");
            permits = new Semaphore(capacity, true);
        }
        Lease tryEnter() { return permits.tryAcquire() ? new Lease(permits) : null; }
    }
    static final class PoolOnly {
        final Semaphore permits;
        PoolOnly(int capacity) {
            if (capacity <= 0) throw new IllegalArgumentException("capacity");
            permits = new Semaphore(capacity, true);
        }
        Lease borrow() throws InterruptedException { permits.acquire(); return new Lease(permits); }
    }
    static void check(boolean ok, String name) {
        if (!ok) throw new AssertionError(name);
        System.out.println("PASS " + name);
    }
    public static void main(String[] args) throws Exception {
        FixedAdmission fixed = new FixedAdmission(2);
        Lease a = fixed.tryEnter(), b = fixed.tryEnter();
        check(a != null && b != null && fixed.tryEnter() == null, "fixed_rejects_above_capacity");
        a.close(); a.close();
        Lease c = fixed.tryEnter();
        check(c != null && fixed.tryEnter() == null, "lease_close_idempotent");
        b.close(); c.close();
        check(fixed.permits.availablePermits() == 2, "fixed_releases_all_capacity");
        PoolOnly pool = new PoolOnly(1);
        Lease occupied = pool.borrow();
        CompletableFuture<Lease> borrowed = new CompletableFuture<>();
        Thread waiter = new Thread(() -> {
            try { borrowed.complete(pool.borrow()); }
            catch (InterruptedException e) { borrowed.completeExceptionally(e); }
        }, "pool-waiter");
        waiter.start();
        // The held permit makes completion impossible; no timing measurement is used.
        check(!borrowed.isDone() && pool.permits.availablePermits() == 0, "pool_exhaustion_retains_waiter");
        occupied.close();
        Lease handedOff = borrowed.get(5, TimeUnit.SECONDS);
        waiter.join(5000);
        check(!waiter.isAlive() && pool.permits.availablePermits() == 0, "platform_thread_pool_handoff");
        handedOff.close();
        check(pool.permits.availablePermits() == 1, "pool_restores_capacity");
        Thread.currentThread().interrupt();
        boolean interrupted = false;
        try { pool.borrow(); } catch (InterruptedException expected) { interrupted = true; }
        check(interrupted && pool.permits.availablePermits() == 1, "interrupted_borrow_does_not_leak");
        check(CompletableFuture.completedFuture(3).thenApply(x -> x + 1).join() == 4,
              "completion_stage_smoke_not_reactive_framework");
        for (int capacity : new int[]{0, -1}) {
            boolean fixedRejected = false, poolRejected = false;
            try { new FixedAdmission(capacity); } catch (IllegalArgumentException e) { fixedRejected = true; }
            try { new PoolOnly(capacity); } catch (IllegalArgumentException e) { poolRejected = true; }
            check(fixedRejected && poolRejected, "invalid_capacity_" + capacity);
        }
        System.out.println("SUMMARY 10 checks passed; no benchmark or virtual-thread test executed");
    }
}
