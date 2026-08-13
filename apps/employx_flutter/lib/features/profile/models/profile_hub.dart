import 'package:flutter/foundation.dart';

import 'cv_document.dart';

/// Contenedor de nivel usuario para la identidad y los CV de EmployX.
///
/// NO sustituye a ProfessionalProfileModel.
/// ProfessionalProfileModel continúa representando la información
/// profesional estructurada utilizada por ATS.
@immutable
class ProfileHub {
  final String id;
  final String displayName;
  final String? email;
  final String? avatarPath;
  final List<CVDocument> cvs;
  final String? activeCvId;

  const ProfileHub({
    required this.id,
    this.displayName = '',
    this.email,
    this.avatarPath,
    this.cvs = const [],
    this.activeCvId,
  });

  CVDocument? get activeCv {
    final id = activeCvId;

    if (id == null || id.isEmpty) {
      return null;
    }

    for (final cv in cvs) {
      if (cv.id == id) {
        return cv;
      }
    }

    return null;
  }

  ProfileHub selectActiveCv(String cvId) {
    if (!cvs.any((cv) => cv.id == cvId)) {
      return this;
    }

    final updated = cvs.map((cv) {
      final active = cv.id == cvId;

      return cv.copyWith(
        isActive: active,
        updatedAt: active
            ? DateTime.now()
            : cv.updatedAt,
      );
    }).toList(growable: false);

    return copyWith(
      cvs: updated,
      activeCvId: cvId,
    );
  }

  ProfileHub addCv(CVDocument cv) {
    if (cvs.any((item) => item.id == cv.id)) {
      return this;
    }

    final makeActive = cvs.isEmpty;

    final normalized = cv.copyWith(
      isActive: makeActive,
    );

    return copyWith(
      cvs: [...cvs, normalized],
      activeCvId:
          makeActive ? normalized.id : activeCvId,
    );
  }

  ProfileHub removeCv(String cvId) {
    final remaining = cvs
        .where((cv) => cv.id != cvId)
        .toList(growable: false);

    if (remaining.length == cvs.length) {
      return this;
    }

    if (remaining.isEmpty) {
      return copyWith(
        cvs: const [],
        clearActiveCvId: true,
      );
    }

    var nextActiveId = activeCvId;

    if (nextActiveId == null ||
        nextActiveId == cvId) {
      nextActiveId = remaining.first.id;
    }

    final normalized = remaining.map((cv) {
      return cv.copyWith(
        isActive: cv.id == nextActiveId,
      );
    }).toList(growable: false);

    return copyWith(
      cvs: normalized,
      activeCvId: nextActiveId,
    );
  }

  ProfileHub copyWith({
    String? id,
    String? displayName,
    String? email,
    String? avatarPath,
    List<CVDocument>? cvs,
    String? activeCvId,
    bool clearEmail = false,
    bool clearAvatarPath = false,
    bool clearActiveCvId = false,
  }) {
    return ProfileHub(
      id: id ?? this.id,
      displayName:
          displayName ?? this.displayName,
      email:
          clearEmail ? null : email ?? this.email,
      avatarPath:
          clearAvatarPath
              ? null
              : avatarPath ?? this.avatarPath,
      cvs: cvs ?? this.cvs,
      activeCvId:
          clearActiveCvId
              ? null
              : activeCvId ?? this.activeCvId,
    );
  }

  factory ProfileHub.fromJson(
    Map<String, dynamic> json,
  ) {
    final raw = json['cvs'];

    final parsed = raw is List
        ? raw
            .whereType<Map>()
            .map(
              (item) => CVDocument.fromJson(
                item.cast<String, dynamic>(),
              ),
            )
            .toList(growable: false)
        : const <CVDocument>[];

    return ProfileHub(
      id: _string(json['id']),
      displayName: _string(
        json['display_name'] ??
            json['displayName'],
      ),
      email: _nullable(json['email']),
      avatarPath: _nullable(
        json['avatar_path'] ??
            json['avatarPath'],
      ),
      cvs: parsed,
      activeCvId: _nullable(
        json['active_cv_id'] ??
            json['activeCvId'],
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'email': email,
      'avatar_path': avatarPath,
      'active_cv_id': activeCvId,
      'cvs': cvs
          .map((cv) => cv.toJson())
          .toList(),
    };
  }

  static String _string(dynamic value) {
    return value?.toString().trim() ?? '';
  }

  static String? _nullable(dynamic value) {
    final valueString = _string(value);

    return valueString.isEmpty
        ? null
        : valueString;
  }
}
