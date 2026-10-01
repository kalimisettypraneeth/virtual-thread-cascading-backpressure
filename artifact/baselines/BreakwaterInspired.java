import java.util.Locale;

/**
 * Reduced, paper-derived comparator for the Breakwater credit equations.
 *
 * This is an original implementation from Cho et al., OSDI 2020, Section 3.2,
 * Equations (1)--(6). It is not the authors' artifact or an exact reproduction.
 */
public final class BreakwaterInspired {
    private BreakwaterInspired() {}

    record PoolUpdate(double additiveStep, double decreaseFactor, double nextTotal) {}
    record ClientUpdate(long overcommit, long available, long nextUnused, long delta) {}

    static PoolUpdate updatePool(
            double currentTotal,
            double measuredDelay,
            double targetDelay,
            double alpha,
            long clients,
            double beta) {
        requireFinitePositive("currentTotal", currentTotal);
        requireFiniteNonNegative("measuredDelay", measuredDelay);
        requireFinitePositive("targetDelay", targetDelay);
        requireFiniteNonNegative("alpha", alpha);
        requireFiniteNonNegative("beta", beta);
        if (clients < 1) throw new IllegalArgumentException("clients must be >= 1");

        double additive = Math.max(alpha * clients, 1.0); // Eq. (3)
        if (measuredDelay < targetDelay) {
            return new PoolUpdate(additive, 1.0, currentTotal + additive); // Eq. (1)
        }
        double factor = Math.max(
                1.0 - beta * ((measuredDelay - targetDelay) / targetDelay),
                0.5); // Eq. (2)
        return new PoolUpdate(additive, factor, currentTotal * factor);
    }

    static ClientUpdate updateClient(
            long total,
            long issued,
            long clients,
            long demand,
            long unused) {
        if (total < 0 || issued < 0 || demand < 0 || unused < 0) {
            throw new IllegalArgumentException("credit and demand values must be >= 0");
        }
        if (clients < 1) throw new IllegalArgumentException("clients must be >= 1");

        long available = Math.max(total - issued, 0);
        long overcommit = Math.max((total - issued) / clients, 1); // Eq. (4), integer credits
        long next;
        if (issued < total) {
            next = Math.min(Math.addExact(demand, overcommit), Math.addExact(unused, available)); // Eq. (5)
        } else {
            long paperValue = Math.min(Math.addExact(demand, overcommit), unused - 1); // Eq. (6)
            next = Math.max(paperValue, 0); // explicit non-negative safety deviation
        }
        return new ClientUpdate(overcommit, available, next, next - unused);
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.ROOT);
        try {
            if (args.length == 7 && args[0].equals("pool")) {
                PoolUpdate r = updatePool(
                        Double.parseDouble(args[1]), Double.parseDouble(args[2]),
                        Double.parseDouble(args[3]), Double.parseDouble(args[4]),
                        Long.parseLong(args[5]), Double.parseDouble(args[6]));
                System.out.printf("POOL,%.6f,%.6f,%.6f%n", r.additiveStep(), r.decreaseFactor(), r.nextTotal());
                return;
            }
            if (args.length == 6 && args[0].equals("client")) {
                ClientUpdate r = updateClient(
                        Long.parseLong(args[1]), Long.parseLong(args[2]),
                        Long.parseLong(args[3]), Long.parseLong(args[4]),
                        Long.parseLong(args[5]));
                System.out.printf("CLIENT,%d,%d,%d,%d%n", r.overcommit(), r.available(), r.nextUnused(), r.delta());
                return;
            }
            throw new IllegalArgumentException(
                    "usage: pool current measured target alpha clients beta | client total issued clients demand unused");
        } catch (RuntimeException e) {
            System.err.println("ERROR," + e.getClass().getSimpleName() + "," + e.getMessage());
            System.exit(2);
        }
    }

    private static void requireFinitePositive(String name, double value) {
        if (!Double.isFinite(value) || value <= 0) {
            throw new IllegalArgumentException(name + " must be finite and > 0");
        }
    }

    private static void requireFiniteNonNegative(String name, double value) {
        if (!Double.isFinite(value) || value < 0) {
            throw new IllegalArgumentException(name + " must be finite and >= 0");
        }
    }
}
