import '../models/vacancy_model.dart';
import 'freehire_provider.dart';

/// Punto de acceso principal a las vacantes para LIA-EmployX.
///
/// La UI y los Providers de Flutter no dependen directamente
/// de FreeHire. Esto permite agregar posteriormente otras fuentes
/// sin modificar la pantalla de Vacantes.
class VacancyRepository {
  final FreeHireProvider _freeHireProvider;

  VacancyRepository({
    FreeHireProvider? freeHireProvider,
  }) : _freeHireProvider = freeHireProvider ?? FreeHireProvider();

  /// Obtiene una primera página de vacantes.
  Future<List<VacancyModel>> getJobs({
    int limit = 20,
    int offset = 0,
  }) {
    return _freeHireProvider.getJobs(
      limit: limit,
      offset: offset,
    );
  }

  /// Realiza una búsqueda manual.
  Future<List<VacancyModel>> searchJobs({
    String query = '',
    int limit = 20,
    int offset = 0,
  }) {
    return _freeHireProvider.searchJobs(
      query: query,
      limit: limit,
      offset: offset,
    );
  }
}