import java.net.URI;
import java.net.http.*;
import java.time.Duration;

public class Egress {
  public static void main(String[] args) {
    try {
      HttpClient c = HttpClient.newBuilder()
          .connectTimeout(Duration.ofSeconds(5))
          .followRedirects(HttpClient.Redirect.NORMAL)
          .build();

      HttpRequest r = HttpRequest.newBuilder()
          .uri(URI.create(args.length > 0 ? args[0] : "https://example.com"))
          .timeout(Duration.ofSeconds(8))
          .GET()
          .build();

      c.send(r, HttpResponse.BodyHandlers.discarding());
      System.exit(0);
    } catch (Throwable t) {
      System.exit(1);
    }
  }
}
