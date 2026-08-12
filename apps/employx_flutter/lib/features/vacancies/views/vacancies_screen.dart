import 'package:flutter/material.dart';

import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_glass_panel.dart';

class Vacancy {
  final String title;
  final String company;
  final String location;
  final String mode;
  final String level;
  final int match;
  final String salary;
  final List<String> skills;
  final String posted;
  final bool featured;

  const Vacancy({
    required this.title,
    required this.company,
    required this.location,
    required this.mode,
    required this.level,
    required this.match,
    required this.salary,
    required this.skills,
    required this.posted,
    this.featured = false,
  });
}

class VacanciesScreen extends StatefulWidget {
  const VacanciesScreen({super.key});

  @override
  State<VacanciesScreen> createState() => _VacanciesScreenState();
}

class _VacanciesScreenState extends State<VacanciesScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _query = '';
  String _location = 'Todas';
  String _mode = 'Todas';
  String _level = 'Todos';
  int _minimumMatch = 0;
  Vacancy? _selectedVacancy;

  static const List<Vacancy> _vacancies = [
    Vacancy(
      title: 'Full Stack Developer',
      company: 'TechNova Labs',
      location: 'México',
      mode: 'Remoto',
      level: 'Mid / Senior',
      match: 94,
      salary: '\$35k – \$55k MXN',
      skills: ['Flutter', 'Python', 'REST APIs', 'Git'],
      posted: 'Hace 2 días',
      featured: true,
    ),
    Vacancy(
      title: 'Software Developer',
      company: 'Northstar Digital',
      location: 'México / USA',
      mode: 'Remoto',
      level: 'Mid',
      match: 87,
      salary: '\$30k – \$48k MXN',
      skills: ['Python', 'Dart', 'SQL', 'Git'],
      posted: 'Hace 1 día',
    ),
    Vacancy(
      title: 'Ecommerce Technology Specialist',
      company: 'Commerce One',
      location: 'México',
      mode: 'Híbrido',
      level: 'Mid',
      match: 84,
      salary: '\$28k – \$42k MXN',
      skills: ['Ecommerce', 'Shopify', 'SEO', 'Analytics'],
      posted: 'Hace 3 días',
    ),
    Vacancy(
      title: 'Data & Automation Analyst',
      company: 'Lumen Analytics',
      location: 'México',
      mode: 'Remoto',
      level: 'Junior / Mid',
      match: 79,
      salary: '\$24k – \$38k MXN',
      skills: ['SQL', 'Python', 'BigQuery', 'Analytics'],
      posted: 'Hace 4 días',
    ),
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<Vacancy> get _filteredVacancies {
    final query = _query.trim().toLowerCase();
    return _vacancies.where((vacancy) {
      final matchesQuery = query.isEmpty ||
          vacancy.title.toLowerCase().contains(query) ||
          vacancy.company.toLowerCase().contains(query) ||
          vacancy.skills.any((skill) => skill.toLowerCase().contains(query));
      final matchesLocation = _location == 'Todas' || vacancy.location.contains(_location);
      final matchesMode = _mode == 'Todas' || vacancy.mode == _mode;
      final matchesLevel = _level == 'Todos' || vacancy.level.contains(_level);
      final matchesScore = vacancy.match >= _minimumMatch;
      return matchesQuery && matchesLocation && matchesMode && matchesLevel && matchesScore;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    final typography = context.liaTypography;

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          _buildBackground(colors),
          CustomScrollView(
            slivers: [
              SliverPadding(
                padding: EdgeInsets.fromLTRB(spacings.xl, spacings.xl, spacings.xl, spacings.xxl),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    _buildHero(context),
                    SizedBox(height: spacings.lg),
                    _buildSearchBar(context),
                    SizedBox(height: spacings.md),
                    _buildFilters(context),
                    SizedBox(height: spacings.xl),
                    Row(
                      children: [
                        Text('${_filteredVacancies.length} oportunidades encontradas', style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
                        const Spacer(),
                        _buildMatchLegend(context),
                      ],
                    ),
                    SizedBox(height: spacings.md),
                    if (_filteredVacancies.isEmpty)
                      _buildEmptyResults(context)
                    else
                      ..._filteredVacancies.map((vacancy) => Padding(
                            padding: EdgeInsets.only(bottom: spacings.md),
                            child: _buildVacancyCard(context, vacancy),
                          )),
                  ]),
                ),
              ),
            ],
          ),
          if (_selectedVacancy != null) _buildDetailOverlay(context, _selectedVacancy!),
        ],
      ),
    );
  }

  Widget _buildBackground(LiaColors colors) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [colors.background, const Color(0xFF0B1220), const Color(0xFF10091A)],
        ),
      ),
    );
  }

  Widget _buildHero(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaGlassPanel(
      hasGlow: true,
      glowColor: colors.accentPrimary,
      padding: EdgeInsets.all(spacings.xl),
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: colors.accentPrimary.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: colors.accentPrimary.withValues(alpha: 0.45)),
            ),
            child: Icon(Icons.travel_explore_rounded, color: colors.accentPrimary, size: 32),
          ),
          SizedBox(width: spacings.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('LIA JOB HUNTER', style: typography.caption.copyWith(color: colors.accentPrimary, letterSpacing: 2.2, fontWeight: FontWeight.w700)),
                SizedBox(height: spacings.xs),
                Text('Vacantes', style: typography.h1.copyWith(color: colors.textPrimary)),
                SizedBox(height: spacings.xs),
                Text('Encuentra oportunidades compatibles con tu perfil y deja que LIA priorice dónde vale la pena aplicar.', style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
              ],
            ),
          ),
          SizedBox(width: spacings.lg),
          _HeroMetric(value: '${_vacancies.length}', label: 'Oportunidades', color: colors.accentSecondary),
          SizedBox(width: spacings.md),
          _HeroMetric(value: '94%', label: 'Mejor match', color: colors.accentPrimary),
        ],
      ),
    );
  }

  Widget _buildSearchBar(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Container(
      decoration: BoxDecoration(color: colors.surface, borderRadius: BorderRadius.circular(16), border: Border.all(color: colors.border)),
      padding: EdgeInsets.symmetric(horizontal: spacings.md, vertical: 4),
      child: Row(
        children: [
          Icon(Icons.search_rounded, color: colors.textMuted),
          SizedBox(width: spacings.sm),
          Expanded(
            child: TextField(
              controller: _searchController,
              onChanged: (value) => setState(() => _query = value),
              style: typography.bodyMedium.copyWith(color: colors.textPrimary),
              decoration: InputDecoration(
                hintText: 'Busca por puesto, tecnología o empresa…',
                hintStyle: typography.bodyMedium.copyWith(color: colors.textMuted),
                border: InputBorder.none,
              ),
            ),
          ),
          if (_query.isNotEmpty)
            IconButton(
              onPressed: () {
                _searchController.clear();
                setState(() => _query = '');
              },
              icon: Icon(Icons.close_rounded, color: colors.textMuted),
              tooltip: 'Limpiar búsqueda',
            ),
        ],
      ),
    );
  }

  Widget _buildFilters(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    return Wrap(
      spacing: spacings.sm,
      runSpacing: spacings.sm,
      children: [
        _FilterDropdown(icon: Icons.public_rounded, label: 'Ubicación', value: _location, items: const ['Todas', 'México', 'USA'], onChanged: (value) => setState(() => _location = value)),
        _FilterDropdown(icon: Icons.laptop_mac_rounded, label: 'Modalidad', value: _mode, items: const ['Todas', 'Remoto', 'Híbrido'], onChanged: (value) => setState(() => _mode = value)),
        _FilterDropdown(icon: Icons.workspace_premium_outlined, label: 'Nivel', value: _level, items: const ['Todos', 'Junior', 'Mid', 'Senior'], onChanged: (value) => setState(() => _level = value)),
        PopupMenuButton<int>(
          onSelected: (value) => setState(() => _minimumMatch = value),
          color: colors.surface,
          itemBuilder: (_) => const [
            PopupMenuItem(value: 0, child: Text('Cualquier match')),
            PopupMenuItem(value: 70, child: Text('70% o más')),
            PopupMenuItem(value: 80, child: Text('80% o más')),
            PopupMenuItem(value: 90, child: Text('90% o más')),
          ],
          child: _FilterChip(icon: Icons.auto_awesome_rounded, label: _minimumMatch == 0 ? 'Match' : '${_minimumMatch}%+ Match'),
        ),
      ],
    );
  }

  Widget _buildMatchLegend(BuildContext context) {
    final colors = context.liaColors;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.auto_awesome_rounded, size: 16, color: colors.accentPrimary),
        const SizedBox(width: 6),
        Text('Match calculado por LIA', style: context.liaTypography.caption.copyWith(color: colors.textMuted)),
      ],
    );
  }

  Widget _buildVacancyCard(BuildContext context, Vacancy vacancy) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: LiaGlassPanel(
        padding: EdgeInsets.all(spacings.lg),
        child: InkWell(
          onTap: () => setState(() => _selectedVacancy = vacancy),
          borderRadius: BorderRadius.circular(18),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _MatchBadge(match: vacancy.match),
              SizedBox(width: spacings.lg),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(child: Text(vacancy.title, style: typography.h3.copyWith(color: colors.textPrimary))),
                        if (vacancy.featured) _StatusPill(label: 'TOP MATCH', icon: Icons.star_rounded, color: colors.accentPrimary),
                      ],
                    ),
                    SizedBox(height: spacings.xs),
                    Text(vacancy.company, style: typography.bodyMedium.copyWith(color: colors.accentSecondary, fontWeight: FontWeight.w600)),
                    SizedBox(height: spacings.sm),
                    Wrap(
                      spacing: spacings.md,
                      runSpacing: spacings.xs,
                      children: [
                        _MetaItem(Icons.location_on_outlined, vacancy.location),
                        _MetaItem(Icons.laptop_mac_outlined, vacancy.mode),
                        _MetaItem(Icons.trending_up_rounded, vacancy.level),
                        _MetaItem(Icons.payments_outlined, vacancy.salary),
                      ],
                    ),
                    SizedBox(height: spacings.md),
                    Wrap(spacing: spacings.xs, runSpacing: spacings.xs, children: vacancy.skills.map((skill) => _SkillTag(label: skill)).toList()),
                  ],
                ),
              ),
              SizedBox(width: spacings.lg),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(vacancy.posted, style: typography.caption.copyWith(color: colors.textMuted)),
                  const SizedBox(height: 28),
                  OutlinedButton.icon(
                    onPressed: () => setState(() => _selectedVacancy = vacancy),
                    icon: const Icon(Icons.analytics_outlined, size: 17),
                    label: const Text('Analizar ATS'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyResults(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xxl),
      child: Column(
        children: [
          Icon(Icons.search_off_rounded, size: 52, color: colors.textMuted),
          SizedBox(height: spacings.md),
          Text('No encontramos coincidencias', style: typography.h3),
          SizedBox(height: spacings.xs),
          Text('Prueba con otro término o relaja alguno de los filtros.', style: typography.bodyMedium.copyWith(color: colors.textSecondary), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildDetailOverlay(BuildContext context, Vacancy vacancy) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Positioned.fill(
      child: Material(
        color: Colors.black.withValues(alpha: 0.72),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 760, maxHeight: 680),
            child: LiaGlassPanel(
              hasGlow: true,
              glowColor: colors.accentPrimary,
              padding: EdgeInsets.all(spacings.xl),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      _MatchBadge(match: vacancy.match, large: true),
                      SizedBox(width: spacings.md),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(vacancy.title, style: typography.h2),
                            Text(vacancy.company, style: typography.bodyMedium.copyWith(color: colors.accentSecondary)),
                          ],
                        ),
                      ),
                      IconButton(onPressed: () => setState(() => _selectedVacancy = null), icon: Icon(Icons.close_rounded, color: colors.textSecondary)),
                    ],
                  ),
                  SizedBox(height: spacings.lg),
                  const Divider(),
                  SizedBox(height: spacings.lg),
                  Text('LIA ATS PREVIEW', style: typography.caption.copyWith(color: colors.accentPrimary, letterSpacing: 1.8, fontWeight: FontWeight.w700)),
                  SizedBox(height: spacings.sm),
                  Text('Esta vacante será comparada contra tu perfil profesional para calcular compatibilidad, brechas y oportunidades de optimización.', style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
                  SizedBox(height: spacings.lg),
                  _ScoreRow(label: 'Compatibilidad general', value: vacancy.match),
                  _ScoreRow(label: 'Skills detectadas', value: 92),
                  _ScoreRow(label: 'Experiencia relevante', value: 88),
                  _ScoreRow(label: 'Keywords ATS', value: 90),
                  const Spacer(),
                  Row(
                    children: [
                      Expanded(child: OutlinedButton.icon(onPressed: () => setState(() => _selectedVacancy = null), icon: const Icon(Icons.bookmark_border_rounded), label: const Text('Guardar vacante'))),
                      SizedBox(width: spacings.md),
                      Expanded(child: FilledButton.icon(onPressed: () => setState(() => _selectedVacancy = null), icon: const Icon(Icons.analytics_rounded), label: const Text('Analizar con ATS'))),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _HeroMetric extends StatelessWidget {
  final String value;
  final String label;
  final Color color;

  const _HeroMetric({required this.value, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Container(
      width: 110,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      decoration: BoxDecoration(color: colors.surface.withValues(alpha: 0.75), borderRadius: BorderRadius.circular(14), border: Border.all(color: colors.border)),
      child: Column(children: [
        Text(value, style: context.liaTypography.h3.copyWith(color: color)),
        const SizedBox(height: 2),
        Text(label, style: context.liaTypography.caption.copyWith(color: colors.textMuted)),
      ]),
    );
  }
}

class _FilterDropdown extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final List<String> items;
  final ValueChanged<String> onChanged;

  const _FilterDropdown({required this.icon, required this.label, required this.value, required this.items, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(color: colors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: colors.border)),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          dropdownColor: colors.surface,
          icon: Icon(Icons.keyboard_arrow_down_rounded, color: colors.textMuted),
          items: items.map((item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
          onChanged: (item) { if (item != null) onChanged(item); },
          selectedItemBuilder: (_) => items.map((item) => Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 16, color: colors.accentSecondary), const SizedBox(width: 7), Text('$label: $item')])).toList(),
        ),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _FilterChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(color: colors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: colors.border)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 16, color: colors.accentPrimary), const SizedBox(width: 7), Text(label), const SizedBox(width: 5), Icon(Icons.keyboard_arrow_down_rounded, size: 17, color: colors.textMuted)]),
    );
  }
}

class _MatchBadge extends StatelessWidget {
  final int match;
  final bool large;

  const _MatchBadge({required this.match, this.large = false});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final color = match >= 90 ? colors.accentPrimary : match >= 80 ? colors.accentSecondary : colors.textSecondary;
    final size = large ? 82.0 : 70.0;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color.withValues(alpha: 0.08), border: Border.all(color: color.withValues(alpha: 0.65), width: 2), boxShadow: [BoxShadow(color: color.withValues(alpha: 0.16), blurRadius: 18)]),
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text('$match%', style: context.liaTypography.h3.copyWith(color: color)), Text('MATCH', style: context.liaTypography.caption.copyWith(color: colors.textMuted, fontSize: 9))]),
    );
  }
}

class _StatusPill extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;

  const _StatusPill({required this.label, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(20), border: Border.all(color: color.withValues(alpha: 0.35))),
      child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 13, color: color), const SizedBox(width: 5), Text(label, style: context.liaTypography.caption.copyWith(color: color, fontWeight: FontWeight.w700))]),
    );
  }
}

class _MetaItem extends StatelessWidget {
  final IconData icon;
  final String label;

  const _MetaItem(this.icon, this.label);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 15, color: colors.textMuted), const SizedBox(width: 5), Text(label, style: context.liaTypography.caption.copyWith(color: colors.textSecondary))]);
  }
}

class _SkillTag extends StatelessWidget {
  final String label;

  const _SkillTag({required this.label});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: colors.accentSecondary.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(20), border: Border.all(color: colors.accentSecondary.withValues(alpha: 0.25))),
      child: Text(label, style: context.liaTypography.caption.copyWith(color: colors.textSecondary)),
    );
  }
}

class _ScoreRow extends StatelessWidget {
  final String label;
  final int value;

  const _ScoreRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [Expanded(child: Text(label, style: context.liaTypography.bodySmall)), Text('$value%', style: context.liaTypography.bodySmall.copyWith(color: colors.accentPrimary, fontWeight: FontWeight.w700))]),
        const SizedBox(height: 7),
        ClipRRect(borderRadius: BorderRadius.circular(10), child: LinearProgressIndicator(value: value / 100, minHeight: 7, backgroundColor: colors.surfaceHover, valueColor: AlwaysStoppedAnimation(colors.accentPrimary))),
      ]),
    );
  }
}
