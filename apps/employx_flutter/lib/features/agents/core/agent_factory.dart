import '../models/agent_base.dart';
import '../models/agent_models.dart';
import 'career_agent.dart';
import 'cv_expert_agent.dart';
import 'job_hunter_agent.dart';

class AgentFactory {
  static Agent createAgent(AgentType type) {
    switch (type) {
      case AgentType.career:
        return CareerAgent();
      case AgentType.cv:
        return CVExpertAgent();
      case AgentType.hunter:
        return JobHunterAgent();
      default:
        throw Exception('AgentType $type is not currently supported by factory.');
    }
  }
}
