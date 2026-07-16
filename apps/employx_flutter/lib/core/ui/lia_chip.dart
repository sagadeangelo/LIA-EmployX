import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

enum LiaChipVariant {
  neutral,
  primary,
  success,
  warning,
  error,
}

class LiaChip extends StatelessWidget {
  final String label;
  final LiaChipVariant variant;
  final IconData? icon;
  final VoidCallback? onDeleted;
  final VoidCallback? onTap;

  const LiaChip({
    Key? key,
    required this.label,
    this.variant = LiaChipVariant.neutral,
    this.icon,
    this.onDeleted,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    Color backgroundColor;
    Color foregroundColor;

    switch (variant) {
      case LiaChipVariant.neutral:
        backgroundColor = colors.surfaceHover;
        foregroundColor = colors.textPrimary;
        break;
      case LiaChipVariant.primary:
        backgroundColor = colors.accentPrimary.withOpacity(0.15);
        foregroundColor = colors.accentPrimary;
        break;
      case LiaChipVariant.success:
        backgroundColor = Colors.green.withOpacity(0.15);
        foregroundColor = Colors.greenAccent;
        break;
      case LiaChipVariant.warning:
        backgroundColor = Colors.orange.withOpacity(0.15);
        foregroundColor = Colors.orangeAccent;
        break;
      case LiaChipVariant.error:
        backgroundColor = colors.error.withOpacity(0.15);
        foregroundColor = colors.error;
        break;
    }

    Widget content = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (icon != null) ...[
          Icon(icon, size: 14, color: foregroundColor),
          SizedBox(width: spacings.xxs),
        ],
        Text(
          label,
          style: typography.caption.copyWith(
            color: foregroundColor,
            fontWeight: FontWeight.w500,
          ),
        ),
        if (onDeleted != null) ...[
          SizedBox(width: spacings.xxs),
          GestureDetector(
            onTap: onDeleted,
            child: Icon(Icons.close, size: 14, color: foregroundColor),
          ),
        ],
      ],
    );

    return MouseRegion(
      cursor: onTap != null ? SystemMouseCursors.click : SystemMouseCursors.basic,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: EdgeInsets.symmetric(
            horizontal: spacings.sm,
            vertical: spacings.xxs,
          ),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: spacings.radiusMax, // Forma de pildora
            border: Border.all(
              color: foregroundColor.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: content,
        ),
      ),
    );
  }
}
