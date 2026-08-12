import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';
import 'lia_glass_panel.dart';

class LiaMetric extends StatelessWidget {
  final String title;
  final String? value;
  final IconData? icon;
  final Color? color;
  final String emptyText;

  const LiaMetric({
    Key? key,
    required this.title,
    this.value,
    this.icon,
    this.color,
    this.emptyText = 'Sin datos',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final activeColor = color ?? colors.accentPrimary;
    final hasData = value != null && value!.isNotEmpty;

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(icon, size: 16, color: hasData ? activeColor : colors.textMuted),
                SizedBox(width: spacings.xs),
              ],
              Expanded(
                child: Text(
                  title,
                  style: typography.caption.copyWith(
                    color: colors.textSecondary,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          SizedBox(height: spacings.sm),
          Text(
            hasData ? value! : emptyText,
            style: typography.h2.copyWith(
              color: hasData ? colors.textPrimary : colors.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
