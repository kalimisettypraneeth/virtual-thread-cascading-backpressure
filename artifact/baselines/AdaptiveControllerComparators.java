import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Locale;

/**
 * Dependency-free equation comparators derived from pinned, licensed controller sources.
 *
 * <p>This is not vendored Netflix or Envoy code and is not an official artifact build. It keeps
 * only the arithmetic/state needed for deterministic trace validation. See README.md for the
 * exact upstream revisions, source blobs, omissions, and evidence boundary.</p>
 */
public final class AdaptiveControllerComparators {
    private AdaptiveControllerComparators() {}

    private static final class NetflixGradient2Step {
        private double estimatedLimit;
        private final int minLimit;
        private final int maxLimit;
        private final double smoothing;
        private final int queueSize;
        private final double tolerance;
        private final int longWindow;
        private final int warmupWindow;
        private double longRtt;
        private double sum;
        private int count;

        NetflixGradient2Step(int initialLimit, int minLimit, int maxLimit, double smoothing,
                             int queueSize, double tolerance, int longWindow, int warmupWindow) {
            this.estimatedLimit = initialLimit;
            this.minLimit = minLimit;
            this.maxLimit = maxLimit;
            this.smoothing = smoothing;
            this.queueSize = queueSize;
            this.tolerance = tolerance;
            this.longWindow = longWindow;
            this.warmupWindow = warmupWindow;
        }

        int sample(double rtt, int inflight) {
            if (count < warmupWindow) {
                count++;
                sum += rtt;
                longRtt = sum / count;
            } else {
                double factor = 2.0 / (longWindow + 1.0);
                longRtt = longRtt * (1.0 - factor) + rtt * factor;
            }

            if (longRtt / rtt > 2.0) {
                longRtt *= 0.95;
            }

            if (inflight < estimatedLimit / 2.0) {
                return (int) estimatedLimit;
            }

            double gradient = Math.max(0.5, Math.min(1.0, tolerance * longRtt / rtt));
            double proposed = estimatedLimit * gradient + queueSize;
            proposed = estimatedLimit * (1.0 - smoothing) + proposed * smoothing;
            estimatedLimit = Math.max(minLimit, Math.min(maxLimit, proposed));
            return (int) estimatedLimit;
        }

        double estimatedLimit() {
            return estimatedLimit;
        }

        double longRtt() {
            return longRtt;
        }
    }

    private static int envoyStep(int oldLimit, int minLimit, int maxLimit, double minRtt,
                                 double bufferFraction, double sampleRtt) {
        double bufferedMinRtt = minRtt + minRtt * bufferFraction;
        double gradient = Math.max(0.5, Math.min(2.0, bufferedMinRtt / sampleRtt));
        double scaled = oldLimit * gradient;
        long truncated = (long) (scaled + Math.sqrt(scaled));
        return (int) Math.max(minLimit, Math.min(maxLimit, truncated));
    }

    public static void main(String[] args) throws Exception {
        Locale.setDefault(Locale.ROOT);
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        NetflixGradient2Step netflix = null;
        String line;
        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] p = line.split(",");
            switch (p[0]) {
                case "NC" -> {
                    netflix = new NetflixGradient2Step(
                            Integer.parseInt(p[1]), Integer.parseInt(p[2]), Integer.parseInt(p[3]),
                            Double.parseDouble(p[4]), Integer.parseInt(p[5]),
                            Double.parseDouble(p[6]), Integer.parseInt(p[7]), Integer.parseInt(p[8]));
                    System.out.println("NC,OK");
                }
                case "NS" -> {
                    if (netflix == null) throw new IllegalStateException("NC must precede NS");
                    int limit = netflix.sample(Double.parseDouble(p[1]), Integer.parseInt(p[2]));
                    System.out.printf(Locale.ROOT, "NS,%d,%.12f,%.12f%n", limit,
                            netflix.estimatedLimit(), netflix.longRtt());
                }
                case "E" -> {
                    int limit = envoyStep(Integer.parseInt(p[1]), Integer.parseInt(p[2]),
                            Integer.parseInt(p[3]), Double.parseDouble(p[4]),
                            Double.parseDouble(p[5]), Double.parseDouble(p[6]));
                    System.out.printf(Locale.ROOT, "E,%d%n", limit);
                }
                default -> throw new IllegalArgumentException("Unknown record: " + p[0]);
            }
        }
    }
}
