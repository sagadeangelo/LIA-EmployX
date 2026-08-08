import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaProgressBar extends StatelessWidget {
  final double progress; // 0.0 to 1.0
  final Color? color;
  final String? label;
  final String? trailingText;
  final double height;

  const LiaProgressBar({
    Key? key,
    required this.progress,
    this.color,
    this.label,
    this.trailingText,
    this.height = 6.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final activeColor = color ?? colors.accentPrimary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null || trailingText != null) ...[
          Row(
            children: [
              if (label != null)
                Expanded(
                  child: Text(
                    label!,
                    style: typography.caption.copyWith(color: colors.textSecondary),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              if (label != null && trailingText != null)
                const SizedBox(width: 4),
              if (trailingText != null)
                Text(
                  trailingText!,
                  style: typography.caption.copyWith(
                    color: activeColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
            ],
          ),
          SizedBox(height: spacings.xs),
        ],
        Container(
          height: height,
          width: double.infinity,
          decoration: BoxDecoration(
            color: colors.surfaceHover,
            borderRadius: BorderRadius.circular(height / 2),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              return Stack(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 500),
                    curve: Curves.easeOutCubic,
                    width: constraints.maxWidth * progress.clamp(0.0, 1.0),
                    height: height,
                    decoration: BoxDecoration(
                      color: activeColor,
                      borderRadius: BorderRadius.circular(height / 2),
                      boxShadow: [
                        BoxShadow(
                          color: activeColor.withValues(alpha: 0.5),
                          blurRadius: 10,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }
}
