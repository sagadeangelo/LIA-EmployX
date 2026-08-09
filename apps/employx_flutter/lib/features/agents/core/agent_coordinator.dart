import 'package:flutter/foundation.dart';

import '../models/agent_models.dart';
import '../models/agent_activity.dart';

class AgentCoordinator extends ChangeNotifier {
  List<AgentModel> _agents = [];
  List<AgentActivity> _activities = [];

  List<AgentModel> get agents =>
      List.unmodifiable(_agents);

  List<AgentActivity> get activities =>
      List.unmodifiable(_activities);

  int get workingAgentsCount {
    return _agents
        .where(
          (agent) =>
              agent.status ==
                  AgentStatus.executing ||
              agent.status ==
                  AgentStatus.coordinating,
        )
        .length;
  }

  /// Todavía no existe un contador persistente
  /// de tareas dentro de AgentModel.
  ///
  /// No fabricamos datos.
  int get tasksCompletedToday => 0;

  /// Todavía no existe tracking de tiempo
  /// dentro de AgentModel.
  ///
  /// No fabricamos datos.
  Duration get timeSaved =>
      Duration.zero;

  AgentCoordinator() {
    _initializeAgents();
  }

  void _initializeAgents() {
    _agents = [];
    _activities = [];
  }

  void addActivity(
    AgentActivity activity,
  ) {
    _activities = [
      ..._activities,
      activity,
    ];

    notifyListeners();
  }

  void clearActivities() {
    if (_activities.isEmpty) {
      return;
    }

    _activities = [];

    notifyListeners();
  }

  void simulateActivity() {
    // Pendiente de conectar con el runtime real.
    //
    // No generamos actividades falsas.
  }
}