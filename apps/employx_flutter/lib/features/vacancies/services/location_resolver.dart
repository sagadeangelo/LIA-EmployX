/// Resolución de texto de ubicación a código ISO de país.
///
/// FreeHire /jobs/search acepta únicamente el parámetro [countries]
/// con códigos ISO 3166-1 alpha-2 (ej. "mx", "us", "es").
///
/// Esta clase convierte la cadena de texto libre introducida por el
/// usuario en el código ISO correspondiente y conserva la ciudad
/// y región para el ranking geográfico posterior.
class LocationResolver {
  const LocationResolver._();

  // ============================================================
  // RESOLUCIÓN PRINCIPAL
  // ============================================================

  /// Convierte un texto libre de ubicación a [ResolvedLocation].
  ///
  /// Estrategia: separar por coma e iterar de derecha a izquierda
  /// (país → estado → ciudad). Si ninguna parte resuelve, intentar
  /// el string completo.
  ///
  /// Retorna null si no se puede determinar el país.
  static ResolvedLocation? resolve(String input) {
    final raw = input.trim();
    if (raw.isEmpty) return null;

    final parts = raw.split(',').map((p) => p.trim()).toList();

    // Intentar desde la parte más derecha hacia la izquierda
    for (int i = parts.length - 1; i >= 0; i--) {
      final code = _resolveCode(parts[i]);
      if (code != null) {
        final city = parts.isNotEmpty ? parts[0] : null;
        final region = parts.length > 2 ? parts[1] : null;
        return ResolvedLocation(
          rawInput: raw,
          city: city != parts[i] ? city : null,
          region: region,
          countryCode: code,
        );
      }
    }

    return null;
  }

  // ============================================================
  // MAPEO TEXTO → CÓDIGO ISO
  // ============================================================

  static String? _resolveCode(String text) {
    final normalized = text.toLowerCase().trim();
    return _countryMap[normalized];
  }

  /// Mapa de variantes comunes → código ISO 3166-1 alpha-2.
  /// Enfocado en LATAM, España y mercados tecnológicos frecuentes.
  static const Map<String, String> _countryMap = {
    // ── MÉXICO ──────────────────────────────────────────────────
    'mx': 'mx', 'mex': 'mx', 'mexico': 'mx', 'méxico': 'mx',
    'méx': 'mx', 'cdmx': 'mx',
    'ciudad de mexico': 'mx', 'ciudad de méxico': 'mx',
    // Estados de México
    'coahuila': 'mx', 'jalisco': 'mx',
    'nuevo leon': 'mx', 'nuevo león': 'mx',
    'sonora': 'mx', 'baja california': 'mx', 'sinaloa': 'mx',
    'tamaulipas': 'mx', 'yucatan': 'mx', 'yucatán': 'mx',
    'hidalgo': 'mx', 'michoacan': 'mx', 'michoacán': 'mx',
    'guanajuato': 'mx', 'estado de mexico': 'mx',
    'estado de méxico': 'mx', 'veracruz': 'mx', 'oaxaca': 'mx',
    'durango': 'mx', 'chihuahua': 'mx',
    // Ciudades de México
    'monterrey': 'mx', 'guadalajara': 'mx', 'puebla': 'mx',
    'tijuana': 'mx', 'leon': 'mx', 'juarez': 'mx',
    'mérida': 'mx', 'merida': 'mx',
    'queretaro': 'mx', 'querétaro': 'mx',
    'san luis potosi': 'mx', 'san luis potosí': 'mx',
    'aguascalientes': 'mx', 'saltillo': 'mx',
    'hermosillo': 'mx', 'mexicali': 'mx',
    'culiacan': 'mx', 'culiacán': 'mx',
    'acapulco': 'mx', 'cancun': 'mx', 'cancún': 'mx',
    'torreon': 'mx', 'torreón': 'mx', 'morelia': 'mx',
    'toluca': 'mx',
    'piedras negras': 'mx', 'nuevo laredo': 'mx',
    'reynosa': 'mx', 'matamoros': 'mx', 'la paz': 'mx',
    'tapachula': 'mx', 'mazatlan': 'mx', 'mazatlán': 'mx',
    'irapuato': 'mx', 'celaya': 'mx', 'apodaca': 'mx',
    'san nicolas de los garza': 'mx', 'ecatepec': 'mx',
    'naucalpan': 'mx', 'tlalnepantla': 'mx', 'nezahualcoyotl': 'mx',
    // ── ESTADOS UNIDOS ──────────────────────────────────────────
    'us': 'us', 'usa': 'us',
    'united states': 'us', 'estados unidos': 'us',
    'new york': 'us', 'nueva york': 'us',
    'los angeles': 'us', 'chicago': 'us', 'houston': 'us',
    'miami': 'us', 'san francisco': 'us', 'austin': 'us',
    'seattle': 'us', 'boston': 'us', 'denver': 'us',
    'atlanta': 'us', 'dallas': 'us', 'phoenix': 'us',
    'california': 'us', 'texas': 'us', 'florida': 'us',
    'new york state': 'us', 'washington dc': 'us',
    // ── ESPAÑA ──────────────────────────────────────────────────
    'es': 'es', 'spain': 'es', 'españa': 'es', 'espana': 'es',
    'madrid': 'es', 'barcelona': 'es', 'valencia': 'es',
    'sevilla': 'es', 'seville': 'es', 'bilbao': 'es',
    'zaragoza': 'es', 'malaga': 'es', 'málaga': 'es',
    'alicante': 'es', 'granada': 'es', 'palma': 'es',
    // ── COLOMBIA ────────────────────────────────────────────────
    'co': 'co', 'colombia': 'co',
    'bogota': 'co', 'bogotá': 'co',
    'medellin': 'co', 'medellín': 'co',
    'cali': 'co', 'barranquilla': 'co', 'bucaramanga': 'co',
    // ── ARGENTINA ───────────────────────────────────────────────
    'ar': 'ar', 'argentina': 'ar',
    'buenos aires': 'ar',
    'córdoba': 'ar', 'cordoba': 'ar', 'rosario': 'ar',
    'mendoza': 'ar', 'tucuman': 'ar', 'tucumán': 'ar',
    // ── CHILE ───────────────────────────────────────────────────
    'cl': 'cl', 'chile': 'cl',
    'santiago': 'cl', 'valparaíso': 'cl', 'valparaiso': 'cl',
    // ── PERÚ ────────────────────────────────────────────────────
    'pe': 'pe', 'peru': 'pe', 'perú': 'pe', 'lima': 'pe',
    // ── BRASIL ──────────────────────────────────────────────────
    'br': 'br', 'brazil': 'br', 'brasil': 'br',
    'sao paulo': 'br', 'são paulo': 'br',
    'rio de janeiro': 'br', 'brasilia': 'br', 'brasília': 'br',
    'curitiba': 'br', 'belo horizonte': 'br',
    // ── REINO UNIDO ─────────────────────────────────────────────
    'gb': 'gb', 'uk': 'gb',
    'united kingdom': 'gb', 'reino unido': 'gb',
    'london': 'gb', 'londres': 'gb',
    'manchester': 'gb', 'edinburgh': 'gb',
    // ── CANADÁ ──────────────────────────────────────────────────
    'ca': 'ca', 'canada': 'ca', 'canadá': 'ca',
    'toronto': 'ca', 'montreal': 'ca', 'vancouver': 'ca',
    // ── ALEMANIA ────────────────────────────────────────────────
    'de': 'de', 'germany': 'de', 'alemania': 'de',
    'berlin': 'de', 'berlín': 'de',
    'munich': 'de', 'múnich': 'de', 'frankfurt': 'de',
    // ── PORTUGAL ────────────────────────────────────────────────
    'pt': 'pt', 'portugal': 'pt',
    'lisbon': 'pt', 'lisboa': 'pt', 'porto': 'pt',
    // ── URUGUAY ─────────────────────────────────────────────────
    'uy': 'uy', 'uruguay': 'uy', 'montevideo': 'uy',
    // ── ECUADOR ─────────────────────────────────────────────────
    'ec': 'ec', 'ecuador': 'ec', 'quito': 'ec', 'guayaquil': 'ec',
    // ── VENEZUELA ───────────────────────────────────────────────
    've': 've', 'venezuela': 've', 'caracas': 've',
    // ── PANAMÁ ──────────────────────────────────────────────────
    'pa': 'pa', 'panama': 'pa', 'panamá': 'pa',
    // ── COSTA RICA ──────────────────────────────────────────────
    'cr': 'cr', 'costa rica': 'cr', 'san jose': 'cr', 'san josé': 'cr',
  };
}

// ============================================================
// MODELO RESULTADO
// ============================================================

/// Resultado de la resolución de texto de ubicación.
class ResolvedLocation {
  /// Texto original introducido por el usuario.
  final String rawInput;

  /// Ciudad extraída del texto (primer elemento separado por coma).
  /// Puede ser null si el texto era solo el país.
  final String? city;

  /// Estado o región extraído (segundo elemento separado por coma).
  final String? region;

  /// Código ISO 3166-1 alpha-2 del país.
  final String countryCode;

  const ResolvedLocation({
    required this.rawInput,
    required this.city,
    required this.region,
    required this.countryCode,
  });

  @override
  String toString() =>
      'ResolvedLocation(city=$city, region=$region, country=$countryCode)';
}
