import 'package:flutter/material.dart';

import '../../../core/models/professional_profile_model.dart';
import '../services/ats_analyzer.dart';

/// Panel visual de inteligencia ATS para LIA-EmployX.
///
/// Esta pieza es independiente del ProfessionalProfileScreen.
/// Recibe un ProfessionalProfile y permite analizar una vacante
/// directamente desde el panel.
///
/// ATS 1B:
/// - Entrada de descripción de vacante.
/// - Ejecución del ATSAnalyzer.
/// - Score general.
/// - Desglose de compatibilidad.
/// - Keywords encontradas.
/// - Keywords faltantes.
/// - Recomendaciones de LIA.
class ATSAnalyzerPanel extends StatefulWidget {
  final ProfessionalProfile profile;

  const ATSAnalyzerPanel({
    super.key,
    required this.profile,
  });

  @override
  State<ATSAnalyzerPanel> createState() => _ATSAnalyzerPanelState();
}

class _ATSAnalyzerPanelState extends State<ATSAnalyzerPanel> {
  final TextEditingController _jobController =
      TextEditingController();

  final ATSAnalyzer _analyzer = const ATSAnalyzer();

  ATSAnalysisResult? _result;
  bool _isAnalyzing = false;

  @override
  void dispose() {
    _jobController.dispose();
    super.dispose();
  }

  void _analyze() {
    final jobDescription = _jobController.text.trim();

    if (jobDescription.isEmpty) {
      setState(() {
        _result = null;
      });
      return;
    }

    setState(() {
      _isAnalyzing = true;
    });

    // El análisis actual es local y determinista.
    final result = _analyzer.analyze(
      profile: widget.profile,
      jobDescription: jobDescription,
    );

    setState(() {
      _result = result;
      _isAnalyzing = false;
    });
  }

  void _clear() {
    _jobController.clear();

    setState(() {
      _result = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: theme.colorScheme.outline.withValues(
            alpha: 0.35,
          ),
        ),
        boxShadow: [
          BoxShadow(
            blurRadius: 24,
            offset: const Offset(0, 10),
            color: Colors.black.withValues(
              alpha: 0.10,
            ),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(context),
            const SizedBox(height: 24),
            _buildJobInput(context),
            const SizedBox(height: 20),
            _buildActionRow(context),
            if (_result != null) ...[
              const SizedBox(height: 28),
              _buildAnalysis(context, _result!),
            ],
          ],
        ),
      ),
    );
  }

  // ===========================================================================
  // HEADER
  // ===========================================================================

  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            gradient: LinearGradient(
              colors: [
                theme.colorScheme.primary,
                theme.colorScheme.secondary,
              ],
            ),
          ),
          child: const Icon(
            Icons.auto_awesome,
            color: Colors.white,
            size: 24,
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'ATS Intelligence',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.2,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Descubre qué tan compatible es tu perfil con una vacante.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(
                    alpha: 0.65,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ===========================================================================
  // JOB INPUT
  // ===========================================================================

  Widget _buildJobInput(BuildContext context) {
    final theme = Theme.of(context);

    return TextField(
      controller: _jobController,
      minLines: 6,
      maxLines: 12,
      textInputAction: TextInputAction.newline,
      decoration: InputDecoration(
        labelText: 'Descripción de la vacante',
        hintText:
            'Pega aquí la descripción completa de la vacante...\n\n'
            'Ejemplo:\n'
            'Full Stack Developer\n'
            'Python, Flutter, REST APIs, SQL...\n'
            '3+ years of experience...',
        alignLabelWithHint: true,
        prefixIcon: const Padding(
          padding: EdgeInsets.only(
            left: 14,
            right: 10,
            top: 16,
          ),
          child: Icon(
            Icons.work_outline,
          ),
        ),
        prefixIconConstraints: const BoxConstraints(
          minWidth: 48,
        ),
        filled: true,
        fillColor: theme.colorScheme.surfaceContainerHighest
            .withValues(alpha: 0.35),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: theme.colorScheme.outline.withValues(
              alpha: 0.25,
            ),
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: theme.colorScheme.outline.withValues(
              alpha: 0.25,
            ),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: theme.colorScheme.primary,
            width: 1.5,
          ),
        ),
      ),
    );
  }

  // ===========================================================================
  // ACTIONS
  // ===========================================================================

  Widget _buildActionRow(BuildContext context) {
    return Row(
      children: [
        FilledButton.icon(
          onPressed: _isAnalyzing ? null : _analyze,
          icon: _isAnalyzing
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : const Icon(
                  Icons.analytics_outlined,
                ),
          label: Text(
            _isAnalyzing
                ? 'Analizando...'
                : 'Analizar compatibilidad',
          ),
        ),
        const SizedBox(width: 10),
        if (_jobController.text.isNotEmpty)
          OutlinedButton.icon(
            onPressed: _isAnalyzing ? null : _clear,
            icon: const Icon(
              Icons.refresh,
              size: 18,
            ),
            label: const Text('Limpiar'),
          ),
      ],
    );
  }

  // ===========================================================================
  // ANALYSIS
  // ===========================================================================

  Widget _buildAnalysis(
    BuildContext context,
    ATSAnalysisResult result,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildScoreSection(
          context,
          result,
        ),
        const SizedBox(height: 24),
        _buildMetricGrid(
          context,
          result,
        ),
        const SizedBox(height: 24),
        _buildKeywordsSection(
          context,
          result,
        ),
        const SizedBox(height: 24),
        _buildRecommendations(
          context,
          result,
        ),
      ],
    );
  }

  // ===========================================================================
  // SCORE
  // ===========================================================================

  Widget _buildScoreSection(
    BuildContext context,
    ATSAnalysisResult result,
  ) {
    final theme = Theme.of(context);

    final scoreColor = _scoreColor(
      context,
      result.score,
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            scoreColor.withValues(alpha: 0.16),
            theme.colorScheme.surface,
          ],
        ),
        border: Border.all(
          color: scoreColor.withValues(
            alpha: 0.35,
          ),
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 116,
            height: 116,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 116,
                  height: 116,
                  child: CircularProgressIndicator(
                    value: result.score / 100,
                    strokeWidth: 9,
                    backgroundColor: theme
                        .colorScheme
                        .outline
                        .withValues(alpha: 0.12),
                    valueColor: AlwaysStoppedAnimation<Color>(
                      scoreColor,
                    ),
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '${result.score}',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: scoreColor,
                      ),
                    ),
                    Text(
                      '/100',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface
                            .withValues(alpha: 0.55),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ATS Match',
                  style: theme.textTheme.labelLarge?.copyWith(
                    color: theme.colorScheme.onSurface
                        .withValues(alpha: 0.55),
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  result.compatibility,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: scoreColor,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _scoreDescription(result.score),
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface
                        .withValues(alpha: 0.68),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // METRICS
  // ===========================================================================

  Widget _buildMetricGrid(
    BuildContext context,
    ATSAnalysisResult result,
  ) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = constraints.maxWidth >= 900 ? 5 : 2;

        final metrics = [
          _ATSMetric(
            label: 'Keywords',
            value: result.keywordMatch,
            icon: Icons.key,
          ),
          _ATSMetric(
            label: 'Skills',
            value: result.skillsMatch,
            icon: Icons.code,
          ),
          _ATSMetric(
            label: 'Role',
            value: result.roleMatch,
            icon: Icons.badge_outlined,
          ),
          _ATSMetric(
            label: 'Experiencia',
            value: result.experienceMatch,
            icon: Icons.timeline,
          ),
          _ATSMetric(
            label: 'Educación',
            value: result.educationMatch,
            icon: Icons.school_outlined,
          ),
        ];

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: metrics.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.7,
          ),
          itemBuilder: (context, index) {
            return _buildMetricCard(
              context,
              metrics[index],
            );
          },
        );
      },
    );
  }

  Widget _buildMetricCard(
    BuildContext context,
    _ATSMetric metric,
  ) {
    final theme = Theme.of(context);
    final color = _scoreColor(
      context,
      metric.value,
    );

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest
            .withValues(alpha: 0.28),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.outline.withValues(
            alpha: 0.18,
          ),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              metric.icon,
              size: 19,
              color: color,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  metric.label,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: theme.colorScheme.onSurface
                        .withValues(alpha: 0.55),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${metric.value}%',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // KEYWORDS
  // ===========================================================================

  Widget _buildKeywordsSection(
    BuildContext context,
    ATSAnalysisResult result,
  ) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 720) {
          return Column(
            children: [
              _buildKeywordCard(
                context,
                title: 'Coincidencias',
                icon: Icons.check_circle_outline,
                keywords: result.matchedKeywords,
                positive: true,
              ),
              const SizedBox(height: 12),
              _buildKeywordCard(
                context,
                title: 'Brechas',
                icon: Icons.warning_amber_outlined,
                keywords: result.missingKeywords,
                positive: false,
              ),
            ],
          );
        }

        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _buildKeywordCard(
                context,
                title: 'Coincidencias',
                icon: Icons.check_circle_outline,
                keywords: result.matchedKeywords,
                positive: true,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildKeywordCard(
                context,
                title: 'Brechas',
                icon: Icons.warning_amber_outlined,
                keywords: result.missingKeywords,
                positive: false,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildKeywordCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<String> keywords,
    required bool positive,
  }) {
    final theme = Theme.of(context);

    final color = positive
        ? Colors.green
        : Colors.orange;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest
            .withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withValues(alpha: 0.22),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: color,
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Spacer(),
              Text(
                '${keywords.length}',
                style: theme.textTheme.labelLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          if (keywords.isEmpty)
            Text(
              positive
                  ? 'No se detectaron coincidencias.'
                  : 'No se detectaron brechas.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface
                    .withValues(alpha: 0.55),
              ),
            )
          else
            Wrap(
              spacing: 7,
              runSpacing: 7,
              children: keywords
                  .take(15)
                  .map(
                    (keyword) => _buildKeywordChip(
                      context,
                      keyword,
                      color,
                    ),
                  )
                  .toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildKeywordChip(
    BuildContext context,
    String keyword,
    Color color,
  ) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 10,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: color.withValues(alpha: 0.20),
        ),
      ),
      child: Text(
        keyword,
        style: theme.textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  // ===========================================================================
  // RECOMMENDATIONS
  // ===========================================================================

  Widget _buildRecommendations(
    BuildContext context,
    ATSAnalysisResult result,
  ) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primary.withValues(alpha: 0.10),
            theme.colorScheme.secondary.withValues(alpha: 0.05),
          ],
        ),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(
            alpha: 0.18,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.auto_awesome,
                color: theme.colorScheme.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Recomendaciones de LIA',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          ...result.recommendations.map(
            (recommendation) => Padding(
              padding: const EdgeInsets.only(
                bottom: 10,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    margin: const EdgeInsets.only(
                      top: 7,
                    ),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      recommendation,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ===========================================================================
  // HELPERS
  // ===========================================================================

  Color _scoreColor(
    BuildContext context,
    int score,
  ) {
    if (score >= 85) {
      return Colors.green;
    }

    if (score >= 70) {
      return Colors.lightGreen;
    }

    if (score >= 55) {
      return Colors.orange;
    }

    return Colors.redAccent;
  }

  String _scoreDescription(int score) {
    if (score >= 85) {
      return 'Tu perfil presenta una excelente alineación con esta vacante.';
    }

    if (score >= 70) {
      return 'Tu perfil presenta una buena alineación con esta vacante.';
    }

    if (score >= 55) {
      return 'Existe una compatibilidad moderada. Hay áreas que LIA puede ayudarte a mejorar.';
    }

    if (score >= 40) {
      return 'La compatibilidad es baja. Conviene revisar las principales brechas.';
    }

    return 'La vacante presenta una baja coincidencia con el perfil actual.';
  }
}

// =============================================================================
// METRIC MODEL
// =============================================================================

class _ATSMetric {
  final String label;
  final int value;
  final IconData icon;

  const _ATSMetric({
    required this.label,
    required this.value,
    required this.icon,
  });
}