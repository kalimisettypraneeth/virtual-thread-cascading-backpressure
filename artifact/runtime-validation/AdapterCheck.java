/** Java17-only preparation check; does not execute VT, database or JFR fixtures. */
public class AdapterCheck {
    public static void main(String[] args) throws Exception {
        for (String control : new String[]{"fixed", "pool-only", "breakwater-inspired", "gradient2-reduced", "envoy-reduced"}) {
            int actual = RuntimeSmoke.capacity(control);
            if (actual != 2) throw new AssertionError(control + " expected=2 actual=" + actual);
            System.out.println("PASS scripted adapter " + control + " capacity=2");
        }
    }
}
