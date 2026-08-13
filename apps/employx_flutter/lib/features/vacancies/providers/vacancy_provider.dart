import 'package:flutter/foundation.dart';

import '../models/vacancy_model.dart';
import '../services/vacancy_repository.dart';

/// Proveedor de estado central para el Job Hunter.
///
/// Gestiona la búsqueda de vacantes garantizando:
///
/// - Invalidación inmediata de resultados al cambiar de CV.
/// - Protección contra race conditions mediante [_searchGeneration].
/// - Separación entre contexto profesional (query) y
///   filtro geográfico (countries).
/// - Conservación de ciudad/región para el ranking geográfico
///   posterior que realiza VacanciesScreen.
class VacancyProvider extends ChangeNotifier {
  final VacancyRepository _repository;

  VacancyProvider({
    VacancyRepository? repository,
  }) : _repository = repository ?? VacancyRepository();

  List<VacancyModel> _vacancies = const [];

  bool _isLoading = false;

  String? _errorMessage;

  // ── Contexto de búsqueda actual ──────────────────────────────

  /// Query profesional: cargo + skills. NUNCA contiene ubicación.
  String _query = '';

  /// Código(s) ISO del país enviado a FreeHire como `countries`.
  String _countries = '';

  /// Ciudad extraída del texto libre del usuario.
  /// Usada para el ranking geográfico local; NO se envía a la API.
  String? _city;

  /// Región/estado extraída del texto libre del usuario.
  String? _region;

  // ── Paginación ───────────────────────────────────────────────
  int _currentOffset = 0;
  bool _hasMore = true;

  // ── Race-condition guard ─────────────────────────────────────
  /// Incrementado en cada nueva llamada a search().
  /// Permite descartar respuestas de búsquedas obsoletas.
  int _searchGeneration = 0;

  // ── Getters públicos ─────────────────────────────────────────

  List<VacancyModel> get vacancies => List.unmodifiable(_vacancies);
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get query => _query;
  String get countries => _countries;

  /// Ciudad del usuario (para uso del ranking en la UI).
  String? get city => _city;

  /// Región/estado del usuario (para uso del ranking en la UI).
  String? get region => _region;

  bool get hasMore => _hasMore;
  int get resultCount => _vacancies.length;

  // ── Carga inicial (sin contexto de perfil) ───────────────────

  Future<void> loadInitialVacancies({
    int limit = 20,
  }) async {
    if (_isLoading) return;

    final generation = ++_searchGeneration;

    _setLoading(true);
    _errorMessage = null;
    _currentOffset = 0;
    _hasMore = true;
    _query = '';
    _countries = '';
    _city = null;
    _region = null;

    // Limpiar resultados del CV anterior INMEDIATAMENTE
    _vacancies = const [];
    notifyListeners();

    try {
      final results = await _repository.getJobs(
        limit: limit,
        offset: 0,
      );

      // Descartar si llegó una búsqueda más nueva mientras esperábamos
      if (generation != _searchGeneration) return;

      _vacancies = results;
      _currentOffset = results.length;
      _hasMore = results.length >= limit;
    } catch (error) {
      if (generation != _searchGeneration) return;
      _errorMessage = _readableError(error);
      _vacancies = const [];
      _hasMore = false;
    } finally {
      if (generation == _searchGeneration) {
        _setLoading(false);
      }
    }
  }

  // ── Búsqueda con contexto de perfil ─────────────────────────

  /// Ejecuta una búsqueda diferenciada por CV activo.
  ///
  /// [query] contiene solo contexto profesional (cargo + skills).
  ///
  /// [countries] es el código ISO resuelto a partir del texto de
  /// ubicación del usuario. Se envía directamente a FreeHire.
  ///
  /// [city] y [region] se conservan para el ranking geográfico
  /// posterior en VacanciesScreen. NO se envían a la API.
  Future<void> search({
    String query = '',
    String countries = '',
    String? city,
    String? region,
    int limit = 20,
  }) async {
    if (_isLoading) return;

    // Incrementar generación ANTES de limpiar para que cualquier
    // respuesta en vuelo de la generación anterior sea descartada.
    final generation = ++_searchGeneration;

    _setLoading(true);
    _errorMessage = null;
    _query = query.trim();
    _countries = countries.trim();
    _city = city?.trim().isNotEmpty == true ? city!.trim() : null;
    _region = region?.trim().isNotEmpty == true ? region!.trim() : null;
    _currentOffset = 0;
    _hasMore = true;

    // Limpiar resultados del CV anterior INMEDIATAMENTE
    _vacancies = const [];
    notifyListeners();

    try {
      final results = await _repository.searchJobs(
        query: _query,
        countries: _countries,
        limit: limit,
        offset: 0,
      );

      // Descartar si llegó una búsqueda más nueva mientras esperábamos
      if (generation != _searchGeneration) return;

      _vacancies = results;
      _currentOffset = results.length;
      _hasMore = results.length >= limit;
    } catch (error) {
      if (generation != _searchGeneration) return;
      _errorMessage = _readableError(error);
      _vacancies = const [];
      _hasMore = false;
    } finally {
      if (generation == _searchGeneration) {
        _setLoading(false);
      }
    }
  }

  // ── Paginación ───────────────────────────────────────────────

  Future<void> loadMore({
    int limit = 20,
  }) async {
    if (_isLoading || !_hasMore) return;

    final generation = _searchGeneration;
    _setLoading(true);

    try {
      final results = _query.isEmpty
          ? await _repository.getJobs(
              limit: limit,
              offset: _currentOffset,
            )
          : await _repository.searchJobs(
              query: _query,
              countries: _countries,
              limit: limit,
              offset: _currentOffset,
            );

      if (generation != _searchGeneration) return;

      if (results.isEmpty) {
        _hasMore = false;
        return;
      }

      _vacancies = [..._vacancies, ...results];
      _currentOffset += results.length;
      _hasMore = results.length >= limit;
    } catch (error) {
      if (generation != _searchGeneration) return;
      _errorMessage = _readableError(error);
    } finally {
      if (generation == _searchGeneration) {
        _setLoading(false);
      }
    }
  }

  // ── Utilidades ───────────────────────────────────────────────

  void clearError() {
    if (_errorMessage == null) return;
    _errorMessage = null;
    notifyListeners();
  }

  void clearResults() {
    ++_searchGeneration;
    _vacancies = const [];
    _query = '';
    _countries = '';
    _city = null;
    _region = null;
    _currentOffset = 0;
    _hasMore = true;
    _errorMessage = null;
    notifyListeners();
  }

  void _setLoading(bool value) {
    if (_isLoading == value) return;
    _isLoading = value;
    notifyListeners();
  }

  String _readableError(Object error) {
    if (error is FormatException) return error.message;
    return 'No fue posible cargar las vacantes. Intenta nuevamente.';
  }
}
