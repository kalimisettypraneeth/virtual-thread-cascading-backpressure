import com.netflix.concurrency.limits.limit.Gradient2Limit;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
public final class OfficialProbe {
 public static void main(String[] args)throws Exception {
  Gradient2Limit limit=null;String name="";int index=0;AtomicInteger notifications=new AtomicInteger();
  for(String line:Files.readAllLines(Path.of(args[0]))){String[] p=line.split(",");
   if(p[0].equals("C")){name=p[1];index=0;notifications.set(0);limit=Gradient2Limit.newBuilder().initialLimit(Integer.parseInt(p[2])).minLimit(Integer.parseInt(p[3])).maxConcurrency(Integer.parseInt(p[4])).smoothing(Double.parseDouble(p[5])).queueSize(Integer.parseInt(p[6])).rttTolerance(Double.parseDouble(p[7])).longWindow(Integer.parseInt(p[8])).build();limit.notifyOnChange(v->notifications.incrementAndGet());}
   else{limit.onSample(0,Long.parseLong(p[1]),Integer.parseInt(p[2]),Boolean.parseBoolean(p[3]));System.out.println(name+","+(index++)+","+limit.getLimit()+","+limit.getRttNoLoad(TimeUnit.NANOSECONDS)+","+notifications.get());}
  }
  OfficialAdmission admission=new OfficialAdmission();
  var a=admission.acquire();var b=admission.acquire();
  if(a==null||b==null||admission.acquire()!=null)throw new AssertionError("API admission");
  a.success();a.error();a.cancel();b.error();b.success();
  if(admission.success.get()!=1||admission.error.get()!=1||admission.cancel.get()!=0)throw new AssertionError("terminal accounting");
  admission.assertRestored();
  var c=admission.acquire();int before=admission.success.get()+admission.error.get()+admission.cancel.get();
  var barrier=new CountDownLatch(1);Thread[] t={new Thread(()->{await(barrier);c.success();}),new Thread(()->{await(barrier);c.error();}),new Thread(()->{await(barrier);c.cancel();})};
  for(var x:t)x.start();barrier.countDown();for(var x:t)x.join();
  if(admission.success.get()+admission.error.get()+admission.cancel.get()!=before+1)throw new AssertionError("race accounting");
  admission.assertRestored();System.err.println("API/listener smoke PASS: success, drop, ignore, duplicate terminal calls, racing terminals, restored capacity");
 }
 static void await(CountDownLatch l){try{l.await();}catch(Exception e){throw new RuntimeException(e);}}
}
