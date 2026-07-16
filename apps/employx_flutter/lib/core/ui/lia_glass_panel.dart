import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaGlassPanel extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double blurSigma;
  final double opacity;
  final BorderRadius? borderRadius;

  const LiaGlassPanel({
    Key? key,
    required this.child,
    this.padding,
    this.blurSigma = 10.0,
    this.opacity = 0.7,
    this.borderRadius,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    
    final radius = borderRadius ?? spacings.radiusLg;

    return ClipRRect(
      borderRadius: radius,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
        child: Container(
          padding: padding ?? EdgeInsets.all(spacings.lg),
          decoration: BoxDecoration(
            color: colors.surface.withOpacity(opacity),
            borderRadius: radius,
            border: Border.all(
              color: Colors.white.withOpacity(0.05),
              width: 1,
            ),
          ),
          child: child,
        ),
      ),
    );
  }
}
