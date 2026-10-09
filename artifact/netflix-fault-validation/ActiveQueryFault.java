import java.sql.*;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import io.r2dbc.spi.ConnectionFactories;
import io.r2dbc.spi.R2dbcException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

/** Preparation: server-side interruption, not client subscription-cancel certification. */
public final class ActiveQueryFault {
    static final Duration WAIT = Duration.ofSeconds(30);
    static final AtomicInteger sequence = new AtomicInteger();
    static final OfficialAdmission admission = new OfficialAdmission();
    static final String JDBC = "jdbc:postgresql://db:5432/smoke";
    static final String R2DBC = "r2dbc:postgresql://smoke:smoke@db:5432/smoke";
    static synchronized void event(String kind, String request, String connection, int pid, String value) {
        System.out.println(sequence.incrementAndGet()+"\t"+kind+"\t"+request+"\t"+connection+"\t"+pid+"\t"+value.replace('\t',' ').replace('\n',' '));
        System.out.flush();
    }
    static void require(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
    static String state(Throwable error) {
        for (Throwable e=error;e!=null;e=e.getCause()) {
            if(e instanceof SQLException s) return s.getSQLState();
            if(e instanceof R2dbcException r) return r.getSqlState();
        }
        return error==null?"OK":"UNKNOWN";
    }
    static int scalar(java.sql.Connection c, String sql) throws Exception {
        try(var s=c.createStatement();var r=s.executeQuery(sql)){require(r.next(),"missing scalar");return r.getInt(1);}
    }
    static int scalar(io.r2dbc.spi.Connection c, String sql) {
        Integer v=Flux.from(c.createStatement(sql).execute()).concatMap(r->r.map((row,meta)->row.get(0,Integer.class))).single().block(WAIT);
        require(v!=null,"missing scalar");return v;
    }
    static boolean isActive(java.sql.Connection control, int pid, String marker) throws Exception {
        try(var s=control.prepareStatement("SELECT state='active' AND query LIKE ? FROM pg_stat_activity WHERE pid=?")) {
            s.setString(1,"%"+marker+"%");s.setInt(2,pid);
            try(var r=s.executeQuery()){return r.next()&&r.getBoolean(1);}
        }
    }
    static void awaitActive(java.sql.Connection control,int pid,String marker,CompletableFuture<Throwable> done) throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);
        while(System.nanoTime()<deadline){
            if(isActive(control,pid,marker)) return;
            require(!done.isDone(),"query terminated before active observation");Thread.sleep(10);
        }
        throw new AssertionError("active-query confirmation deadline");
    }
    static void restored(String request) {
        require(admission.limiter.getInflight()==0,"inflight leak");
        admission.assertRestored();event("capacity-restored",request,"none",0,"2");
    }
    static void runCase(String mode,String scenario,boolean followup,String parent) throws Exception {
        String request=UUID.randomUUID().toString(), connection=UUID.randomUUID().toString();
        String marker="fault_"+request.replace("-","");
        event("request",request,connection,0,followup?"followup:"+parent:scenario);
        OfficialAdmission.Lease lease=admission.acquire();require(lease!=null,"lease rejected");
        event("lease-acquired",request,connection,0,"1");
        int beforeSuccess=admission.success.get(),beforeError=admission.error.get(),beforeCancel=admission.cancel.get();
        java.sql.Connection jdbc=null;io.r2dbc.spi.Connection reactive=null;
        ExecutorService executor=null;int pid=0;boolean closed=false,terminal=false;
        CompletableFuture<Throwable> done=new CompletableFuture<>();
        try(var control=DriverManager.getConnection(JDBC,"smoke","smoke")) {
            if(mode.equals("reactive")) {
                reactive=Mono.from(ConnectionFactories.get(R2DBC).create()).block(WAIT);require(reactive!=null,"connect returned null");
                pid=scalar(reactive,"SELECT pg_backend_pid()");
                // Setup is synchronous orchestration; actual pg_sleep is a subscribed R2DBC publisher.
                Flux.from(reactive.createStatement("SET statement_timeout = '"+(scenario.equals("server-timeout")?"5s":"0")+"'").execute()).concatMap(r->r.getRowsUpdated()).then().block(WAIT);
            } else {
                jdbc=DriverManager.getConnection(JDBC,"smoke","smoke");pid=scalar(jdbc,"SELECT pg_backend_pid()");
                try(var s=jdbc.createStatement()){s.execute("SET statement_timeout = '"+(scenario.equals("server-timeout")?"5s":"0")+"'");}
            }
            event("connection-acquired",request,connection,pid,"1");
            final int backend=pid;
            if(!followup&&scenario.equals("before-query")) {
                require(!isActive(control,pid,marker),"unexpected active marker");
                event("before-query-cancel",request,connection,pid,"no-sleep-issued");
                event("outcome",request,connection,pid,"NONE");
            } else {
                String sql=followup?"SELECT 1":"SELECT 1 FROM pg_sleep(20) /* "+marker+" */";
                event("query-issued",request,connection,pid,followup?"SELECT1":marker);
                if(mode.equals("reactive")) {
                    Flux.from(reactive.createStatement(sql).execute()).concatMap(r->r.map((row,meta)->row.get(0,Integer.class)))
                        .single().subscribe(value->{
                            if(value==null||value!=1)done.complete(new AssertionError("wrong scalar"));else done.complete(null);
                        },done::complete);
                } else {
                    executor=mode.equals("virtual")?Executors.newVirtualThreadPerTaskExecutor():Executors.newSingleThreadExecutor();
                    final java.sql.Connection target=jdbc;
                    executor.submit(()->{try{
                        require(Thread.currentThread().isVirtual()==mode.equals("virtual"),"thread identity");
                        event("thread-identity",request,connection,backend,Boolean.toString(Thread.currentThread().isVirtual()));
                        require(scalar(target,sql)==1,"wrong scalar");done.complete(null);
                    }catch(Throwable error){done.complete(error);}});
                }
                if(!followup){
                    awaitActive(control,pid,marker,done);event("server-active",request,connection,pid,marker);
                    if(scenario.equals("server-cancel")){
                        try(var s=control.prepareStatement("SELECT pg_cancel_backend(?)")){
                            s.setInt(1,pid);try(var r=s.executeQuery()){
                                require(r.next()&&r.getBoolean(1),"pg_cancel_backend false");
                                event("cancel-requested",request,connection,pid,"true");
                            }
                        }
                    }else event("timeout-armed",request,connection,pid,"PostgreSQL statement_timeout=5s");
                }
                Throwable error=done.get(30,TimeUnit.SECONDS);String sqlstate=state(error);
                event("outcome",request,connection,pid,sqlstate);
                require(sqlstate.equals(followup?"OK":"57014"),"unexpected outcome "+sqlstate);
            }
            if(reactive!=null)Mono.from(reactive.close()).block(WAIT);else jdbc.close();
            closed=true;event("connection-closed",request,connection,pid,"1");
            require(!isActive(control,pid,marker),"query remains active after close");
            event("server-inactive",request,connection,pid,"confirmed");
            String outcome=followup?"success":scenario.equals("server-timeout")?"error":"cancel";
            if(outcome.equals("success"))lease.success();else if(outcome.equals("error"))lease.error();else lease.cancel();
            terminal=true;event("lease-terminal",request,connection,pid,outcome);
            // Sequential duplicate attempts exercise the preserved CAS guard, not upstream idempotence.
            lease.success();lease.error();lease.cancel();
            int ds=admission.success.get()-beforeSuccess,de=admission.error.get()-beforeError,dc=admission.cancel.get()-beforeCancel;
            require(ds==(outcome.equals("success")?1:0)&&de==(outcome.equals("error")?1:0)&&dc==(outcome.equals("cancel")?1:0),"duplicate upstream callback");
            event("callback-counts",request,connection,pid,ds+","+de+","+dc);
            restored(request);
        } catch(Throwable failure) {
            event("unresolved",request,connection,pid,"closed="+closed+",terminal="+terminal+",done="+done.isDone()+",failure="+failure);
            // Retain late cleanup separately; this never converts the failed case to PASS.
            if(!closed){try{
                if(reactive!=null)Mono.from(reactive.close()).block(WAIT);else if(jdbc!=null)jdbc.close();
                event("late-cleanup",request,connection,pid,"attempt-completed");
            }catch(Throwable cleanup){event("late-cleanup-error",request,connection,pid,cleanup.toString());}}
            throw failure;
        } finally {
            if(executor!=null){executor.shutdownNow();if(!executor.awaitTermination(5,TimeUnit.SECONDS))event("unresolved",request,connection,pid,"executor-not-terminated");}
        }
        if(!followup)runCase(mode,scenario,true,request);
    }
    public static void main(String[] args) throws Exception {
        require(args.length==2,"mode scenario required");String mode=args[0],scenario=args[1];
        require(java.util.Set.of("platform","virtual","reactive").contains(mode),"unknown mode");
        require(java.util.Set.of("before-query","server-cancel","server-timeout").contains(scenario),"unknown scenario");
        event("runtime","none","none",0,System.getProperty("java.version")+","+System.getProperty("os.arch")+","+mode);
        runCase(mode,scenario,false,"");
        event("case-finished","none","none",0,"inspect-events-before-PASS");
    }
}
