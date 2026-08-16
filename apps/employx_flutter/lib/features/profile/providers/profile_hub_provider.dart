import 'package:flutter/foundation.dart';

import '../../../core/models/professional_profile_model.dart';
import '../../../core/repositories/profile_repository.dart';

import '../models/cv_document.dart';
import '../models/profile_hub.dart';

/// Estado central del perfil del usuario.
///
/// Mantiene:
/// - identidad
/// - avatar
/// - colección de CVs
/// - CV activo
/// - ProfessionalProfile asociado al CV activo
///
/// El ProfileHub es la fuente de verdad para la selección del CV.
///
/// MissionActions se ocupa del procesamiento de la misión/upload,
/// pero no determina qué perfil debe mostrarse en la pantalla
/// de Perfil Profesional.
///
/// Los CV persistidos en backend se hidratan mediante
/// ProfileRepository.getCVs().
class ProfileHubProvider extends ChangeNotifier {
  final ProfileRepository _profileRepository;

  ProfileHubProvider({
    ProfileRepository? profileRepository,
  }) : _profileRepository =
            profileRepository ?? ProfileRepository();

  ProfileHub _profile = const ProfileHub(
    id: 'local-user',
  );

  ProfessionalProfile? _activeProfessionalProfile;

  bool _isLoadingProfile = false;

  String? _profileError;

  int _profileLoadRequest = 0;

  int _cvHydrationRequest = 0;

  // ============================================================
  // GETTERS
  // ============================================================

  ProfileHub get profile => _profile;

  List<CVDocument> get cvs => _profile.cvs;

  CVDocument? get activeCv => _profile.activeCv;

  ProfessionalProfile? get activeProfessionalProfile =>
      _activeProfessionalProfile;

  String? get avatarPath => _profile.avatarPath;

  bool get hasCvs => _profile.cvs.isNotEmpty;

  bool get isLoadingProfile => _isLoadingProfile;

  String? get profileError => _profileError;

  bool get hasActiveProfessionalProfile =>
      _activeProfessionalProfile != null;

  // ============================================================
  // INITIALIZATION
  // ============================================================

  /// Inicializa el Profile Hub.
  ///
  /// Primero conserva el estado recibido por la aplicación y
  /// después intenta hidratar los CV persistidos en backend.
  ///
  /// Una vez recuperados los CV:
  ///
  /// 1. conserva el CV activo actual si todavía existe;
  /// 2. si no existe CV activo, selecciona el primero disponible;
  /// 3. carga el ProfessionalProfile correspondiente al CV activo.
  Future<void> initialize(ProfileHub profile) async {
    ++_cvHydrationRequest;
    ++_profileLoadRequest;

    _profile = profile;
    _activeProfessionalProfile = null;
    _profileError = null;
    _isLoadingProfile = false;

    notifyListeners();

    await loadPersistedCvs();
  }

  // ============================================================
  // BACKEND HYDRATION
  // ============================================================

  /// Recupera los CV persistidos del backend y los incorpora
  /// al ProfileHub actual.
  ///
  /// Esta operación es idempotente:
  /// ejecutar varias veces no debe crear duplicados.
  ///
  /// La selección del CV activo sigue estas reglas:
  ///
  /// 1. conservar el CV activo actual si todavía existe;
  /// 2. si no existe, conservar un CV marcado como activo;
  /// 3. si tampoco existe, seleccionar el primer CV.
  Future<void> loadPersistedCvs() async {
    final requestId = ++_cvHydrationRequest;

    try {
      final persistedCvs =
          await _profileRepository.getCVs();

      // Si otra hidratación comenzó mientras esperábamos
      // la respuesta, ignoramos esta respuesta.
      if (requestId != _cvHydrationRequest) {
        return;
      }

      // ----------------------------------------------------------
      // BACKEND SIN CVs
      // ----------------------------------------------------------

      if (persistedCvs.isEmpty) {
        // No borramos los CV locales.
        //
        // Esto es importante para no destruir un estado local
        // válido si el backend temporalmente no devuelve datos.
        if (_profile.activeCv != null) {
          await _loadActiveProfessionalProfile();
        }

        return;
      }

      // ----------------------------------------------------------
      // RECORDAR CV ACTIVO ACTUAL
      // ----------------------------------------------------------

      final currentActiveId =
          _profile.activeCvId;

      // ----------------------------------------------------------
      // MERGE LOCAL + BACKEND
      // ----------------------------------------------------------

      final merged = <CVDocument>[];
      final backendIds = <String>{};

      // Primero conservamos los CV que ya estaban en memoria.
      for (final localCv in _profile.cvs) {
        merged.add(localCv);
      }

      // Después incorporamos los CV persistidos.
      for (final persistedCv in persistedCvs) {
        backendIds.add(persistedCv.id);

        final existingIndex = merged.indexWhere(
          (cv) => cv.id == persistedCv.id,
        );

        if (existingIndex == -1) {
          merged.add(persistedCv);
        } else {
          // El backend es la fuente de verdad para los datos
          // persistidos, pero conservamos localPath e isActive
          // cuando existen localmente.
          final existing = merged[existingIndex];

          merged[existingIndex] =
              persistedCv.copyWith(
            localPath:
                existing.localPath ??
                    persistedCv.localPath,
            isActive:
                existing.isActive,
          );
        }
      }

      // ----------------------------------------------------------
      // DETERMINAR CV ACTIVO
      // ----------------------------------------------------------

      String? nextActiveId;

      // 1. Intentar conservar el CV activo anterior.
      if (currentActiveId != null &&
          currentActiveId.isNotEmpty &&
          merged.any(
            (cv) => cv.id == currentActiveId,
          )) {
        nextActiveId = currentActiveId;
      }

      // 2. Si no existe, buscar uno que venga marcado como activo.
      if (nextActiveId == null) {
        for (final cv in merged) {
          if (cv.isActive) {
            nextActiveId = cv.id;
            break;
          }
        }
      }

      // 3. Si todavía no hay activo, usar el primero.
      if (nextActiveId == null &&
          merged.isNotEmpty) {
        nextActiveId = merged.first.id;
      }

      // ----------------------------------------------------------
      // NORMALIZAR ESTADO ACTIVO
      // ----------------------------------------------------------

      final normalized = merged.map((cv) {
        return cv.copyWith(
          isActive:
              cv.id == nextActiveId,
        );
      }).toList(growable: false);

      // ----------------------------------------------------------
      // ACTUALIZAR PROFILE HUB
      // ----------------------------------------------------------

      _profile = _profile.copyWith(
        cvs: normalized,
        activeCvId: nextActiveId,
        clearActiveCvId:
            nextActiveId == null,
      );

      _profileError = null;

      notifyListeners();

      // ----------------------------------------------------------
      // CARGAR PROFESSIONAL PROFILE
      // ----------------------------------------------------------

      await _loadActiveProfessionalProfile();
    } catch (e) {
      if (requestId != _cvHydrationRequest) {
        return;
      }

      // No destruimos los CV locales si falla el backend.
      //
      // Si ya tenemos un CV activo, intentamos cargar su perfil
      // profesional desde el estado disponible.
      if (_profile.activeCv != null) {
        await _loadActiveProfessionalProfile();
      } else {
        _profileError =
            'No se pudieron cargar los CV guardados.';

        notifyListeners();
      }
    }
  }

  // ============================================================
  // CV MANAGEMENT
  // ============================================================

  /// Agrega un CV al perfil.
  ///
  /// No cambia el CV activo si ya existe uno.
  void addCv(CVDocument cv) {
    final updated = _profile.addCv(cv);

    if (identical(updated, _profile)) {
      return;
    }

    _profile = updated;

    notifyListeners();
  }

  /// Registra un CV recién procesado por el backend.
  ///
  /// El primer CV se convierte automáticamente en activo.
  ///
  /// Los siguientes CVs se agregan a la colección sin sustituir
  /// el CV activo actual.
  ///
  /// Si el CV recién registrado se convierte en activo, se carga
  /// inmediatamente su ProfessionalProfile.
  Future<void> registerProcessedCv({
    required String id,
    required String fileName,
    String? localPath,
    String? remotePath,
    String? professionalProfileId,
    String? displayName,
  }) async {
    final now = DateTime.now();

    // SIEMPRE hacemos que el CV recién procesado sea el activo
    final shouldBeActive = true;

    final document = CVDocument(
      id: id,
      displayName: _buildDisplayName(
        displayName,
        fileName,
      ),
      fileName: fileName,
      localPath: localPath,
      remotePath: remotePath,
      professionalProfileId:
          professionalProfileId,
      createdAt: now,
      updatedAt: now,
      isActive: shouldBeActive,
    );

    var updated = _profile.addCv(document);

    if (identical(updated, _profile)) {
      return;
    }

    // Forzar que el ProfileHub marque este CV como el activo,
    // desactivando los anteriores.
    updated = updated.selectActiveCv(document.id);

    _profile = updated;

    notifyListeners();

    if (shouldBeActive) {
      await _loadActiveProfessionalProfile();
    }
  }

  /// Selecciona un CV existente como CV activo.
  ///
  /// Después de cambiar la selección, carga el ProfessionalProfile
  /// correspondiente usando CVDocument.professionalProfileId.
  Future<void> selectActiveCv(String cvId) async {
    final updated = _profile.selectActiveCv(cvId);

    if (identical(updated, _profile)) {
      await _loadActiveProfessionalProfile();
      return;
    }

    _profile = updated;

    _activeProfessionalProfile = null;
    _profileError = null;

    notifyListeners();

    await _loadActiveProfessionalProfile();
  }

  /// Elimina un CV del perfil.
  ///
  /// Si se elimina el CV activo y el modelo selecciona otro,
  /// cargamos automáticamente el perfil correspondiente.
  Future<void> removeCv(String cvId) async {
    final wasActive =
        _profile.activeCv?.id == cvId;

    final updated = _profile.removeCv(cvId);

    if (identical(updated, _profile)) {
      return;
    }

    _profile = updated;

    if (wasActive) {
      _activeProfessionalProfile = null;
      _profileError = null;
    }

    notifyListeners();

    if (wasActive) {
      await _loadActiveProfessionalProfile();
    }
  }

  // ============================================================
  // PROFESSIONAL PROFILE
  // ============================================================

  /// Carga el ProfessionalProfile correspondiente al CV activo.
  Future<void>
      refreshActiveProfessionalProfile() async {
    await _loadActiveProfessionalProfile();
  }

  Future<void>
      _loadActiveProfessionalProfile() async {
    final cv = _profile.activeCv;

    if (cv == null) {
      _activeProfessionalProfile = null;
      _profileError = null;
      _isLoadingProfile = false;

      notifyListeners();
      return;
    }

    final profileId =
        cv.professionalProfileId?.trim();

    if (profileId == null ||
        profileId.isEmpty) {
      _activeProfessionalProfile = null;
      _profileError =
          'El CV activo no tiene un perfil profesional asociado.';
      _isLoadingProfile = false;

      notifyListeners();
      return;
    }

    final requestId =
        ++_profileLoadRequest;

    _isLoadingProfile = true;
    _profileError = null;

    notifyListeners();

    try {
      final professionalProfile =
          await _profileRepository.getProfile(
        profileId,
      );

      // Si mientras esperábamos el servidor el usuario
      // cambió de CV, ignoramos esta respuesta porque
      // pertenece al CV anterior.
      if (requestId != _profileLoadRequest) {
        return;
      }

      _activeProfessionalProfile =
          professionalProfile;

      if (professionalProfile == null) {
        _profileError =
            'No se encontró el perfil profesional asociado '
            'al CV seleccionado.';
      } else {
        _profileError = null;
      }
    } catch (e) {
      if (requestId != _profileLoadRequest) {
        return;
      }

      _activeProfessionalProfile = null;
      _profileError =
          'No se pudo cargar el perfil profesional.';
    } finally {
      if (requestId == _profileLoadRequest) {
        _isLoadingProfile = false;
        notifyListeners();
      }
    }
  }

  // ============================================================
  // IDENTITY / AVATAR
  // ============================================================

  /// Actualiza el avatar.
  void setAvatar(String? avatarPath) {
    _profile = _profile.copyWith(
      avatarPath: avatarPath,
      clearAvatarPath:
          avatarPath == null ||
          avatarPath.isEmpty,
    );

    notifyListeners();
  }

  /// Actualiza datos básicos de identidad.
  void updateIdentity({
    String? displayName,
    String? email,
  }) {
    _profile = _profile.copyWith(
      displayName: displayName,
      email: email,
    );

    notifyListeners();
  }

  // ============================================================
  // RESET
  // ============================================================

  /// Limpia completamente el estado local.
  void clear() {
    ++_profileLoadRequest;
    ++_cvHydrationRequest;

    _profile = const ProfileHub(
      id: 'local-user',
    );

    _activeProfessionalProfile = null;
    _isLoadingProfile = false;
    _profileError = null;

    notifyListeners();
  }

  // ============================================================
  // DISPLAY NAME
  // ============================================================

  String _buildDisplayName(
    String? providedName,
    String fileName,
  ) {
    final explicitName =
        providedName?.trim() ?? '';

    if (explicitName.isNotEmpty) {
      return explicitName;
    }

    final normalized =
        fileName.trim();

    if (normalized.isEmpty) {
      return 'CV sin nombre';
    }

    final lastSeparator =
        normalized.lastIndexOf(
      RegExp(r'[\\/]'),
    );

    final baseName =
        lastSeparator >= 0
            ? normalized.substring(
                lastSeparator + 1,
              )
            : normalized;

    final extensionIndex =
        baseName.lastIndexOf('.');

    if (extensionIndex > 0) {
      return baseName.substring(
        0,
        extensionIndex,
      );
    }

    return baseName;
  }
}