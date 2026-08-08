import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/command_center_data.dart';
import '../repositories/command_repository.dart';

class CommandActions extends ChangeNotifier {
  final CommandRepository _commandRepository;

  CommandCenterData? _data;
  bool _isLoading = false;
  bool _isSendingCommand = false;
  String? _error;
  Timer? _pollTimer;

  CommandActions(this._commandRepository);

  CommandCenterData? get data => _data;
  bool get isLoading => _isLoading;
  bool get isSendingCommand => _isSendingCommand;
  String? get error => _error;

  Future<void> loadCommandCenterData(String missionId, {bool silent = false}) async {
    if (!silent) _setLoading(true);
    try {
      _data = await _commandRepository.getCommandCenterData(missionId);
      _error = null;
    } catch (e) {
      if (!silent) _error = e.toString();
    } finally {
      if (!silent) _setLoading(false);
    }
  }

  Future<void> executeCommand(String missionId, String commandText) async {
    if (commandText.trim().isEmpty) return;
    
    _isSendingCommand = true;
    notifyListeners();
    
    try {
      await _commandRepository.sendCommand(missionId, commandText);
      // Reload data to reflect changes
      await loadCommandCenterData(missionId);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isSendingCommand = false;
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void startPolling(String missionId) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      loadCommandCenterData(missionId, silent: true);
    });
  }

  void stopPolling() {
    _pollTimer?.cancel();
    _pollTimer = null;
  }

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }
}
