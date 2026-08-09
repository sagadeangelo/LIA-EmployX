import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileEducationCertificationsWidget
    extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileEducationCertificationsWidget({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final education = profile.education;
    final certifications =
        profile.certifications;
    final languages = profile.languages;

    if (education.isEmpty &&
        certifications.isEmpty &&
        languages.isEmpty) {
      return const SizedBox.shrink();
    }

    return LiaGlassPanel(
      padding: EdgeInsets.all(
        spacings.xl,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.school_outlined,
                color: colors.accentPrimary,
                size: 24,
              ),
              SizedBox(
                width: spacings.sm,
              ),
              Text(
                'Educación y Más',
                style: typography.h3.copyWith(
                  color: colors.textPrimary,
                ),
              ),
            ],
          ),

          SizedBox(
            height: spacings.lg,
          ),

          if (education.isNotEmpty) ...[
            _buildSectionTitle(
              context,
              'Educación',
              Icons.book_outlined,
            ),

            SizedBox(
              height: spacings.sm,
            ),

            for (final edu in education)
              _buildEducationItem(
                context,
                edu,
              ),

            SizedBox(
              height: spacings.lg,
            ),
          ],

          if (certifications.isNotEmpty) ...[
            _buildSectionTitle(
              context,
              'Certificaciones',
              Icons.workspace_premium_outlined,
            ),

            SizedBox(
              height: spacings.sm,
            ),

            for (final certification
                in certifications)
              _buildCertificationItem(
                context,
                certification,
              ),

            SizedBox(
              height: spacings.lg,
            ),
          ],

          if (languages.isNotEmpty) ...[
            _buildSectionTitle(
              context,
              'Idiomas',
              Icons.language_outlined,
            ),

            SizedBox(
              height: spacings.sm,
            ),

            Wrap(
              spacing: spacings.md,
              runSpacing: spacings.sm,
              children: [
                for (final language in languages)
                  _buildLanguageItem(
                    context,
                    language,
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSectionTitle(
    BuildContext context,
    String title,
    IconData icon,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: colors.textMuted,
        ),
        const SizedBox(
          width: 6,
        ),
        Text(
          title,
          style: typography.caption.copyWith(
            color: colors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildEducationItem(
    BuildContext context,
    Education education,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final degree =
        education.degree.trim().isNotEmpty
            ? education.degree.trim()
            : 'Formación académica';

    final institution =
        education.institution.trim().isNotEmpty
            ? education.institution.trim()
            : 'Institución no disponible';

    final period =
        education.period.trim().isNotEmpty
            ? education.period.trim()
            : '';

    return Padding(
      padding:
          const EdgeInsets.only(
        bottom: 12,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Text(
            degree,
            style: typography.bodyMedium.copyWith(
              color: colors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(
            height: 3,
          ),

          Text(
            period.isEmpty
                ? institution
                : '$institution • $period',
            style: typography.caption.copyWith(
              color: colors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCertificationItem(
    BuildContext context,
    Certification certification,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final name =
        certification.name.trim().isNotEmpty
            ? certification.name.trim()
            : 'Certificación';

    final provider =
        certification.provider.trim().isNotEmpty
            ? certification.provider.trim()
            : 'Emisor no disponible';

    final date =
        certification.date.trim().isNotEmpty
            ? certification.date.trim()
            : '';

    return Padding(
      padding:
          const EdgeInsets.only(
        bottom: 12,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.verified_outlined,
                size: 18,
                color: colors.accentPrimary,
              ),

              const SizedBox(
                width: 8,
              ),

              Expanded(
                child: Text(
                  name,
                  style:
                      typography.bodyMedium.copyWith(
                    color: colors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 3,
          ),

          Padding(
            padding:
                const EdgeInsets.only(
              left: 26,
            ),
            child: Text(
              date.isEmpty
                  ? provider
                  : '$provider • $date',
              style:
                  typography.caption.copyWith(
                color:
                    colors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLanguageItem(
    BuildContext context,
    Language language,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final name =
        language.language.trim().isNotEmpty
            ? language.language.trim()
            : 'Idioma';

    final level =
        language.level.trim().isNotEmpty
            ? language.level.trim()
            : 'No especificado';

    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      decoration: BoxDecoration(
        color: colors.surfaceHover,
        borderRadius:
            BorderRadius.circular(8),
        border: Border.all(
          color: colors.border,
        ),
      ),
      child: Row(
        mainAxisSize:
            MainAxisSize.min,
        children: [
          Text(
            name,
            style:
                typography.bodyMedium.copyWith(
              color: colors.textPrimary,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(
            width: 8,
          ),

          Container(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 6,
              vertical: 2,
            ),
            decoration: BoxDecoration(
              color:
                  colors.accentPrimary
                      .withValues(
                alpha: 0.2,
              ),
              borderRadius:
                  BorderRadius.circular(4),
            ),
            child: Text(
              level,
              style:
                  typography.caption.copyWith(
                color:
                    colors.accentPrimary,
                fontSize: 10,
                fontWeight:
                    FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}