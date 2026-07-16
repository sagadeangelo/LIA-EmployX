import 'package:flutter/material.dart';

/// Define la paleta de colores premium y minimalista para LIA EmployX.
/// Inspirado en interfaces modernas como Linear y Raycast.
class LiaColors extends ThemeExtension<LiaColors> {
  // ---------------------------------------------------------------------------
  // Backgrounds & Surfaces
  // ---------------------------------------------------------------------------
  
  /// Fondo principal de la app (casi negro profundo)
  final Color background;
  
  /// Fondo para tarjetas, modales y paneles principales
  final Color surface;
  
  /// Fondo para elementos elevados o estados hover
  final Color surfaceHover;
  
  // ---------------------------------------------------------------------------
  // Text & Icons
  // ---------------------------------------------------------------------------
  
  /// Texto principal de alto contraste (blanco puro o casi puro)
  final Color textPrimary;
  
  /// Texto secundario para descripciones o metadata (Gris/Zinc)
  final Color textSecondary;
  
  /// Texto sutil para placeholders o elementos desactivados
  final Color textMuted;

  // ---------------------------------------------------------------------------
  // Borders & Dividers
  // ---------------------------------------------------------------------------
  
  /// Color sutil para líneas divisorias y bordes de tarjetas
  final Color border;
  
  /// Borde más marcado para estados de focus
  final Color borderFocus;

  // ---------------------------------------------------------------------------
  // Accents & Brand (AI)
  // ---------------------------------------------------------------------------
  
  /// Color primario de acento (ej. Violeta)
  final Color accentPrimary;
  
  /// Color secundario de acento (ej. Azul)
  final Color accentSecondary;
  
  /// Color para acciones destructivas o errores
  final Color error;

  const LiaColors({
    required this.background,
    required this.surface,
    required this.surfaceHover,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.border,
    required this.borderFocus,
    required this.accentPrimary,
    required this.accentSecondary,
    required this.error,
  });

  /// Instancia predeterminada para el Modo Oscuro (Dark Mode).
  /// Esta es la estética principal de la plataforma.
  static const LiaColors dark = LiaColors(
    background: Color(0xFF0A0A0A), // Neutral 900+
    surface: Color(0xFF171717),    // Neutral 900
    surfaceHover: Color(0xFF262626), // Neutral 800
    textPrimary: Color(0xFFFAFAFA),  // Neutral 50
    textSecondary: Color(0xFFA1A1AA),// Zinc 400
    textMuted: Color(0xFF52525B),    // Zinc 600
    border: Color(0xFF333333),       // Neutral 800 (sutil)
    borderFocus: Color(0xFF52525B),
    accentPrimary: Color(0xFF8B5CF6), // Violeta vibrante
    accentSecondary: Color(0xFF3B82F6), // Azul vibrante
    error: Color(0xFFEF4444),
  );

  @override
  ThemeExtension<LiaColors> copyWith({
    Color? background,
    Color? surface,
    Color? surfaceHover,
    Color? textPrimary,
    Color? textSecondary,
    Color? textMuted,
    Color? border,
    Color? borderFocus,
    Color? accentPrimary,
    Color? accentSecondary,
    Color? error,
  }) {
    return LiaColors(
      background: background ?? this.background,
      surface: surface ?? this.surface,
      surfaceHover: surfaceHover ?? this.surfaceHover,
      textPrimary: textPrimary ?? this.textPrimary,
      textSecondary: textSecondary ?? this.textSecondary,
      textMuted: textMuted ?? this.textMuted,
      border: border ?? this.border,
      borderFocus: borderFocus ?? this.borderFocus,
      accentPrimary: accentPrimary ?? this.accentPrimary,
      accentSecondary: accentSecondary ?? this.accentSecondary,
      error: error ?? this.error,
    );
  }

  @override
  ThemeExtension<LiaColors> lerp(
    covariant ThemeExtension<LiaColors>? other,
    double t,
  ) {
    if (other is! LiaColors) return this;
    return LiaColors(
      background: Color.lerp(background, other.background, t)!,
      surface: Color.lerp(surface, other.surface, t)!,
      surfaceHover: Color.lerp(surfaceHover, other.surfaceHover, t)!,
      textPrimary: Color.lerp(textPrimary, other.textPrimary, t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
      textMuted: Color.lerp(textMuted, other.textMuted, t)!,
      border: Color.lerp(border, other.border, t)!,
      borderFocus: Color.lerp(borderFocus, other.borderFocus, t)!,
      accentPrimary: Color.lerp(accentPrimary, other.accentPrimary, t)!,
      accentSecondary: Color.lerp(accentSecondary, other.accentSecondary, t)!,
      error: Color.lerp(error, other.error, t)!,
    );
  }
}
