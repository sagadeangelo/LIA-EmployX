import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'lia_colors.dart';
import 'lia_spacings.dart';
import 'lia_typography.dart';

/// Define el tema central de la aplicación.
class LiaTheme {
  /// Devuelve el ThemeData para el Modo Oscuro (Diseño principal de LIA)
  static ThemeData get darkTheme {
    final colors = LiaColors.dark;
    final typography = LiaTypography.modern;
    final spacings = LiaSpacings.modern;

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: colors.background,
      
      // Extensiones de diseño
      extensions: <ThemeExtension<dynamic>>[
        colors,
        typography,
        spacings,
      ],

      // Ajustes de AppBar para que sea minimalista
      appBarTheme: AppBarTheme(
        backgroundColor: colors.background,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        iconTheme: IconThemeData(color: colors.textPrimary),
      ),
      
      // Eliminamos el efecto ripple (splash) en toda la app para un 
      // look más limpio, estilo web/desktop
      splashColor: Colors.transparent,
      highlightColor: Colors.transparent,
      hoverColor: Colors.transparent,
      
      // Configuraciones globales para widgets Material (si se usan accidentalmente)
      colorScheme: ColorScheme.dark(
        primary: colors.accentPrimary,
        secondary: colors.accentSecondary,
        surface: colors.surface,
        background: colors.background,
        error: colors.error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: colors.textPrimary,
        onBackground: colors.textPrimary,
        onError: Colors.white,
      ),
    );
  }
}

/// Helper para acceder más fácilmente al tema en la UI
extension LiaThemeExtension on BuildContext {
  LiaColors get liaColors => Theme.of(this).extension<LiaColors>()!;
  LiaTypography get liaTypography => Theme.of(this).extension<LiaTypography>()!;
  LiaSpacings get liaSpacings => Theme.of(this).extension<LiaSpacings>()!;
}
