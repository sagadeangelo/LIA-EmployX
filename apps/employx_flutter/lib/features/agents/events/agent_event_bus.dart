import 'dart:async';
import 'agent_events.dart';

class AgentEventBus {
  static final AgentEventBus _instance = AgentEventBus._internal();
  
  factory AgentEventBus() {
    return _instance;
  }
  
  AgentEventBus._internal();

  final StreamController<AgentEvent> _controller = StreamController<AgentEvent>.broadcast();

  Stream<AgentEvent> get stream => _controller.stream;

  void fire(AgentEvent event) {
    _controller.add(event);
  }

  Stream<T> on<T extends AgentEvent>() {
    return _controller.stream.where((event) => event is T).cast<T>();
  }

  void dispose() {
    _controller.close();
  }
}
