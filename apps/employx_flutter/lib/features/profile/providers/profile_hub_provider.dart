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
/// MissionActions se ocupa del procesamiento de la misión/upload,
/// pero no determina qué perfil debe mostrarse en la pantalla
/// de Perfil Profesional.
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
  /// Si el perfil recibido ya tiene un CV activo, intenta cargar
  /// automáticamente el ProfessionalProfile asociado.
  Future<void> initialize(ProfileHub profile) async {
    _profile = profile;
    _activeProfessionalProfile = null;
    _profileError = null;

    notifyListeners();

    await _loadActiveProfessionalProfile();
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

    final shouldBeActive = !hasCvs;

    final document = CVDocument(
      id: id,
      displayName: _buildDisplayName(
        displayName,
        fileName,
      ),
      fileName: fileName,
      localPath: localPath,
      remotePath: remotePath,
      professionalProfileId: professionalProfileId,
      createdAt: now,
      updatedAt: now,
      isActive: shouldBeActive,
    );

    final updated = _profile.addCv(document);

    if (identical(updated, _profile)) {
      return;
    }

    _profile = updated;

    // Notificamos inmediatamente para que la lista de CVs
    // aparezca aunque la carga del perfil todavía esté en curso.
    notifyListeners();

    // Solamente cambiamos/cargamos el perfil si este CV
    // realmente se convirtió en el CV activo.
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
      // Aunque el CV ya sea activo, intentamos garantizar que
      // su perfil esté cargado.
      await _loadActiveProfessionalProfile();
      return;
    }

    _profile = updated;

    // El perfil anterior deja de representar al CV activo.
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
    final wasActive = _profile.activeCv?.id == cvId;

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
  Future<void> refreshActiveProfessionalProfile() async {
    await _loadActiveProfessionalProfile();
  }

  Future<void> _loadActiveProfessionalProfile() async {
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

    final requestId = ++_profileLoadRequest;

    _isLoadingProfile = true;
    _profileError = null;

    notifyListeners();

    try {
      final professionalProfile =
          await _profileRepository.getProfile(
        profileId,
      );

      // Si mientras esperábamos el servidor el usuario cambió
      // de CV, ignoramos esta respuesta porque pertenece al CV
      // anterior.
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