import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Define el sistema tipográfico premium para LIA EmployX.
/// Utiliza Google Fonts (preferiblemente Inter) para un look limpio y moderno.
class LiaTypography extends ThemeExtension<LiaTypography> {
  // ---------------------------------------------------------------------------
  // Headings
  // ---------------------------------------------------------------------------
  final TextStyle display;
  final TextStyle h1;
  final TextStyle h2;
  final TextStyle h3;

  // ---------------------------------------------------------------------------
  // Body & UI
  // ---------------------------------------------------------------------------
  final TextStyle bodyLarge;
  final TextStyle bodyMedium;
  final TextStyle bodySmall;
  final TextStyle caption;
  final TextStyle button;

  const LiaTypography({
    required this.display,
    required this.h1,
    required this.h2,
    required this.h3,
    required this.bodyLarge,
    required this.bodyMedium,
    required this.bodySmall,
    required this.caption,
    required this.button,
  });

  /// Instancia predeterminada usando Inter o fuente similar sans-serif moderna.
  static LiaTypography get modern {
    // Aquí puedes cambiar a GoogleFonts.geist() si prefieres Geist,
    // o cualquier otra fuente premium sans-serif.
    final baseFont = GoogleFonts.inter();

    return LiaTypography(
      display: baseFont.copyWith(
        fontSize: 48,
        fontWeight: FontWeight.w700,
        letterSpacing: -1.5,
        height: 1.1,
      ),
      h1: baseFont.copyWith(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        letterSpacing: -1.0,
        height: 1.2,
      ),
      h2: baseFont.copyWith(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.5,
        height: 1.3,
      ),
      h3: baseFont.copyWith(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.2,
        height: 1.4,
      ),
      bodyLarge: baseFont.copyWith(
        fontSize: 18,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.5,
      ),
      bodyMedium: baseFont.copyWith(
        fontSize: 15,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.1,
        height: 1.5,
      ),
      bodySmall: baseFont.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.1,
        height: 1.5,
      ),
      caption: baseFont.copyWith(
        fontSize: 13,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.2,
        height: 1.4,
      ),
      button: baseFont.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.2,
        height: 1.0,
      ),
    );
  }

  @override
  ThemeExtension<LiaTypography> copyWith({
    TextStyle? display,
    TextStyle? h1,
    TextStyle? h2,
    TextStyle? h3,
    TextStyle? bodyLarge,
    TextStyle? bodyMedium,
    TextStyle? bodySmall,
    TextStyle? caption,
    TextStyle? button,
  }) {
    return LiaTypography(
      display: display ?? this.display,
      h1: h1 ?? this.h1,
      h2: h2 ?? this.h2,
      h3: h3 ?? this.h3,
      bodyLarge: bodyLarge ?? this.bodyLarge,
      bodyMedium: bodyMedium ?? this.bodyMedium,
      bodySmall: bodySmall ?? this.bodySmall,
      caption: caption ?? this.caption,
      button: button ?? this.button,
    );
  }

  @override
  ThemeExtension<LiaTypography> lerp(
    covariant ThemeExtension<LiaTypography>? other,
    double t,
  ) {
    if (other is! LiaTypography) return this;
    return LiaTypography(
      display: TextStyle.lerp(display, other.display, t)!,
      h1: TextStyle.lerp(h1, other.h1, t)!,
      h2: TextStyle.lerp(h2, other.h2, t)!,
      h3: TextStyle.lerp(h3, other.h3, t)!,
      bodyLarge: TextStyle.lerp(bodyLarge, other.bodyLarge, t)!,
      bodyMedium: TextStyle.lerp(bodyMedium, other.bodyMedium, t)!,
      bodySmall: TextStyle.lerp(bodySmall, other.bodySmall, t)!,
      caption: TextStyle.lerp(caption, other.caption, t)!,
      button: TextStyle.lerp(button, other.button, t)!,
    );
  }
}
