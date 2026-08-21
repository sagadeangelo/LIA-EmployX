import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
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
  static const Duration _checkTimeout = Duration(seconds: 5);
  static const Duration _positionTimeout = Duration(seconds: 8);
  static const Duration _reverseTimeout = Duration(seconds: 8);

  static ApiClient get _api => sl<ApiClient>();

  /// Detecta la ubicación actual del dispositivo/navegador y la resuelve
  /// mediante el backend de LIA-EmployX.
  ///
  /// Garantiza que NUNCA quede un Future pendiente indefinidamente y que
  /// siempre retorne un [LocationResult] controlado.
  static Future<LocationResult> detectLocation() async {
    try {
      // 1. Verificar que el servicio de ubicación está habilitado
      bool serviceEnabled = false;
      try {
        serviceEnabled = await Geolocator.isLocationServiceEnabled()
            .timeout(_checkTimeout);
      } on TimeoutException {
        return LocationError(
          'Tiempo de espera agotado al consultar el servicio de ubicación.',
        );
      } on LocationServiceDisabledException {
        return LocationError(
          'El servicio de ubicación está deshabilitado en tu dispositivo.',
        );
      } catch (_) {
        return LocationError(
          'Tu navegador no permite detectar la ubicación.',
        );
      }

      if (!serviceEnabled) {
        return LocationError(
          'El servicio de ubicación está desactivado en tu navegador o sistema.',
        );
      }

      // 2. Verificar/solicitar permisos
      LocationPermission permission;
      try {
        permission = await Geolocator.checkPermission()
            .timeout(_checkTimeout);

        if (permission == LocationPermission.denied) {
          permission = await Geolocator.requestPermission()
              .timeout(_checkTimeout);
          if (permission == LocationPermission.denied) {
            return LocationError(
              'No se concedió permiso para acceder a la ubicación.',
            );
          }
        }

        if (permission == LocationPermission.deniedForever) {
          return LocationError(
            'El acceso a la ubicación está bloqueado en tu navegador. Habilítalo en los ajustes del sitio o ingresa tu ciudad manualmente.',
          );
        }
      } on TimeoutException {
        return LocationError(
          'Tiempo de espera agotado al solicitar permisos de ubicación.',
        );
      } on PermissionDeniedException {
        return LocationError(
          'No se concedió permiso para acceder a la ubicación.',
        );
      } on PlatformException catch (e) {
        return LocationError(
          'Error del navegador con los permisos de ubicación: ${e.message ?? e.code}',
        );
      } catch (_) {
        return LocationError(
          'No fue posible verificar los permisos de ubicación.',
        );
      }

      // 3. Obtener coordenadas con timeout estricto a nivel Dart
      Position position;
      try {
        position = await Geolocator.getCurrentPosition(
          locationSettings: const LocationSettings(
            accuracy: LocationAccuracy.medium,
            timeLimit: _positionTimeout,
          ),
        ).timeout(_positionTimeout);
      } on TimeoutException {
        return LocationError(
          'Tiempo de espera agotado al obtener coordenadas GPS.',
        );
      } on PermissionDeniedException {
        return LocationError(
          'Permiso de ubicación denegado por el navegador.',
        );
      } on LocationServiceDisabledException {
        return LocationError(
          'El servicio de ubicación está deshabilitado.',
        );
      } on PlatformException catch (e) {
        return LocationError(
          'Error al obtener ubicación: ${e.message ?? e.code}',
        );
      } catch (_) {
        return LocationError(
          'No fue posible obtener coordenadas de ubicación.',
        );
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
        ).timeout(_reverseTimeout);

        final rawData = response.data;
        final Map<String, dynamic> data;
        if (rawData is Map<String, dynamic>) {
          data = rawData;
        } else if (rawData is Map) {
          data = Map<String, dynamic>.from(rawData);
        } else {
          return LocationError(
            'Respuesta inválida del servidor de geolocalización.',
          );
        }

        resolved = ResolvedDeviceLocation(
          latitude: position.latitude,
          longitude: position.longitude,
          city: data['city'] as String?,
          region: data['region'] as String?,
          country: data['country'] as String?,
          countryCode: data['country_code'] as String?,
          displayName: data['display_name'] as String? ?? 'Ubicación detectada',
        );
      } on TimeoutException {
        return LocationError(
          'Tiempo de espera agotado al resolver la dirección.',
        );
      } on DioException catch (e) {
        if (e.type == DioExceptionType.connectionTimeout ||
            e.type == DioExceptionType.receiveTimeout ||
            e.type == DioExceptionType.sendTimeout) {
          return LocationError(
            'Tiempo de espera agotado con el servidor de geolocalización.',
          );
        }
        return LocationError(
          'Error al contactar al servidor de geolocalización.',
        );
      } catch (_) {
        return LocationError(
          'No fue posible resolver la ubicación (Reverse Geocoding).',
        );
      }

      return LocationSuccess(resolved);
    } catch (e) {
      return LocationError(
        'Error inesperado al detectar ubicación: $e',
      );
    }
  }
}
