import 'package:flutter/material.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileEducationCertificationsWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileEducationCertificationsWidget({Key? key, required this.profile}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final education = profile.education;
    final certifications = profile.certifications;
    final languages = profile.languages;

    if (education.isEmpty && certifications.isEmpty && languages.isEmpty) {
      return const SizedBox.shrink();
    }

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.school_outlined, color: colors.accentPrimary, size: 24),
              SizedBox(width: spacings.sm),
              Text('Educación y Más', style: typography.h3.copyWith(color: colors.textPrimary)),
            ],
          ),
          SizedBox(height: spacings.lg),

          if (education.isNotEmpty) ...[
            _buildSectionTitle(context, 'Educación', Icons.book_outlined),
            SizedBox(height: spacings.sm),
            ...education.map((edu) => _buildEducationItem(context, edu)).toList(),
            SizedBox(height: spacings.lg),
          ],

          if (certifications.isNotEmpty) ...[
            _buildSectionTitle(context, 'Certificaciones', Icons.workspace_premium_outlined),
            SizedBox(height: spacings.sm),
            ...certifications.map((cert) => _buildCertificationItem(context, cert)).toList(),
            SizedBox(height: spacings.lg),
          ],

          if (languages.isNotEmpty) ...[
            _buildSectionTitle(context, 'Idiomas', Icons.language_outlined),
            SizedBox(height: spacings.sm),
            Wrap(
              spacing: spacings.md,
              runSpacing: spacings.sm,
              children: languages.map((lang) => _buildLanguageItem(context, lang)).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title, IconData icon) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Row(
      children: [
        Icon(icon, size: 16, color: colors.textMuted),
        const SizedBox(width: 6),
        Text(title, style: typography.caption.copyWith(color: colors.textSecondary)),
      ],
    );
  }

  Widget _buildEducationItem(BuildContext context, Education edu) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(edu.degree.isNotEmpty ? edu.degree : 'Sin título', style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: 2),
          Text('${edu.institution.isNotEmpty ? edu.institution : "Institución no disponible"} • ${edu.period.isNotEmpty ? edu.period : "Fecha no disponible"}', style: typography.caption.copyWith(color: colors.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildCertificationItem(BuildContext context, Certification cert) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(cert.name.isNotEmpty ? cert.name : 'Certificación sin nombre', style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: 2),
          Text('${cert.provider.isNotEmpty ? cert.provider : "Emisor no disponible"} • ${cert.date.isNotEmpty ? cert.date : "Fecha no disponible"}', style: typography.caption.copyWith(color: colors.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildLanguageItem(BuildContext context, Language lang) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: colors.surfaceHover,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(lang.language.isNotEmpty ? lang.language : 'Idioma', style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.w500)),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: colors.accentPrimary.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              lang.level.isNotEmpty ? lang.level : 'No especificado',
              style: typography.caption.copyWith(color: colors.accentPrimary, fontSize: 10, fontWeight: FontWeight.bold),
            ),
          )
        ],
      ),
    );
  }
}
