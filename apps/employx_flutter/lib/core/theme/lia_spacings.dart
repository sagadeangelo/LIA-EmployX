import 'package:flutter/material.dart';

/// Define el sistema de espaciados y border radius premium para LIA EmployX.
class LiaSpacings extends ThemeExtension<LiaSpacings> {
  // ---------------------------------------------------------------------------
  // Spacing (Padding/Margins) - Escala base 4px
  // ---------------------------------------------------------------------------
  final double xxs; // 4px
  final double xs;  // 8px
  final double sm;  // 12px
  final double md;  // 16px
  final double lg;  // 24px
  final double xl;  // 32px
  final double xxl; // 48px
  final double xxxl; // 64px

  // ---------------------------------------------------------------------------
  // Border Radius
  // ---------------------------------------------------------------------------
  final BorderRadius radiusSm; // 8px (Inputs, Chips)
  final BorderRadius radiusMd; // 12px (Cards pequeñas, Botones)
  final BorderRadius radiusLg; // 24px (Cards principales, Modales)
  final BorderRadius radiusMax; // Pill shape

  const LiaSpacings({
    required this.xxs,
    required this.xs,
    required this.sm,
    required this.md,
    required this.lg,
    required this.xl,
    required this.xxl,
    required this.xxxl,
    required this.radiusSm,
    required this.radiusMd,
    required this.radiusLg,
    required this.radiusMax,
  });

  /// Instancia predeterminada para el Design System.
  static const LiaSpacings modern = LiaSpacings(
    xxs: 4.0,
    xs: 8.0,
    sm: 12.0,
    md: 16.0,
    lg: 24.0,
    xl: 32.0,
    xxl: 48.0,
    xxxl: 64.0,
    radiusSm: BorderRadius.all(Radius.circular(8.0)),
    radiusMd: BorderRadius.all(Radius.circular(12.0)),
    radiusLg: BorderRadius.all(Radius.circular(24.0)),
    radiusMax: BorderRadius.all(Radius.circular(999.0)),
  );

  @override
  ThemeExtension<LiaSpacings> copyWith({
    double? xxs,
    double? xs,
    double? sm,
    double? md,
    double? lg,
    double? xl,
    double? xxl,
    double? xxxl,
    BorderRadius? radiusSm,
    BorderRadius? radiusMd,
    BorderRadius? radiusLg,
    BorderRadius? radiusMax,
  }) {
    return LiaSpacings(
      xxs: xxs ?? this.xxs,
      xs: xs ?? this.xs,
      sm: sm ?? this.sm,
      md: md ?? this.md,
      lg: lg ?? this.lg,
      xl: xl ?? this.xl,
      xxl: xxl ?? this.xxl,
      xxxl: xxxl ?? this.xxxl,
      radiusSm: radiusSm ?? this.radiusSm,
      radiusMd: radiusMd ?? this.radiusMd,
      radiusLg: radiusLg ?? this.radiusLg,
      radiusMax: radiusMax ?? this.radiusMax,
    );
  }

  @override
  ThemeExtension<LiaSpacings> lerp(
    covariant ThemeExtension<LiaSpacings>? other,
    double t,
  ) {
    if (other is! LiaSpacings) return this;
    return LiaSpacings(
      xxs: (xxs + (other.xxs - xxs) * t),
      xs: (xs + (other.xs - xs) * t),
      sm: (sm + (other.sm - sm) * t),
      md: (md + (other.md - md) * t),
      lg: (lg + (other.lg - lg) * t),
      xl: (xl + (other.xl - xl) * t),
      xxl: (xxl + (other.xxl - xxl) * t),
      xxxl: (xxxl + (other.xxxl - xxxl) * t),
      radiusSm: BorderRadius.lerp(radiusSm, other.radiusSm, t)!,
      radiusMd: BorderRadius.lerp(radiusMd, other.radiusMd, t)!,
      radiusLg: BorderRadius.lerp(radiusLg, other.radiusLg, t)!,
      radiusMax: BorderRadius.lerp(radiusMax, other.radiusMax, t)!,
    );
  }
}
