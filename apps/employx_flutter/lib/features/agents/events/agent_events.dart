abstract class AgentEvent {
  final DateTime timestamp;
  AgentEvent() : timestamp = DateTime.now();
}

// Lifecycle Events
class AgentStarted extends AgentEvent {
  final String agentId;
  AgentStarted(this.agentId);
}

class AgentStopped extends AgentEvent {
  final String agentId;
  AgentStopped(this.agentId);
}

class AgentStatusChanged extends AgentEvent {
  final String agentId;
  final dynamic newStatus; // Using dynamic here temporarily to avoid import loops, but ideally type AgentStatus
  AgentStatusChanged(this.agentId, this.newStatus);
}

// Domain Events
class JobSearchRequested extends AgentEvent {
  final String query;
  JobSearchRequested(this.query);
}

class CVAdaptationRequested extends AgentEvent {
  final String targetJobId;
  CVAdaptationRequested(this.targetJobId);
}

class CVOptimized extends AgentEvent {
  final String cvId;
  CVOptimized(this.cvId);
}

class JobFound extends AgentEvent {
  final int count;
  JobFound(this.count);
}
