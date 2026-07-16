import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_button.dart';
import '../../../core/ui/lia_chip.dart';

class AiAssistantScreen extends StatelessWidget {
  const AiAssistantScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Spacer(),
              
              // Greeting
              Text(
                '👋 Buenas noches, Miguel',
                style: typography.h1.copyWith(color: colors.textPrimary),
              ),
              SizedBox(height: spacings.sm),
              Text(
                '¿Qué quieres hacer hoy?',
                style: typography.h3.copyWith(color: colors.textSecondary, fontWeight: FontWeight.w400),
              ),
              SizedBox(height: spacings.xl),

              // Suggestions
              Wrap(
                spacing: spacings.sm,
                runSpacing: spacings.sm,
                alignment: WrapAlignment.center,
                children: [
                  LiaChip(
                    label: 'Analizar mi CV',
                    icon: Icons.document_scanner_outlined,
                    onTap: () {},
                  ),
                  LiaChip(
                    label: 'Buscar vacantes',
                    icon: Icons.work_outline,
                    onTap: () {},
                  ),
                  LiaChip(
                    label: 'Preparar entrevista',
                    icon: Icons.mic_none,
                    onTap: () {},
                  ),
                  LiaChip(
                    label: 'Mejorar mi perfil',
                    icon: Icons.star_border,
                    onTap: () {},
                  ),
                ],
              ),
              
              Spacer(),

              // Chat Input Area
              Container(
                margin: EdgeInsets.only(bottom: spacings.xxl),
                padding: EdgeInsets.symmetric(horizontal: spacings.lg),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Chat IA',
                      style: typography.caption.copyWith(
                        color: colors.textMuted,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1,
                      ),
                    ),
                    SizedBox(height: spacings.xs),
                    Container(
                      padding: EdgeInsets.all(spacings.xs),
                      decoration: BoxDecoration(
                        color: colors.surface,
                        borderRadius: spacings.radiusMd,
                        border: Border.all(color: colors.border),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 5),
                          )
                        ]
                      ),
                      child: Row(
                        children: [
                          IconButton(
                            icon: Icon(Icons.attach_file, color: colors.textSecondary),
                            onPressed: () {},
                          ),
                          Expanded(
                            child: TextField(
                              style: typography.bodyMedium.copyWith(color: colors.textPrimary),
                              cursorColor: colors.accentPrimary,
                              decoration: InputDecoration(
                                hintText: 'Sube tu CV o hazme una pregunta...',
                                hintStyle: typography.bodyMedium.copyWith(color: colors.textMuted),
                                border: InputBorder.none,
                                isDense: true,
                              ),
                            ),
                          ),
                          LiaButton(
                            text: 'Enviar',
                            variant: LiaButtonVariant.primary,
                            icon: Icons.send_rounded,
                            onPressed: () {},
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
