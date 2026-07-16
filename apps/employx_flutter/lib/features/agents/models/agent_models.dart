import 'package:flutter/material.dart';

enum AgentType {
  career, cv, hunter, email, whatsapp, linkedin, interview, recruiter, custom,
}

enum AgentStatus {
  idle, active, thinking, planning, coordinating, executing, waiting, success, warning, error, disabled,
}

class AgentCapabilities {
  final List<String> skills;
  final List<String> integrations;
  
  AgentCapabilities({this.skills = const [], this.integrations = const []});
}

class AgentMetrics {
  int tasksCompleted;
  Duration timeSaved;
  double cpuUsage;
  double productivity;
  
  AgentMetrics({
    this.tasksCompleted = 0,
    this.timeSaved = Duration.zero,
    this.cpuUsage = 0.0,
    this.productivity = 0.0,
  });
}

class AgentConfiguration {
  bool autoStart;
  bool notificationsEnabled;
  Map<String, dynamic> customSettings;
  
  AgentConfiguration({
    this.autoStart = true,
    this.notificationsEnabled = true,
    this.customSettings = const {},
  });
}

class AgentPermissions {
  bool canReadFiles;
  bool canWriteFiles;
  bool canSendEmails;
  bool canAccessInternet;
  
  AgentPermissions({
    this.canReadFiles = false,
    this.canWriteFiles = false,
    this.canSendEmails = false,
    this.canAccessInternet = true,
  });
}

class AgentExecution {
  String currentActionText;
  double currentProgress; // 0.0 to 1.0
  String lastActionText;
  String nextActionText;
  
  AgentExecution({
    this.currentActionText = '',
    this.currentProgress = 0.0,
    this.lastActionText = '',
    this.nextActionText = '',
  });
}

class AgentModel {
  final String id;
  final String name;
  final String subtitle;
  final String description;
  final IconData icon;
  final Color color;
  final Color accentColor;
  final AgentType type;
  
  AgentStatus status;
  bool installed;
  bool enabled;
  final bool isCore;
  final bool isPremium;
  final String version;
  final String author;
  final String category;
  
  // Topology for Mission Center
  final String? connectedTo;

  AgentCapabilities capabilities;
  AgentMetrics metrics;
  AgentConfiguration configuration;
  AgentPermissions permissions;
  AgentExecution execution;

  AgentModel({
    required this.id,
    required this.name,
    required this.subtitle,
    required this.description,
    required this.icon,
    required this.color,
    required this.accentColor,
    required this.type,
    this.status = AgentStatus.idle,
    this.installed = true,
    this.enabled = true,
    this.isCore = false,
    this.isPremium = false,
    this.version = '1.0.0',
    this.author = 'LIA Core',
    this.category = 'General',
    this.connectedTo,
    AgentCapabilities? capabilities,
    AgentMetrics? metrics,
    AgentConfiguration? configuration,
    AgentPermissions? permissions,
    AgentExecution? execution,
  }) : 
    this.capabilities = capabilities ?? AgentCapabilities(),
    this.metrics = metrics ?? AgentMetrics(),
    this.configuration = configuration ?? AgentConfiguration(),
    this.permissions = permissions ?? AgentPermissions(),
    this.execution = execution ?? AgentExecution();
}
