import '../models/agent_models.dart';

class AgentRegistry {
  static final AgentRegistry _instance = AgentRegistry._internal();
  
  factory AgentRegistry() {
    return _instance;
  }
  
  AgentRegistry._internal();

  final Map<String, AgentModel> _registry = {};

  void registerAgent(AgentModel agent) {
    _registry[agent.id] = agent;
  }

  void unregisterAgent(String id) {
    _registry.remove(id);
  }

  AgentModel? getAgent(String id) {
    return _registry[id];
  }

  List<AgentModel> getAllAgents() {
    return _registry.values.toList();
  }

  List<AgentModel> getInstalledAgents() {
    return _registry.values.where((agent) => agent.installed).toList();
  }
}
