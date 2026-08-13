import 'dart:async';
import 'package:dio/dio.dart';
import 'package:geolocator/geolocator.dart';

import '../../../core/api/api_client.dart';
import '../../../core/di/service_locator.dart';

/// Modelo interno que representa una ubicación resuelta.
/// Contiene los datos estructurados devueltos por el backend.
class ResolvedDeviceLocation {
  final double latitude;
  final double longitude;
  final String? city;
  final String? region;
  final String? country;
  final String? countryCode;
  final String displayName;

  const ResolvedDeviceLocation({
    required this.latitude,
    required this.longitude,
    this.city,
    this.region,
    this.country,
    this.countryCode,
    required this.displayName,
  });
}

/// Resultado de la detección de ubicación: éxito o error descriptivo.
sealed class LocationResult {}

class LocationSuccess extends LocationResult {
  final ResolvedDeviceLocation location;
  LocationSuccess(this.location);
}

class LocationError extends LocationResult {
  final String message;
  LocationError(this.message);
}

/// Servicio de ubicación exclusivo del módulo de Vacantes.
/// 
/// Flujo:
///   geolocator (Browser Geolocation API / GPS)
///       ↓
///   latitude + longitude
///       ↓
///   POST /api/v1/location/reverse  ← LIA-EmployX Backend
///       ↓
///   city + region + country + country_code + display_name
class DeviceLocationService {
  static ApiClient get _api => sl<ApiClient>();

  /// Detecta la ubicación actual del dispositivo/navegador y la resuelve
  /// mediante el backend de LIA-EmployX.
  static Future<LocationResult> detectLocation() async {
    // 1. Verificar que el servicio de ubicación está habilitado
    bool serviceEnabled;
    try {
      serviceEnabled = await Geolocator.isLocationServiceEnabled();
    } catch (_) {
      return LocationError('Tu navegador no permite detectar la ubicación.');
    }

    if (!serviceEnabled) {
      return LocationError('Tu navegador no permite detectar la ubicación.');
    }

    // 2. Verificar/solicitar permisos
    LocationPermission permission;
    try {
      permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return LocationError(
            'No se concedió permiso para acceder a la ubicación.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return LocationError(
          'No se concedió permiso para acceder a la ubicación.',
        );
      }
    } catch (_) {
      return LocationError(
        'No se concedió permiso para acceder a la ubicación.',
      );
    }

    // 3. Obtener coordenadas
    Position position;
    try {
      position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.medium,
          timeLimit: Duration(seconds: 10),
        ),
      );
    } on TimeoutException {
      return LocationError('Tiempo de espera agotado al detectar el GPS.');
    } catch (_) {
      return LocationError('No fue posible obtener coordenadas GPS.');
    }

    // 4. Enviar al backend para reverse geocoding
    ResolvedDeviceLocation resolved;
    try {
      final response = await _api.post(
        '/location/reverse',
        data: {
          'latitude': position.latitude,
          'longitude': position.longitude,
        },
      );
      final data = response.data as Map<String, dynamic>;
      resolved = ResolvedDeviceLocation(
        latitude: position.latitude,
        longitude: position.longitude,
        city: data['city'] as String?,
        region: data['region'] as String?,
        country: data['country'] as String?,
        countryCode: data['country_code'] as String?,
        displayName: data['display_name'] as String? ?? 'Ubicación detectada',
      );
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        return LocationError('Tiempo de espera agotado con el servidor de geolocalización.');
      }
      return LocationError('Error al contactar al servidor de geolocalización.');
    } catch (_) {
      return LocationError('No fue posible resolver la ubicación (Reverse Geocoding).');
    }

    return LocationSuccess(resolved);
  }
}
