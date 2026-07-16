abstract class Agent {
  Future<void> initialize();
  Future<void> execute();
  Future<void> pause();
  Future<void> stop();
  Future<void> dispose();
}
