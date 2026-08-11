import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../services/ats_analyzer.dart';

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
  final TextEditingController _jobController = TextEditingController();
  final ATSAnalyzer _analyzer = const ATSAnalyzer();
  ATSAnalysisResult? _result;

  @override
  void dispose() {
    _jobController.dispose();
    super.dispose();
  }

  void _analyze() {
    setState(() {
      _result = _analyzer.analyze(widget.profile, _jobController.text);
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    final result = _result;

    return Container(
      padding: EdgeInsets.all(spacings.xl),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: colors.success.withValues(alpha: 0.28)),
        boxShadow: [
          BoxShadow(
            color: colors.success.withValues(alpha: 0.07),
            blurRadius: 28,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(11),
                decoration: BoxDecoration(
                  color: colors.success.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: Icon(
                  Icons.document_scanner_outlined,
                  color: colors.success,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ATS INTELLIGENCE',
                      style: typography.caption.copyWith(
                        color: colors.success,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1.5,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      'Analizador de Vacante',
                      style: typography.h3.copyWith(
                        color: colors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
              if (result != null)
                _ScoreBadge(score: result.score),
            ],
          ),
          SizedBox(height: spacings.lg),
          Text(
            'Compara tu perfil contra una vacante específica y explica dónde existe coincidencia o brecha.',
            style: typography.bodySmall.copyWith(
              color: colors.textSecondary,
              height: 1.45,
            ),
          ),
          SizedBox(height: spacings.lg),
          TextField(
            controller: _jobController,
            minLines: 5,
            maxLines: 9,
            style: typography.bodySmall.copyWith(color: colors.textPrimary),
            decoration: InputDecoration(
              hintText: 'Pega aquí la descripción de la vacante...',
              hintStyle: typography.bodySmall.copyWith(color: colors.textMuted),
              filled: true,
              fillColor: colors.background.withValues(alpha: 0.55),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: colors.border),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: colors.border),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: colors.success),
              ),
            ),
          ),
          SizedBox(height: spacings.md),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _jobController.text.trim().isEmpty ? null : _analyze,
              icon: const Icon(Icons.bolt_outlined),
              label: const Text('ANALIZAR COMPATIBILIDAD'),
              style: FilledButton.styleFrom(
                backgroundColor: colors.success,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 15),
              ),
            ),
          ),
          if (result != null) ...[
            SizedBox(height: spacings.xl),
            _BreakdownGrid(result: result),
            SizedBox(height: spacings.xl),
            _KeywordSection(
              title: 'COINCIDENCIAS',
              items: result.matchedKeywords,
              color: colors.success,
              emptyText: 'No se detectaron coincidencias todavía.',
            ),
            SizedBox(height: spacings.lg),
            _KeywordSection(
              title: 'BRECHAS DETECTADAS',
              items: result.missingKeywords,
              color: colors.accentPrimary,
              emptyText: 'No se detectaron brechas relevantes.',
            ),
            SizedBox(height: spacings.lg),
            _Recommendations(result: result),
          ],
        ],
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  final int score;

  const _ScoreBadge({required this.score});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: colors.success.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: colors.success.withValues(alpha: 0.35)),
      ),
      child: Text(
        '$score / 100',
        style: TextStyle(
          color: colors.success,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _BreakdownGrid extends StatelessWidget {
  final ATSAnalysisResult result;

  const _BreakdownGrid({required this.result});

  @override
  Widget build(BuildContext context) {
    final items = [
      ('Keywords', result.breakdown.keywordMatch),
      ('Rol', result.breakdown.roleMatch),
      ('Skills', result.breakdown.skillsCoverage),
      ('Experiencia', result.breakdown.experienceMatch),
      ('Educación', result.breakdown.educationMatch),
    ];

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: items.map((item) {
        return _MiniScore(label: item.$1, value: item.$2);
      }).toList(),
    );
  }
}

class _MiniScore extends StatelessWidget {
  final String label;
  final int value;

  const _MiniScore({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final color = value >= 75
        ? colors.success
        : value >= 50
            ? colors.accentTertiary
            : colors.accentPrimary;

    return Container(
      width: 135,
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: colors.background.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(13),
        border: Border.all(color: colors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: colors.textMuted, fontSize: 12)),
          const SizedBox(height: 5),
          Text(
            '$value%',
            style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

class _KeywordSection extends StatelessWidget {
  final String title;
  final List<String> items;
  final Color color;
  final String emptyText;

  const _KeywordSection({
    required this.title,
    required this.items,
    required this.color,
    required this.emptyText,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: typography.caption.copyWith(
            color: color,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 9),
        if (items.isEmpty)
          Text(emptyText, style: typography.bodySmall.copyWith(color: colors.textMuted))
        else
          Wrap(
            spacing: 7,
            runSpacing: 7,
            children: items.map((item) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: color.withValues(alpha: 0.25)),
                ),
                child: Text(item, style: TextStyle(color: color, fontSize: 12)),
              );
            }).toList(),
          ),
      ],
    );
  }
}

class _Recommendations extends StatelessWidget {
  final ATSAnalysisResult result;

  const _Recommendations({required this.result});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colors.accentPrimary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: colors.accentPrimary.withValues(alpha: 0.20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'RECOMENDACIONES LIA',
            style: typography.caption.copyWith(
              color: colors.accentPrimary,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 10),
          for (final recommendation in result.recommendations)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.arrow_right, size: 17, color: colors.accentPrimary),
                  const SizedBox(width: 5),
                  Expanded(
                    child: Text(
                      recommendation,
                      style: typography.bodySmall.copyWith(color: colors.textSecondary, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
