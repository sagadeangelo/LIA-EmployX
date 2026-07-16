import 'package:flutter/foundation.dart';
import '../models/agent_models.dart';
import '../models/agent_activity.dart';
import 'career_agent.dart';
import 'cv_expert_agent.dart';
import 'job_hunter_agent.dart';

class AgentCoordinator extends ChangeNotifier {
  final CareerAgent _careerAgent = CareerAgent();
  final CVExpertAgent _cvExpertAgent = CVExpertAgent();
  final JobHunterAgent _jobHunterAgent = JobHunterAgent();

  List<AgentModel> _agents = [];
  List<AgentActivity> _activities = [];

  List<AgentModel> get agents => _agents;
  List<AgentActivity> get activities => _activities;

  int get workingAgentsCount => _agents.where((a) => a.status == AgentStatus.executing || a.status == AgentStatus.coordinating).length;
  int get tasksCompletedToday => _agents.fold(0, (sum, a) => sum + a.tasksToday);
  Duration get timeSaved => _agents.fold(Duration.zero, (sum, a) => sum + a.workTimeToday);

  AgentCoordinator() {
    _initializeAgents();
  }

  void _initializeAgents() {
    // We will populate this later
  }

  // Simulated logic to be expanded later
  void simulateActivity() {
    // ...
  }
}
