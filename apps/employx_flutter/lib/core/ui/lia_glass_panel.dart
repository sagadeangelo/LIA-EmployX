import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaGlassPanel extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double blurSigma;
  final double opacity;
  final BorderRadius? borderRadius;
  final bool hasGlow;
  final Color? glowColor;
  final VoidCallback? onTap;

  const LiaGlassPanel({
    Key? key,
    required this.child,
    this.padding,
    this.blurSigma = 10.0,
    this.opacity = 0.7,
    this.borderRadius,
    this.hasGlow = false,
    this.glowColor,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    
    final radius = borderRadius ?? spacings.radiusLg;
    final baseColor = glowColor ?? colors.accentPrimary;

    Widget content = Container(
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: opacity),
        borderRadius: radius,
        border: Border.all(
          color: hasGlow ? baseColor.withValues(alpha: 0.5) : colors.border,
          width: 1,
        ),
        boxShadow: hasGlow
            ? [
                BoxShadow(
                  color: baseColor.withValues(alpha: 0.15),
                  blurRadius: 20,
                  spreadRadius: 2,
                )
              ]
            : [],
      ),
      child: ClipRRect(
        borderRadius: radius,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: Padding(
            padding: padding ?? EdgeInsets.all(spacings.lg),
            child: child,
          ),
        ),
      ),
    );

    if (onTap != null) {
      return MouseRegion(
        cursor: SystemMouseCursors.click,
        child: GestureDetector(
          onTap: onTap,
          child: content,
        ),
      );
    }

    return content;
  }
}
