import 'dart:developer' as developer;

class AppLogger {
  static void info(String component, String message, {String? missionId, int? durationMs}) {
    _log('INFO', component, message, missionId, durationMs);
  }

  static void debug(String component, String message, {String? missionId, int? durationMs}) {
    _log('DEBUG', component, message, missionId, durationMs);
  }

  static void warning(String component, String message, {String? missionId, int? durationMs}) {
    _log('WARN', component, message, missionId, durationMs);
  }

  static void error(String component, String message, {String? missionId, int? durationMs, dynamic error}) {
    _log('ERROR', component, '$message${error != null ? ' - $error' : ''}', missionId, durationMs);
  }

  static void _log(String level, String component, String message, String? missionId, int? durationMs) {
    final missionPrefix = missionId != null ? '[Mission: $missionId] ' : '';
    final durationSuffix = durationMs != null ? ' - ${durationMs}ms' : '';
    final formattedMessage = '$missionPrefix[$component] $message$durationSuffix';
    
    print('[$level] $formattedMessage');
    
    developer.log(
      formattedMessage,
      name: component,
      level: level == 'ERROR' ? 1000 : (level == 'WARN' ? 900 : 800),
    );
  }
}
