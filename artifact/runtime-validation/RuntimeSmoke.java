import java.nio.file.*;
import java.sql.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.lang.reflect.*;
import jdk.jfr.*;
import jdk.jfr.consumer.*;
import io.r2dbc.pool.*;
import io.r2dbc.spi.*;
import reactor.core.publisher.*;

/** Correctness smoke only. Compile with 17; VT APIs deliberately checked at runtime. */
public final class RuntimeSmoke {
    static final int K = 2, N = 12, WIDTH = 3;
    static final Duration TIMEOUT = Duration.ofSeconds(20);
    static final String SQL = "SELECT id, value FROM fixture WHERE id = ";
    static final AtomicInteger active = new AtomicInteger(), peak = new AtomicInteger();
    static final List<String> rows = Collections.synchronizedList(new ArrayList<>());
    static final Object monitor = new Object();
    @Name("validation.Scenario") @Label("Validation scenario")
    static class Scenario extends Event { String kind; int iteration; boolean virtual; }
    static boolean virtual() throws Exception {
        return (boolean) Thread.class.getMethod("isVirtual").invoke(Thread.currentThread());
    }
    static ExecutorService executor(String mode) throws Exception {
        if (mode.equals("virtual")) return (ExecutorService) Executors.class
            .getMethod("newVirtualThreadPerTaskExecutor").invoke(null);
        return Executors.newFixedThreadPool(WIDTH);
    }
    static void check(boolean ok, String detail) {
        if (!ok) throw new AssertionError(detail);
    }
    static void entered() {
        int n = active.incrementAndGet(); peak.accumulateAndGet(n, Math::max);
        check(n <= K, "finite pool exceeded: " + n);
    }
    static void result(int id, int actualId, int value) {
        check(actualId == id && value == id * 7 + 3, "request " + id + " value mismatch");
        rows.add(id + ",OK," + value);
    }
    // These adapters call the preserved reduced sources, not upstream official artifacts.
    // Constant scripted signals exercise integration, not adaptation or timing equivalence.
    static int capacity(String control) throws Exception {
        return switch (control) {
            case "fixed", "pool-only" -> K;
            case "breakwater-inspired" -> {
                var p = BreakwaterInspired.updatePool(K, 1, 1, 1, 1, .5);
                var c = BreakwaterInspired.updateClient((long)p.nextTotal(), 0, 1, K, 0);
                yield (int)c.nextUnused();
            }
            case "gradient2-reduced" -> {
                Class<?> c = Class.forName("AdaptiveControllerComparators$NetflixGradient2Step");
                Constructor<?> ctor = c.getDeclaredConstructors()[0]; ctor.setAccessible(true);
                Object instance = ctor.newInstance(K, 1, K, 1.0, 0, 1.5, 100, 1);
                Method sample = c.getDeclaredMethod("sample", double.class, int.class);
                sample.setAccessible(true); yield (int)sample.invoke(instance, 1.0, K);
            }
            case "envoy-reduced" -> {
                Method sample = AdaptiveControllerComparators.class.getDeclaredMethod("envoyStep",
                    int.class, int.class, int.class, double.class, double.class, double.class);
                sample.setAccessible(true); yield (int)sample.invoke(null, K, 1, K, 1.0, 0.0, 1.0);
            }
            default -> throw new IllegalArgumentException(control);
        };
    }
    static void jdbc(String mode, String control) throws Exception {
        ArrayBlockingQueue<java.sql.Connection> pool = new ArrayBlockingQueue<>(K);
        List<java.sql.Connection> all = new ArrayList<>();
        ExecutorService executor = executor(mode);
        try {
            for (int i=0; i<K; i++) {
                java.sql.Connection c = DriverManager.getConnection("jdbc:postgresql://db:5432/smoke?socketTimeout=20&connectTimeout=10", "smoke", "smoke");
                c.setAutoCommit(true); c.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);
                all.add(c); pool.add(c);
            }
            for (int start=0; start<N; start+=WIDTH) {
                int cap = capacity(control); check(cap == K, "scripted control capacity differs from oracle");
                NativeControls.FixedAdmission admission = new NativeControls.FixedAdmission(cap);
                List<Future<?>> futures = new ArrayList<>();
                List<NativeControls.Lease> leases = new ArrayList<>();
                // Acquire before dispatch: deterministic held-batch rejection, independent of timing.
                for (int offset=0; offset<WIDTH; offset++) leases.add(control.equals("pool-only") ? null : admission.tryEnter());
                for (int offset=0; offset<WIDTH; offset++) {
                    int id=start+offset; NativeControls.Lease lease=leases.get(offset);
                    if (!control.equals("pool-only") && lease==null) { rows.add(id+",REJECT,"); continue; }
                    futures.add(executor.submit(() -> {
                        java.sql.Connection c=null; boolean counted=false;
                        try {
                            check(virtual()==mode.equals("virtual"), "wrong JDBC thread mode");
                            c=pool.poll(TIMEOUT.toMillis(), TimeUnit.MILLISECONDS);
                            check(c!=null,"pool acquisition timeout request "+id); entered(); counted=true;
                            try (java.sql.Statement s=c.createStatement()) {
                                s.setQueryTimeout(20);
                                try(ResultSet r=s.executeQuery(SQL+id)) { check(r.next(),"missing id "+id); result(id,r.getInt(1),r.getInt(2)); check(!r.next(),"duplicate DB row "+id); }
                            }
                        } catch (Exception e) { throw new CompletionException(e); }
                        finally { if(counted) active.decrementAndGet(); if(c!=null) check(pool.offer(c),"connection returned twice"); if(lease!=null) lease.close(); }
                    }));
                }
                for (Future<?> future:futures) future.get(TIMEOUT.toSeconds(),TimeUnit.SECONDS);
                check(admission.permits.availablePermits()==cap,"admission permit leak");
            }
            check(pool.size()==K && active.get()==0,"JDBC pool leak");
        } finally {
            executor.shutdownNow(); check(executor.awaitTermination(25,TimeUnit.SECONDS),"worker cleanup timeout");
            for(java.sql.Connection c:all) c.close();
        }
    }
    static void reactive(String control) throws Exception {
        ConnectionFactory factory = ConnectionFactories.get("r2dbc:postgresql://smoke:smoke@db:5432/smoke");
        ConnectionPool pool = new ConnectionPool(ConnectionPoolConfiguration.builder(factory)
            .initialSize(K).maxSize(K).maxAcquireTime(TIMEOUT).maxCreateConnectionTime(TIMEOUT).build());
        try {
            pool.warmup().block(TIMEOUT);
            for(int start=0;start<N;start+=WIDTH) {
                int cap=capacity(control); check(cap==K,"scripted control capacity differs from oracle");
                NativeControls.FixedAdmission admission = new NativeControls.FixedAdmission(cap);
                List<NativeControls.Lease> leases = new ArrayList<>();
                for(int offset=0;offset<WIDTH;offset++) leases.add(control.equals("pool-only") ? null : admission.tryEnter());
                List<Mono<Void>> work=new ArrayList<>();
                for(int offset=0;offset<WIDTH;offset++) {
                    int id=start+offset; NativeControls.Lease lease=leases.get(offset);
                    if(!control.equals("pool-only") && lease==null) { rows.add(id+",REJECT,"); continue; }
                    Mono<Void> operation=Mono.usingWhen(pool.create(), c -> {
                        entered();
                        return Mono.from(c.setAutoCommit(true)).then(Mono.from(c.setTransactionIsolationLevel(IsolationLevel.READ_COMMITTED)))
                            .thenMany(Flux.from(c.createStatement(SQL+id).execute()))
                            .concatMap(r -> r.map((row,metadata) -> new int[]{row.get("id",Integer.class),row.get("value",Integer.class)}))
                            .single().doOnNext(v -> result(id,v[0],v[1])).then();
                    }, c -> Mono.defer(() -> {active.decrementAndGet(); return Mono.from(c.close());}),
                       (c,e) -> Mono.defer(() -> {active.decrementAndGet(); return Mono.from(c.close());}),
                       c -> Mono.defer(() -> {active.decrementAndGet(); return Mono.from(c.close());}))
                       .doOnTerminate(() -> {if(lease!=null) lease.close();});
                    work.add(operation);
                }
                Flux.merge(Flux.fromIterable(work),WIDTH).then().block(TIMEOUT);
                // Lease close is idempotent; verify restored admission after all work terminates.
                for(NativeControls.Lease lease:leases) if(lease!=null) lease.close();
                check(admission.permits.availablePermits()==cap,"reactive admission permit leak");
            }
            check(pool.getMetrics().orElseThrow().acquiredSize()==0,"reactive pool leak");
        } finally { pool.disposeLater().block(TIMEOUT); }
    }
    static native void nativeCallback();
    public static void sleepCallback() throws InterruptedException { Thread.sleep(100); }
    static void pinning(String mode, String kind, Path out) throws Exception {
        int feature=Runtime.version().feature();
        if(kind.equals("native")) System.load("/out/native/libvtpin.so");
        check(feature==21 || feature==25 || feature==24,"expected JDK21/24/25");
        check(FlightRecorder.getFlightRecorder().getEventTypes().stream().anyMatch(e->e.getName().equals("jdk.VirtualThreadPinned")),"pinning event unavailable");
        try(Recording rec=new Recording()) {
            rec.enable("jdk.VirtualThreadPinned").withThreshold(Duration.ZERO).withStackTrace();
            rec.enable("validation.Scenario"); rec.enable("jdk.VirtualThreadStart"); rec.enable("jdk.VirtualThreadEnd");
            rec.start(); ExecutorService ex=executor(mode);
            try {
                for(int i=0;i<4;i++) {
                    final int iteration=i;
                    ex.submit(()-> { try {
                        check(virtual()==mode.equals("virtual"),"wrong pin scenario thread mode");
                        Scenario marker=new Scenario(); marker.kind=kind.equals("native") ? "jni-callback-sleep" : "monitor-held-sleep";marker.iteration=iteration;marker.virtual=virtual();marker.begin();
                        if(kind.equals("native")) nativeCallback(); else synchronized(monitor) { Thread.sleep(100); }
                        marker.commit();
                    } catch(Exception e){throw new CompletionException(e);} }).get(10,TimeUnit.SECONDS);
                }
            } finally { ex.shutdownNow(); check(ex.awaitTermination(10,TimeUnit.SECONDS),"pin fixture cleanup"); }
            rec.stop(); rec.dump(out.resolve("pinning.jfr"));
        }
        long pins=0,markers=0;
        for(RecordedEvent event:RecordingFile.readAllEvents(out.resolve("pinning.jfr"))) {
            if(event.getEventType().getName().equals("jdk.VirtualThreadPinned")) pins++;
            if(event.getEventType().getName().equals("validation.Scenario")) markers++;
        }
        check(markers==4,"missing scenario execution markers");
        if(mode.equals("virtual") && (feature==21 || kind.equals("native"))) check(pins>0,"no expected pin observed; inspect JFR and environment");
        if(mode.equals("platform") || (feature>=24 && kind.equals("monitor"))) check(pins==0,"unexpected pin; inspect recorded stack/reason");
        Files.writeString(out.resolve("pinning.json"),"{\"jdk\":"+feature+",\"mode\":\""+mode+"\",\"scenario_markers\":"+markers+",\"pin_events\":"+pins+",\"scenario\":\""+kind+"\",\"foreign_calls\":\"UNATTEMPTED: JNI callback fixture does not cover foreign calls\"}\n");
    }
    public static void main(String[] args) throws Exception {
        Path out=Path.of(args[0]); Files.createDirectories(out);
        Files.writeString(out.resolve("java-properties.txt"),System.getProperties().toString()+"\n"+java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments());
        check(Runtime.version().feature()>=21,"runtime matrix requires JDK21+");
        if(args[1].equals("pin")) {pinning(args[2],args.length>3?args[3]:"monitor",out);return;}
        String mode=args[1],control=args[2];
        if(mode.equals("reactive")) reactive(control); else jdbc(mode,control);
        rows.sort(Comparator.comparingInt(s->Integer.parseInt(s.split(",")[0])));
        check(rows.size()==N,"request accounting mismatch "+rows.size());
        for(int id=0;id<N;id++) {
            String expected = !control.equals("pool-only") && id%WIDTH==K ? id+",REJECT," : id+",OK,"+(id*7+3);
            check(rows.get(id).equals(expected),"first mismatch id="+id+" expected="+expected+" actual="+rows.get(id));
        }
        check(active.get()==0 && peak.get()<=K && peak.get()>0,"pool accounting/peak mismatch");
        Files.write(out.resolve("outcomes.csv"),rows);
        Files.writeString(out.resolve("assertions.json"),"{\"status\":\"PASS\",\"requests\":12,\"pool_capacity\":2,\"observed_peak\":"+peak.get()+",\"active_at_end\":"+active.get()+"}\n");
        System.out.println("PASS correctness smoke "+mode+" "+control+"; no performance claim");
    }
}
