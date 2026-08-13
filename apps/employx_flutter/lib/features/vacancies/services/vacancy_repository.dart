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

  /// Realiza una búsqueda de vacantes con contexto profesional y
  /// filtro geográfico estructurado.
  ///
  /// [query] debe contener solo contexto profesional (cargo, skills).
  ///
  /// [countries] recibe códigos ISO 3166-1 alpha-2 separados por
  /// coma (ej. "mx", "mx,us"). Corresponde al parámetro real
  /// que soporta FreeHire en /jobs/search.
  Future<List<VacancyModel>> searchJobs({
    String query = '',
    String countries = '',
    int limit = 20,
    int offset = 0,
  }) {
    return _freeHireProvider.searchJobs(
      query: query,
      countries: countries,
      limit: limit,
      offset: offset,
    );
  }
}