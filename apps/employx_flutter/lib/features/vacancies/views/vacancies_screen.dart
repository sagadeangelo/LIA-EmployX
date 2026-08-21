import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/vacancy_model.dart';
import '../providers/vacancy_provider.dart';
import '../services/location_resolver.dart';
import '../services/device_location_service.dart';

import '../../profile/providers/profile_hub_provider.dart';
import '../../../core/models/professional_profile_model.dart';

class VacanciesScreen extends StatefulWidget {
  const VacanciesScreen({super.key});

  @override
  State<VacanciesScreen> createState() => _VacanciesScreenState();
}

class _VacanciesScreenState extends State<VacanciesScreen> {
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _locationController = TextEditingController();

  String _selectedMode = 'Todas';
  String _selectedLevel = 'Todos';
  String _selectedMatch = 'Todos';
  String? _selectedJobId;
  
  bool _isDetectingLocation = false;

  final Set<String> _savedJobs = <String>{};

List<_Job> _mapVacanciesToJobs(
  List<VacancyModel> vacancies,
  ProfessionalProfile? profile,
) {
  return vacancies.map((vacancy) {
    return _Job(
      id: vacancy.id,
      title: vacancy.title.isEmpty
          ? 'Posición Confidencial'
          : vacancy.title,
      company: vacancy.company.isEmpty
          ? 'Empresa No Especificada'
          : vacancy.company,
      location: vacancy.location.isEmpty
          ? 'Ubicación remota'
          : vacancy.location,
      mode: _displayModality(vacancy.modality),
      level: vacancy.experienceLevel.isEmpty
          ? 'No especificado'
          : vacancy.experienceLevel,
      salary: _formatSalary(vacancy),
      match: _calculateInitialMatch(vacancy, profile),
      posted: _formatPostedDate(vacancy.postedAt),
      source: vacancy.source.isEmpty
          ? 'LIA EmployX'
          : vacancy.source,
      skills: vacancy.skills,
      description: vacancy.description,
    );
  }).toList();
}

String _displayModality(String modality) {
  final mod = modality.toLowerCase();
  if (mod.contains('remote')) return 'Remoto';
  if (mod.contains('hybrid')) return 'Híbrido';
  if (mod.contains('on-site') || mod.contains('onsite')) {
    return 'Presencial';
  }
  return modality.isEmpty ? 'Híbrido' : modality;
}

String _formatSalary(VacancyModel vacancy) {
  final min = vacancy.salaryMin;
  final max = vacancy.salaryMax;

  if (min == null && max == null) {
    return 'Salario a convenir';
  }

  final currency = vacancy.currency ?? 'MXN';

  if (min != null && max != null) {
    return '\$${_k(min)} - \$${_k(max)} $currency/año';
  }

  if (min != null) {
    return 'Desde \$${_k(min)} $currency/año';
  }

  return 'Hasta \$${_k(max!)} $currency/año';
}

String _k(num value) {
  if (value >= 1000) {
    return '${(value / 1000).toStringAsFixed(0)}k';
  }
  return value.toString();
}

int _calculateInitialMatch(VacancyModel vacancy, ProfessionalProfile? profile) {
  if (profile == null || profile.skills.items.isEmpty) {
    final skillCount = vacancy.skills.length;
    if (skillCount >= 8) return 90;
    if (skillCount >= 5) return 85;
    if (skillCount >= 3) return 80;
    if (skillCount >= 1) return 75;
    return 70;
  }

  final vacancySkills = vacancy.skills.map((s) => s.toLowerCase()).toSet();
  if (vacancySkills.isEmpty) return 70;

  final profileSkills = profile.skills.items.map((s) => s.name.toLowerCase()).toSet();
  
  int matchCount = 0;
  for (final vs in vacancySkills) {
    if (profileSkills.contains(vs)) {
      matchCount++;
    } else {
       for (final ps in profileSkills) {
         if (ps.contains(vs) || vs.contains(ps)) {
           matchCount++;
           break;
         }
       }
    }
  }

  final ratio = matchCount / vacancySkills.length;
  final score = 50 + (ratio * 50).toInt();
  return score.clamp(0, 100);
}

String _formatPostedDate(DateTime? date) {
  if (date == null) {
    return 'Fecha no disponible';
  }

  final difference = DateTime.now().difference(date);

  if (difference.inDays == 0) {
    return 'Hoy';
  }

  if (difference.inDays == 1) {
    return 'Hace 1 día';
  }

  if (difference.inDays < 30) {
    return 'Hace ${difference.inDays} días';
  }

  final months = (difference.inDays / 30).floor();

  if (months == 1) {
    return 'Hace 1 mes';
  }

  return 'Hace $months meses';
}
  String? _lastProfileId;

  @override
  void initState() {
    super.initState();
    // Ya no cargamos aquí porque didChangeDependencies se encargará al iniciar
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    final profile = context.watch<ProfileHubProvider>().activeProfessionalProfile;
    final currentProfileId = profile?.id;

    if (_lastProfileId != currentProfileId) {
      _lastProfileId = currentProfileId;

      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        _triggerProfileSearch(profile);
      });
    }
  }

  /// Construye el query profesional y resuelve la ubicación, luego
  /// dispara una búsqueda en VacancyProvider con los parámetros correctos.
  void _triggerProfileSearch(ProfessionalProfile? profile) {
    final provider = context.read<VacancyProvider>();

    if (profile == null) {
      provider.loadInitialVacancies();
      return;
    }

    // ── Query profesional (cargo + top skills, SIN ubicación) ──
    final role = profile.personalInfo.currentPosition.trim();
    final topSkills = profile.skills.items
        .take(5)
        .map((s) => s.name)
        .join(' ');
    final query = role.isNotEmpty ? '$role $topSkills'.trim() : topSkills;

    // ── Resolución de ubicación → código ISO ──────────────────
    final locationText = _locationController.text.trim();
    final resolved = LocationResolver.resolve(locationText);

    provider.search(
      query: query,
      countries: resolved?.countryCode ?? '',
      city: resolved?.city,
      region: resolved?.region,
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  // ── Ranking geográfico ───────────────────────────────────────

  /// Ordena los trabajos aplicando prioridad geográfica:
  ///   1. Ciudad exacta  2. Estado/Región  3. País  4. Remoto  5. Internacional
  List<_Job> _applyGeoRanking(List<_Job> jobs) {
    final provider = context.read<VacancyProvider>();
    final city = (provider.city ?? '').toLowerCase();
    final region = (provider.region ?? '').toLowerCase();

    if (city.isEmpty && region.isEmpty) return jobs;

    int geoScore(_Job job) {
      final loc = job.location.toLowerCase();
      if (city.isNotEmpty && loc.contains(city)) return 5;
      if (region.isNotEmpty && loc.contains(region)) return 4;
      if (job.mode.toLowerCase().contains('remoto') ||
          job.mode.toLowerCase().contains('remote')) {
        return 3;
      }
      if (job.location.isNotEmpty) return 2;
      return 1;
    }

    final sorted = [...jobs]..sort((a, b) {
      final geo = geoScore(b).compareTo(geoScore(a));
      if (geo != 0) return geo;
      return b.match.compareTo(a.match);
    });
    return sorted;
  }

  List<_Job> get _filteredJobs {
    final provider = context.read<VacancyProvider>();
    final profile = context.read<ProfileHubProvider>().activeProfessionalProfile;
    final liveJobs = _mapVacanciesToJobs(provider.vacancies, profile);

    final query = _searchController.text.trim().toLowerCase();

    final filtered = liveJobs.where((job) {
      final matchesQuery = query.isEmpty ||
          job.title.toLowerCase().contains(query) ||
          job.company.toLowerCase().contains(query) ||
          job.skills.any(
            (skill) => skill.toLowerCase().contains(query),
          );

      final matchesMode =
          _selectedMode == 'Todas' || job.mode == _selectedMode;

      final matchesLevel =
          _selectedLevel == 'Todos' || job.level == _selectedLevel;

      final matchesScore = switch (_selectedMatch) {
        '90%+' => job.match >= 90,
        '80%+' => job.match >= 80,
        '70%+' => job.match >= 70,
        _ => true,
      };

      return matchesQuery &&
          matchesMode &&
          matchesLevel &&
          matchesScore;
    }).toList();

    return _applyGeoRanking(filtered);
  }

  _Job? get _selectedJob {
    if (_selectedJobId == null) return null;
    final provider = context.read<VacancyProvider>();
    final profile = context.read<ProfileHubProvider>().activeProfessionalProfile;
    final liveJobs = _mapVacanciesToJobs(provider.vacancies, profile);
    for (final job in liveJobs) {
      if (job.id == _selectedJobId) return job;
    }
    return null;
  }

  void _selectJob(_Job job) {
    setState(() {
      _selectedJobId = job.id;
    });
  }

  void _toggleSaved(_Job job) {
    setState(() {
      if (_savedJobs.contains(job.id)) {
        _savedJobs.remove(job.id);
      } else {
        _savedJobs.add(job.id);
      }
    });
  }

  Future<void> _clearFilters() async {
    setState(() {
      _searchController.clear();
      _locationController.clear();
      _selectedMode = 'Todas';
      _selectedLevel = 'Todos';
      _selectedMatch = 'Todos';
      _selectedJobId = null;
    });

    final profile = context.read<ProfileHubProvider>().activeProfessionalProfile;
    _triggerProfileSearch(profile);
  }

  Future<void> _performSearch() async {
    FocusScope.of(context).unfocus();

    // El campo de búsqueda manual anula el contexto de perfil,
    // pero la ubicación sigue resolviéndose como código ISO.
    final locationText = _locationController.text.trim();
    final resolved = LocationResolver.resolve(locationText);

    await context.read<VacancyProvider>().search(
          query: _searchController.text.trim(),
          countries: resolved?.countryCode ?? '',
          city: resolved?.city,
          region: resolved?.region,
        );

    if (!mounted) return;
    setState(() {
      _selectedJobId = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final provider = context.watch<VacancyProvider>();

    return Scaffold(
      backgroundColor: colors.surface,
      body: LayoutBuilder(
        builder: (context, constraints) {
          final wide = constraints.maxWidth >= 1150;

          return SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(28, 30, 28, 40),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(context),
                const SizedBox(height: 24),
                _buildSearchPanel(context),
                const SizedBox(height: 26),
                _buildStats(context),
                const SizedBox(height: 26),
                if (provider.isLoading && provider.vacancies.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 80),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  )
                else if (provider.errorMessage != null &&
                    provider.vacancies.isEmpty)
                  _buildErrorState(context, provider.errorMessage!)
                else if (wide)
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        flex: 58,
                        child: _buildResults(context),
                      ),
                      const SizedBox(width: 22),
                      Expanded(
                        flex: 42,
                        child: _buildJobDetail(context),
                      ),
                    ],
                  )
                else ...[
                  _buildResults(context),
                  const SizedBox(height: 22),
                  _buildJobDetail(context),
                ],
                if (provider.isLoading && provider.vacancies.isNotEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 18),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, String message) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: colors.error.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: colors.error.withValues(alpha: 0.22),
        ),
      ),
      child: Column(
        children: [
          Icon(
            Icons.cloud_off_outlined,
            size: 46,
            color: colors.error,
          ),
          const SizedBox(height: 14),
          const Text(
            'No fue posible cargar las vacantes',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.62),
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: () {
              context.read<VacancyProvider>().loadInitialVacancies();
            },
            icon: const Icon(Icons.refresh),
            label: const Text('REINTENTAR'),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _GlowIcon(
                    icon: Icons.work_outline,
                    color: colors.primary,
                  ),
                  const SizedBox(width: 14),
                  Text(
                    'JOB HUNTER',
                    style: TextStyle(
                      color: colors.primary,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 2.2,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              const Text(
                'Vacantes',
                style: TextStyle(
                  fontSize: 34,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.8,
                ),
              ),
              const SizedBox(height: 7),
              Text(
                'Encuentra oportunidades y deja que LIA determine cuáles encajan mejor contigo.',
                style: TextStyle(
                  color: colors.onSurface.withValues(alpha: 0.62),
                  fontSize: 15,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 20),
        _AgentStatus(),
      ],
    );
  }

  Future<void> _detectLocation() async {
    setState(() {
      _isDetectingLocation = true;
    });

    try {
      final result = await DeviceLocationService.detectLocation();

      if (!mounted) return;

      if (result is LocationSuccess) {
        _locationController.text = result.location.displayName;
        await _performSearch();
      } else if (result is LocationError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('No fue posible detectar la ubicación: $e'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDetectingLocation = false;
        });
      }
    }
  }

  Widget _buildSearchPanel(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: colors.surfaceContainerHighest.withValues(alpha: 0.42),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: colors.primary.withValues(alpha: 0.22),
        ),
        boxShadow: [
          BoxShadow(
            color: colors.primary.withValues(alpha: 0.06),
            blurRadius: 30,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                flex: 5,
                child: _SearchField(
                  controller: _searchController,
                  icon: Icons.search,
                  hint: 'Puesto, empresa o skill...',
                  onChanged: (_) => setState(() {}),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: 3,
                child: _SearchField(
                  controller: _locationController,
                  icon: Icons.location_on_outlined,
                  hint: 'Ubicación...',
                  onChanged: (_) => setState(() {}),
                  suffixIcon: _isDetectingLocation 
                      ? const Padding(
                          padding: EdgeInsets.all(14.0),
                          child: SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        )
                      : IconButton(
                          icon: const Icon(Icons.my_location, size: 20),
                          onPressed: _detectLocation,
                          tooltip: 'Usar mi ubicación',
                          color: colors.primary,
                        ),
                ),
              ),
              const SizedBox(width: 12),
              SizedBox(
                height: 50,
                child: FilledButton.icon(
                  onPressed: _performSearch,
                  icon: const Icon(Icons.search, size: 19),
                  label: const Text('BUSCAR'),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    backgroundColor: colors.primary,
                    foregroundColor: colors.onPrimary,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _FilterDropdown(
                label: 'Modalidad',
                value: _selectedMode,
                items: const [
                  'Todas',
                  'Remoto',
                  'Híbrido',
                  'Presencial',
                ],
                onChanged: (value) {
                  if (value == null) return;
                  setState(() => _selectedMode = value);
                },
              ),
              _FilterDropdown(
                label: 'Experiencia',
                value: _selectedLevel,
                items: const [
                  'Todos',
                  'Junior',
                  'Mid',
                  'Senior',
                ],
                onChanged: (value) {
                  if (value == null) return;
                  setState(() => _selectedLevel = value);
                },
              ),
              _FilterDropdown(
                label: 'Match LIA',
                value: _selectedMatch,
                items: const [
                  'Todos',
                  '90%+',
                  '80%+',
                  '70%+',
                ],
                onChanged: (value) {
                  if (value == null) return;
                  setState(() => _selectedMatch = value);
                },
              ),
              TextButton.icon(
                onPressed: () {
                  _clearFilters();
                },
                icon: const Icon(Icons.refresh, size: 17),
                label: const Text('Limpiar filtros'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStats(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final jobs = _filteredJobs;

    final average = jobs.isEmpty
        ? 0
        : (jobs.map((job) => job.match).reduce((a, b) => a + b) / jobs.length)
            .round();

    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.work_outline,
            title: 'VACANTES',
            value: '${jobs.length}',
            subtitle: 'encontradas',
            color: colors.primary,
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: _StatCard(
            icon: Icons.auto_awesome,
            title: 'MATCH LIA',
            value: '$average%',
            subtitle: 'compatibilidad promedio',
            color: const Color(0xFFB46CFF),
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: _StatCard(
            icon: Icons.bolt,
            title: 'TOP MATCH',
            value: jobs.isEmpty ? '—' : '${jobs.first.match}%',
            subtitle: 'mejor oportunidad',
            color: const Color(0xFF00C9FF),
          ),
        ),
      ],
    );
  }

  Widget _buildResults(BuildContext context) {
    final jobs = _filteredJobs;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text(
              'Oportunidades',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 10),
            _SmallBadge(text: '${jobs.length} resultados'),
            const Spacer(),
            Icon(
              Icons.sort,
              size: 17,
              color: Theme.of(context)
                  .colorScheme
                  .onSurface
                  .withValues(alpha: 0.55),
            ),
            const SizedBox(width: 5),
            Text(
              'Mejor match',
              style: TextStyle(
                color: Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withValues(alpha: 0.55),
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        if (jobs.isEmpty)
          _EmptyResults(onClear: () {
            _clearFilters();
          })
        else
          ...jobs.map(
            (job) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _JobCard(
                job: job,
                selected: job.id == _selectedJobId,
                saved: _savedJobs.contains(job.id),
                onTap: () => _selectJob(job),
                onSave: () => _toggleSaved(job),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildJobDetail(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final job = _selectedJob;

    if (job == null) {
      return Container(
        constraints: const BoxConstraints(minHeight: 430),
        padding: const EdgeInsets.all(30),
        decoration: BoxDecoration(
          color: colors.surfaceContainerHighest.withValues(alpha: 0.28),
          borderRadius: BorderRadius.circular(22),
          border: Border.all(
            color: colors.outline.withValues(alpha: 0.18),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.radar,
              size: 58,
              color: colors.primary.withValues(alpha: 0.8),
            ),
            const SizedBox(height: 18),
            const Text(
              'Selecciona una vacante',
              style: TextStyle(
                fontSize: 23,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 9),
            Text(
              'Aquí aparecerá el análisis de compatibilidad de LIA.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: colors.onSurface.withValues(alpha: 0.58),
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.surfaceContainerHighest.withValues(alpha: 0.28),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: colors.primary.withValues(alpha: 0.25),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'ANÁLISIS DE OPORTUNIDAD',
                  style: TextStyle(
                    color: colors.primary,
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.7,
                  ),
                ),
              ),
              IconButton(
                onPressed: () => _toggleSaved(job),
                icon: Icon(
                  _savedJobs.contains(job.id)
                      ? Icons.bookmark
                      : Icons.bookmark_border,
                  color: _savedJobs.contains(job.id)
                      ? colors.primary
                      : colors.onSurface.withValues(alpha: 0.55),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            job.title,
            style: const TextStyle(
              fontSize: 25,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            job.company,
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.65),
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 18),
          _MatchGauge(score: job.match),
          const SizedBox(height: 20),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _InfoChip(
                icon: Icons.location_on_outlined,
                text: job.location,
              ),
              _InfoChip(
                icon: Icons.laptop_mac_outlined,
                text: job.mode,
              ),
              _InfoChip(
                icon: Icons.bar_chart,
                text: job.level,
              ),
            ],
          ),
          const SizedBox(height: 22),
          const Text(
            'Por qué encaja contigo',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            job.description,
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.65),
              height: 1.5,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Skills detectadas',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: job.skills
                .map(
                  (skill) => Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: colors.primary.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(9),
                      border: Border.all(
                        color: colors.primary.withValues(alpha: 0.25),
                      ),
                    ),
                    child: Text(
                      skill,
                      style: TextStyle(
                        color: colors.primary,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 22),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF00C9FF).withValues(alpha: 0.06),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: const Color(0xFF00C9FF).withValues(alpha: 0.16),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.psychology_outlined,
                  color: Color(0xFF00C9FF),
                ),
                const SizedBox(width: 11),
                Expanded(
                  child: Text(
                    'LIA puede enviar esta vacante al ATS para realizar un análisis profundo.',
                    style: TextStyle(
                      color: colors.onSurface.withValues(alpha: 0.68),
                      fontSize: 12,
                      height: 1.35,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: FilledButton.icon(
              onPressed: () => _showAtsPreview(context, job),
              icon: const Icon(Icons.analytics_outlined),
              label: const Text('ANALIZAR CON ATS'),
              style: FilledButton.styleFrom(
                backgroundColor: colors.primary,
                foregroundColor: colors.onPrimary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(13),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showAtsPreview(BuildContext context, _Job job) {
    final colors = Theme.of(context).colorScheme;

    showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          backgroundColor: colors.surfaceContainerHighest,
          title: const Row(
            children: [
              Icon(Icons.analytics_outlined),
              SizedBox(width: 10),
              Text('ATS Analyzer'),
            ],
          ),
          content: SizedBox(
            width: 460,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  job.title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(job.company),
                const SizedBox(height: 20),
                _PreviewRow(
                  label: 'Match actual',
                  value: '${job.match}%',
                ),
                _PreviewRow(
                  label: 'Skills detectadas',
                  value: '${job.skills.length}',
                ),
                const SizedBox(height: 15),
                Text(
                  'En la siguiente etapa esta acción conectará la vacante con el ATS real y comparará requisitos contra tu perfil profesional.',
                  style: TextStyle(
                    color: colors.onSurface.withValues(alpha: 0.65),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cerrar'),
            ),
          ],
        );
      },
    );
  }
}

class _Job {
  final String id;
  final String title;
  final String company;
  final String location;
  final String mode;
  final String level;
  final String salary;
  final int match;
  final String posted;
  final String source;
  final List<String> skills;
  final String description;

  const _Job({
    required this.id,
    required this.title,
    required this.company,
    required this.location,
    required this.mode,
    required this.level,
    required this.salary,
    required this.match,
    required this.posted,
    required this.source,
    required this.skills,
    required this.description,
  });
}

class _GlowIcon extends StatelessWidget {
  final IconData icon;
  final Color color;

  const _GlowIcon({
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: color.withValues(alpha: 0.35),
        ),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.12),
            blurRadius: 18,
          ),
        ],
      ),
      child: Icon(icon, color: color, size: 23),
    );
  }
}

class _AgentStatus extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 14,
        vertical: 11,
      ),
      decoration: BoxDecoration(
        color: const Color(0xFF00C98D).withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: const Color(0xFF00C98D).withValues(alpha: 0.25),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: const BoxDecoration(
              color: Color(0xFF00C98D),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 9),
          Text(
            'JOB HUNTER READY',
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.78),
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
            ),
          ),
        ],
      ),
    );
  }
}

class _SearchField extends StatelessWidget {
  final TextEditingController controller;
  final IconData icon;
  final String hint;
  final ValueChanged<String>? onChanged;
  final Widget? suffixIcon;

  const _SearchField({
    required this.controller,
    required this.icon,
    required this.hint,
    this.onChanged,
    this.suffixIcon,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return TextField(
      controller: controller,
      onChanged: onChanged,
      style: const TextStyle(fontSize: 14),
      decoration: InputDecoration(
        prefixIcon: Icon(
          icon,
          size: 20,
          color: colors.primary,
        ),
        suffixIcon: suffixIcon,
        hintText: hint,
        hintStyle: TextStyle(
          color: colors.onSurface.withValues(alpha: 0.4),
        ),
        filled: true,
        fillColor: colors.surface.withValues(alpha: 0.55),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 15,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: colors.outline.withValues(alpha: 0.18),
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: colors.outline.withValues(alpha: 0.18),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(
            color: colors.primary.withValues(alpha: 0.65),
          ),
        ),
      ),
    );
  }
}

class _FilterDropdown extends StatelessWidget {
  final String label;
  final String value;
  final List<String> items;
  final ValueChanged<String?> onChanged;

  const _FilterDropdown({
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(11),
        border: Border.all(
          color: colors.outline.withValues(alpha: 0.17),
        ),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isDense: true,
          dropdownColor: colors.surfaceContainerHighest,
          icon: const Icon(Icons.keyboard_arrow_down, size: 17),
          items: items
              .map(
                (item) => DropdownMenuItem<String>(
                  value: item,
                  child: Text(
                    '$label: $item',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
              )
              .toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final String subtitle;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.subtitle,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colors.surfaceContainerHighest.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(17),
        border: Border.all(
          color: colors.outline.withValues(alpha: 0.16),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 21),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: colors.onSurface.withValues(alpha: 0.45),
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 3),
                Row(
                  children: [
                    Text(
                      value,
                      style: const TextStyle(
                        fontSize: 21,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(width: 7),
                    Flexible(
                      child: Text(
                        subtitle,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: colors.onSurface.withValues(alpha: 0.52),
                          fontSize: 11,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SmallBadge extends StatelessWidget {
  final String text;

  const _SmallBadge({
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: colors.primary.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: colors.primary,
          fontSize: 10,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _JobCard extends StatelessWidget {
  final _Job job;
  final bool selected;
  final bool saved;
  final VoidCallback onTap;
  final VoidCallback onSave;

  const _JobCard({
    required this.job,
    required this.selected,
    required this.saved,
    required this.onTap,
    required this.onSave,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: selected
                ? colors.primary.withValues(alpha: 0.055)
                : colors.surfaceContainerHighest.withValues(alpha: 0.24),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: selected
                  ? colors.primary.withValues(alpha: 0.5)
                  : colors.outline.withValues(alpha: 0.15),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          colors.primary.withValues(alpha: 0.2),
                          const Color(0xFF8B5CF6).withValues(alpha: 0.12),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.business_center_outlined,
                      color: colors.primary,
                    ),
                  ),
                  const SizedBox(width: 13),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          job.title,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          job.company,
                          style: TextStyle(
                            color: colors.onSurface.withValues(alpha: 0.58),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _MatchBadge(score: job.match),
                  const SizedBox(width: 4),
                  IconButton(
                    tooltip: saved ? 'Quitar de guardadas' : 'Guardar',
                    onPressed: onSave,
                    icon: Icon(
                      saved ? Icons.bookmark : Icons.bookmark_border,
                      size: 20,
                      color: saved
                          ? colors.primary
                          : colors.onSurface.withValues(alpha: 0.45),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Wrap(
                spacing: 7,
                runSpacing: 7,
                children: [
                  _MiniInfo(
                    icon: Icons.location_on_outlined,
                    text: job.location,
                  ),
                  _MiniInfo(
                    icon: Icons.laptop_mac_outlined,
                    text: job.mode,
                  ),
                  _MiniInfo(
                    icon: Icons.work_outline,
                    text: job.level,
                  ),
                ],
              ),
              const SizedBox(height: 13),
              Text(
                job.salary,
                style: TextStyle(
                  color: const Color(0xFF00C98D),
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: job.skills
                          .take(4)
                          .map(
                            (skill) => Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 5,
                              ),
                              decoration: BoxDecoration(
                                color: colors.primary.withValues(alpha: 0.055),
                                borderRadius: BorderRadius.circular(7),
                              ),
                              child: Text(
                                skill,
                                style: TextStyle(
                                  color: colors.primary.withValues(alpha: 0.9),
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    '${job.source} · ${job.posted}',
                    style: TextStyle(
                      color: colors.onSurface.withValues(alpha: 0.4),
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MatchBadge extends StatelessWidget {
  final int score;

  const _MatchBadge({
    required this.score,
  });

  @override
  Widget build(BuildContext context) {
    final color = score >= 90
        ? const Color(0xFF00C98D)
        : score >= 80
            ? const Color(0xFF00C9FF)
            : const Color(0xFFB46CFF);

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 10,
        vertical: 7,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(9),
        border: Border.all(
          color: color.withValues(alpha: 0.25),
        ),
      ),
      child: Text(
        '$score% MATCH',
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _MiniInfo extends StatelessWidget {
  final IconData icon;
  final String text;

  const _MiniInfo({
    required this.icon,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          size: 14,
          color: colors.onSurface.withValues(alpha: 0.42),
        ),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            color: colors.onSurface.withValues(alpha: 0.52),
            fontSize: 10,
          ),
        ),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String text;

  const _InfoChip({
    required this.icon,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 9,
        vertical: 7,
      ),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: colors.outline.withValues(alpha: 0.14),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: colors.primary,
          ),
          const SizedBox(width: 5),
          Text(
            text,
            style: const TextStyle(fontSize: 10),
          ),
        ],
      ),
    );
  }
}

class _MatchGauge extends StatelessWidget {
  final int score;

  const _MatchGauge({
    required this.score,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Row(
      children: [
        SizedBox(
          width: 82,
          height: 82,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 74,
                height: 74,
                child: CircularProgressIndicator(
                  value: score / 100,
                  strokeWidth: 7,
                  backgroundColor:
                      colors.onSurface.withValues(alpha: 0.07),
                  valueColor: AlwaysStoppedAnimation<Color>(
                    score >= 90
                        ? const Color(0xFF00C98D)
                        : colors.primary,
                  ),
                ),
              ),
              Text(
                '$score%',
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 15),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'COMPATIBILIDAD LIA',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              score >= 90
                  ? 'Excelente oportunidad'
                  : 'Buena oportunidad',
              style: TextStyle(
                color: colors.onSurface.withValues(alpha: 0.58),
                fontSize: 12,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _EmptyResults extends StatelessWidget {
  final VoidCallback onClear;

  const _EmptyResults({
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(40),
      decoration: BoxDecoration(
        color: colors.surfaceContainerHighest.withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: colors.outline.withValues(alpha: 0.14),
        ),
      ),
      child: Column(
        children: [
          Icon(
            Icons.search_off,
            size: 42,
            color: colors.primary.withValues(alpha: 0.7),
          ),
          const SizedBox(height: 12),
          const Text(
            'No encontramos vacantes',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 7),
          Text(
            'Prueba modificando los filtros o las palabras de búsqueda.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.55),
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 15),
          TextButton(
            onPressed: onClear,
            child: const Text('Limpiar filtros'),
          ),
        ],
      ),
    );
  }
}

class _PreviewRow extends StatelessWidget {
  final String label;
  final String value;

  const _PreviewRow({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                color: colors.onSurface.withValues(alpha: 0.55),
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}
