import java.nio.file.*;
import java.sql.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import io.r2dbc.pool.*;
import io.r2dbc.spi.*;
import reactor.core.Disposable;
import reactor.core.publisher.*;

/** Deterministic resource correctness only; no latency/throughput measurements. */
public class OfficialWorkload {
 static final Duration TIMEOUT=Duration.ofSeconds(20);
 static final String SQL="SELECT id, value FROM fixture WHERE id = ";
 static final AtomicInteger active=new AtomicInteger(),peak=new AtomicInteger(),borrow=new AtomicInteger(),release=new AtomicInteger();
 static final List<String> outcomes=Collections.synchronizedList(new ArrayList<>());
 static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
 static void acquired(){borrow.incrementAndGet();int n=active.incrementAndGet();peak.accumulateAndGet(n,Math::max);check(n<=2,"pool capacity");}
 static void released(){release.incrementAndGet();check(active.decrementAndGet()>=0,"duplicate release");}
 static void value(int id,int actual,int v){check(actual==id&&v==7*id+3,"row value");outcomes.add(id+",OK,"+v);}
 static void waitFor(CountDownLatch latch)throws Exception{check(latch.await(20,TimeUnit.SECONDS),"completion timeout");}
 static void terminal(OfficialAdmission.Lease lease,SignalType signal){if(signal==SignalType.ON_COMPLETE)lease.success();else if(signal==SignalType.CANCEL)lease.cancel();else lease.error();}
 static void jdbc(String mode)throws Exception {
  OfficialAdmission admission=new OfficialAdmission();ArrayBlockingQueue<java.sql.Connection> pool=new ArrayBlockingQueue<>(2);List<java.sql.Connection> all=new ArrayList<>();
  ExecutorService ex=mode.equals("virtual")?Executors.newVirtualThreadPerTaskExecutor():Executors.newFixedThreadPool(3);
  try{
   for(int i=0;i<2;i++){var c=DriverManager.getConnection("jdbc:postgresql://db:5432/smoke", "smoke","smoke");c.setAutoCommit(true);c.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);pool.add(c);all.add(c);}
   for(int base=0;base<12;base+=3){List<OfficialAdmission.Lease> leases=Arrays.asList(admission.acquire(),admission.acquire(),admission.acquire());List<Future<?>> fs=new ArrayList<>();
    for(int j=0;j<3;j++){int id=base+j;var lease=leases.get(j);if(lease==null){outcomes.add(id+",REJECT,");continue;}
     fs.add(ex.submit(()->{java.sql.Connection c=null;try{check(Thread.currentThread().isVirtual()==mode.equals("virtual"),"thread identity");c=pool.poll(20,TimeUnit.SECONDS);check(c!=null,"borrow timeout");acquired();try(var st=c.createStatement();var rs=st.executeQuery(SQL+id)){check(rs.next(),"missing row");value(id,rs.getInt(1),rs.getInt(2));check(!rs.next(),"duplicate row");}lease.success();}catch(Exception e){lease.error();throw new RuntimeException(e);}finally{if(c!=null){released();check(pool.offer(c),"double pool return");}lease.cancel();}}));
    }for(var f:fs)f.get(20,TimeUnit.SECONDS);check(pool.size()==2,"batch pool leak");admission.assertRestored();
   }
   // Real SQL error must return the connection and signal one drop.
   var fail=admission.acquire();var c=pool.take();acquired();int errors=admission.error.get();
   try(var st=c.createStatement()){st.executeQuery("SELECT 1/0");throw new AssertionError("expected SQL error");}catch(SQLException expected){fail.error();}finally{released();check(pool.offer(c),"error return");fail.cancel();}
   check(admission.error.get()==errors+1,"error accounting");
   // Cancellation after a real borrow, while work is paused before issuing SQL.
   var cancel=admission.acquire();CountDownLatch entered=new CountDownLatch(1),finished=new CountDownLatch(1);int cancels=admission.cancel.get();
   Future<?> future=ex.submit(()->{java.sql.Connection held=null;try{held=pool.take();acquired();entered.countDown();new CountDownLatch(1).await();}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{if(held!=null){released();check(pool.offer(held),"cancel return");}cancel.cancel();cancel.success();finished.countDown();}});
   waitFor(entered);check(future.cancel(true),"cancel accepted");waitFor(finished);check(admission.cancel.get()==cancels+1,"cancel accounting");
   // Cancellation while waiting for the pool: must not return a never-borrowed connection.
   var h1=pool.take();var h2=pool.take();var pending=admission.acquire();CountDownLatch waiting=new CountDownLatch(1),done=new CountDownLatch(1);int before=borrow.get();
   Future<?> f=ex.submit(()->{try{waiting.countDown();pool.take();throw new AssertionError("unexpected borrow");}catch(InterruptedException expected){Thread.currentThread().interrupt();}finally{pending.cancel();done.countDown();}});
   waitFor(waiting);check(f.cancel(true),"pending cancel");waitFor(done);check(borrow.get()==before,"pending borrow");pool.add(h1);pool.add(h2);
   admission.assertRestored();check(pool.size()==2,"final pool leak");
  }finally{ex.shutdownNow();check(ex.awaitTermination(20,TimeUnit.SECONDS),"executor shutdown");for(var c:all)c.close();}
 }
 static Mono<Void> operation(ConnectionPool pool,OfficialAdmission.Lease lease,int id,boolean fail,CountDownLatch entered,CountDownLatch ended){
  return Mono.usingWhen(pool.create(),c->{acquired();if(entered!=null){entered.countDown();return Mono.<Void>never();}
   return Mono.from(c.setAutoCommit(true)).then(Mono.from(c.setTransactionIsolationLevel(IsolationLevel.READ_COMMITTED)))
    .thenMany(Flux.from(c.createStatement(fail?"SELECT 1/0":SQL+id).execute()))
    .concatMap(r->r.map((row,meta)->new int[]{row.get("id",Integer.class),row.get("value",Integer.class)})).single().doOnNext(v->value(id,v[0],v[1])).then();
  },c->Mono.from(c.close()).doOnSuccess(v->released()),(c,e)->Mono.from(c.close()).doOnSuccess(v->released()),c->Mono.from(c.close()).doOnSuccess(v->released()))
   .doFinally(signal->{terminal(lease,signal);if(ended!=null)ended.countDown();});
 }
 static void reactive()throws Exception {
  var factory=ConnectionFactories.get("r2dbc:postgresql://smoke:smoke@db:5432/smoke");var pool=new ConnectionPool(ConnectionPoolConfiguration.builder(factory).initialSize(2).maxSize(2).maxAcquireTime(TIMEOUT).build());var admission=new OfficialAdmission();
  try{pool.warmup().block(TIMEOUT);
   for(int base=0;base<12;base+=3){var leases=Arrays.asList(admission.acquire(),admission.acquire(),admission.acquire());var work=new ArrayList<Mono<Void>>();var done=new CountDownLatch(2);
    for(int j=0;j<3;j++){int id=base+j;var lease=leases.get(j);if(lease==null)outcomes.add(id+",REJECT,");else work.add(operation(pool,lease,id,false,null,done));}
    Flux.merge(work).then().block(TIMEOUT);waitFor(done);admission.assertRestored();
   }
   int errors=admission.error.get();var failed=new CountDownLatch(1);
   try{operation(pool,admission.acquire(),0,true,null,failed).block(TIMEOUT);throw new AssertionError("expected reactive SQL error");}catch(RuntimeException expected){}
   waitFor(failed);check(admission.error.get()==errors+1,"reactive error accounting");
   var entered=new CountDownLatch(1);var done=new CountDownLatch(1);int cancels=admission.cancel.get();
   Disposable d=operation(pool,admission.acquire(),0,false,entered,done).subscribe();waitFor(entered);d.dispose();waitFor(done);
   check(admission.cancel.get()==cancels+1,"reactive cancel accounting");
   // Hold both real resources; cancellation must release admission without a borrowed connection.
   var a=pool.create().block(TIMEOUT);var b=pool.create().block(TIMEOUT);var pendingDone=new CountDownLatch(1);int before=borrow.get();
   Disposable p=operation(pool,admission.acquire(),0,false,null,pendingDone).subscribe();p.dispose();waitFor(pendingDone);check(borrow.get()==before,"pending reactive borrow");
   Mono.from(a.close()).block(TIMEOUT);Mono.from(b.close()).block(TIMEOUT);
   // Pool cancellation cleanup can finish asynchronously after doFinally.
   long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(20);
   while((active.get()!=0||pool.getMetrics().orElseThrow().acquiredSize()!=0)&&System.nanoTime()<deadline)Thread.sleep(5);
   check(pool.getMetrics().orElseThrow().acquiredSize()==0,"reactive pool leak");admission.assertRestored();
  }finally{pool.disposeLater().block(TIMEOUT);}
 }
 public static void main(String[] args)throws Exception{
  String mode=args[0];if(mode.equals("reactive"))reactive();else jdbc(mode);
  Collections.sort(outcomes,Comparator.comparingInt(s->Integer.parseInt(s.split(",")[0])));
  check(outcomes.size()==12,"outcome count");for(int id=0;id<12;id++)check(outcomes.get(id).equals(id%3==2?id+",REJECT,":id+",OK,"+(7*id+3)),"outcome oracle");
  check(active.get()==0&&borrow.get()==release.get(),"resource balance");
  Path out=Path.of(args[1]);Files.createDirectories(out);Files.writeString(out.resolve("outcomes.csv"),String.join("\n",outcomes)+"\n");
  Files.writeString(out.resolve("assertions.json"),"{\"status\":\"PASS\",\"mode\":\""+mode+"\",\"requests\":12,\"peak\":"+peak.get()+",\"borrows\":"+borrow.get()+",\"releases\":"+release.get()+",\"active_at_end\":0,\"sql_error\":\"PASS\",\"cancel_after_borrow\":\"PASS\",\"cancel_waiting_for_pool\":\"PASS\"}\n");
  System.out.println("PASS "+mode+" matched requests, SQL error, cancellation before/after borrow, exactly-once admission and pool release");
 }
}
