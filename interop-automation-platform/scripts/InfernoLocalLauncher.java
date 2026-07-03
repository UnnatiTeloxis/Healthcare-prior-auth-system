package inferno.local;

import spark.Spark;

/**
 * Starts Inferno on 127.0.0.1 only so Render routes public traffic to FastAPI (PORT),
 * not to the validator wrapper on 4567.
 */
public final class InfernoLocalLauncher {
    private InfernoLocalLauncher() {}

    public static void main(String[] args) throws Exception {
        Spark.ipAddress("127.0.0.1");
        org.mitre.inferno.App.main(args);
    }
}
