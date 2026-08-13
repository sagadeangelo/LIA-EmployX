import 'package:flutter/foundation.dart';

enum UploadPhase { transfer, analysis }
enum TransferStep { preparing, uploading, verifying, completed }
enum MissionStage {
  receiveFile,
  storeFile,
  detectFormat,
  readDocument,
  extractText,
  normalizeText,
  buildProfile,
  saveProfile,
  updateRuntime,
  complete,
}

class UploadProvider extends ChangeNotifier {
  UploadPhase _currentPhase = UploadPhase.transfer;
  TransferStep _transferStep = TransferStep.preparing;
  double _transferProgress = 0.0;
  String _fileName = '';
  int _fileSize = 0;
  double _speedMBps = 0.0;
  Duration _eta = Duration.zero;
  MissionStage _missionStage = MissionStage.receiveFile;
  String _errorMessage = '';
  bool _hasError = false;
  bool _isUploading = false;
  bool _isCompleted = false;
  DateTime? _startTime;
  DateTime? _lastUploadTime;
  int _lastUploadedBytes = 0;
  Duration _totalTime = Duration.zero;

  UploadPhase get currentPhase => _currentPhase;
  TransferStep get transferStep => _transferStep;
  MissionStage get missionStage => _missionStage;
  double get transferProgress => _transferProgress;
  String get fileName => _fileName;
  int get fileSize => _fileSize;
  double get speedMBps => _speedMBps;
  Duration get eta => _eta;
  String get errorMessage => _errorMessage;
  bool get hasError => _hasError;
  bool get isUploading => _isUploading;
  bool get isCompleted => _isCompleted;
  Duration get totalTime => _totalTime;

  double get analysisProgress =>
      (_missionStage.index + 1) / MissionStage.values.length;

  void startUpload(String fileName, {int fileSize = 0}) {
    _isUploading = true;
    _isCompleted = false;
    _hasError = false;
    _errorMessage = '';
    _currentPhase = UploadPhase.transfer;
    _transferStep = TransferStep.preparing;
    _transferProgress = 0.0;
    _fileName = fileName;
    _fileSize = fileSize;
    _speedMBps = 0.0;
    _eta = Duration.zero;
    _startTime = DateTime.now();
    _lastUploadTime = DateTime.now();
    _lastUploadedBytes = 0;
    _missionStage = MissionStage.receiveFile;
    notifyListeners();
  }

  void updateDioProgress(int sent, int total) {
    if (total <= 0 || _currentPhase != UploadPhase.transfer) return;
    if (_transferStep == TransferStep.preparing) {
      _transferStep = TransferStep.uploading;
    }
    _transferProgress = (sent / total).clamp(0.0, 1.0);
    final now = DateTime.now();
    if (_lastUploadTime != null) {
      final elapsedMs = now.difference(_lastUploadTime!).inMilliseconds;
      if (elapsedMs > 500) {
        final bytesSinceLast = sent - _lastUploadedBytes;
        final speedBps = bytesSinceLast / (elapsedMs / 1000);
        _speedMBps = speedBps / (1024 * 1024);
        if (speedBps > 0) {
          _eta = Duration(seconds: ((total - sent) / speedBps).toInt());
        }
        _lastUploadedBytes = sent;
        _lastUploadTime = now;
      }
    }
    if (_transferProgress >= 1.0 && _transferStep != TransferStep.completed) {
      _transferStep = TransferStep.verifying;
      _speedMBps = 0.0;
      _eta = Duration.zero;
    }
    notifyListeners();
  }

  void completeTransfer() {
    if (_currentPhase != UploadPhase.transfer) return;
    _transferStep = TransferStep.completed;
    _transferProgress = 1.0;
    _currentPhase = UploadPhase.analysis;
    notifyListeners();
  }

  void updateAnalysisStep(String backendStep) {
    if (_currentPhase == UploadPhase.transfer) completeTransfer();
    switch (backendStep) {
      case 'RECEIVE_FILE': _missionStage = MissionStage.receiveFile; break;
      case 'STORE_FILE': _missionStage = MissionStage.storeFile; break;
      case 'DETECT_FORMAT': _missionStage = MissionStage.detectFormat; break;
      case 'READ_DOCUMENT': _missionStage = MissionStage.readDocument; break;
      case 'EXTRACT_TEXT': _missionStage = MissionStage.extractText; break;
      case 'NORMALIZE_TEXT': _missionStage = MissionStage.normalizeText; break;
      case 'BUILD_PROFILE': _missionStage = MissionStage.buildProfile; break;
      case 'SAVE_PROFILE': _missionStage = MissionStage.saveProfile; break;
      case 'UPDATE_RUNTIME': _missionStage = MissionStage.updateRuntime; break;
      case 'COMPLETE': _missionStage = MissionStage.complete; break;
    }
    notifyListeners();
  }

  void setError(String message) {
    _errorMessage = message;
    _hasError = true;
    _isUploading = false;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = '';
    _hasError = false;
    _isUploading = true;
    notifyListeners();
  }

  void completeProcess() {
    _isCompleted = true;
    _isUploading = false;
    _hasError = false;
    _missionStage = MissionStage.complete;
    if (_startTime != null) {
      _totalTime = DateTime.now().difference(_startTime!);
    }
    notifyListeners();
  }

  void reset() {
    _isUploading = false;
    _isCompleted = false;
    _hasError = false;
    _errorMessage = '';
    _currentPhase = UploadPhase.transfer;
    _transferStep = TransferStep.preparing;
    _transferProgress = 0.0;
    _fileName = '';
    _fileSize = 0;
    _speedMBps = 0.0;
    _eta = Duration.zero;
    _startTime = null;
    _lastUploadTime = null;
    _lastUploadedBytes = 0;
    _totalTime = Duration.zero;
    _missionStage = MissionStage.receiveFile;
    notifyListeners();
  }
}
