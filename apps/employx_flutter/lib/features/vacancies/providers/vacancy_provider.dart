import 'package:flutter/foundation.dart';

import '../models/vacancy_model.dart';
import '../services/vacancy_repository.dart';

class VacancyProvider extends ChangeNotifier {
  final VacancyRepository _repository;

  VacancyProvider({
    VacancyRepository? repository,
  }) : _repository = repository ?? VacancyRepository();

  List<VacancyModel> _vacancies = const [];

  bool _isLoading = false;

  String? _errorMessage;

  String _query = '';

  int _currentOffset = 0;

  bool _hasMore = true;

  List<VacancyModel> get vacancies => List.unmodifiable(_vacancies);

  bool get isLoading => _isLoading;

  String? get errorMessage => _errorMessage;

  String get query => _query;

  bool get hasMore => _hasMore;

  int get resultCount => _vacancies.length;

  Future<void> loadInitialVacancies({
    int limit = 20,
  }) async {
    if (_isLoading) {
      return;
    }

    _setLoading(true);
    _errorMessage = null;
    _currentOffset = 0;
    _hasMore = true;

    try {
      final results = await _repository.getJobs(
        limit: limit,
        offset: 0,
      );

      _vacancies = results;
      _currentOffset = results.length;
      _hasMore = results.length >= limit;
    } catch (error) {
      _errorMessage = _readableError(error);
      _vacancies = const [];
      _hasMore = false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> search({
    String query = '',
    int limit = 20,
  }) async {
    if (_isLoading) {
      return;
    }

    final normalizedQuery = query.trim();

    _setLoading(true);
    _errorMessage = null;
    _query = normalizedQuery;
    _currentOffset = 0;
    _hasMore = true;

    try {
      final results = await _repository.searchJobs(
        query: normalizedQuery,
        limit: limit,
        offset: 0,
      );

      _vacancies = results;
      _currentOffset = results.length;
      _hasMore = results.length >= limit;
    } catch (error) {
      _errorMessage = _readableError(error);
      _vacancies = const [];
      _hasMore = false;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> loadMore({
    int limit = 20,
  }) async {
    if (_isLoading || !_hasMore) {
      return;
    }

    _setLoading(true);

    try {
      final results = _query.isEmpty
          ? await _repository.getJobs(
              limit: limit,
              offset: _currentOffset,
            )
          : await _repository.searchJobs(
              query: _query,
              limit: limit,
              offset: _currentOffset,
            );

      if (results.isEmpty) {
        _hasMore = false;
        return;
      }

      _vacancies = [
        ..._vacancies,
        ...results,
      ];

      _currentOffset += results.length;

      _hasMore = results.length >= limit;
    } catch (error) {
      _errorMessage = _readableError(error);
    } finally {
      _setLoading(false);
    }
  }

  void clearError() {
    if (_errorMessage == null) {
      return;
    }

    _errorMessage = null;
    notifyListeners();
  }

  void clearResults() {
    _vacancies = const [];
    _query = '';
    _currentOffset = 0;
    _hasMore = true;
    _errorMessage = null;

    notifyListeners();
  }

  void _setLoading(bool value) {
    if (_isLoading == value) {
      return;
    }

    _isLoading = value;
    notifyListeners();
  }

  String _readableError(Object error) {
    if (error is FormatException) {
      return error.message;
    }

    return 'No fue posible cargar las vacantes. Intenta nuevamente.';
  }
}