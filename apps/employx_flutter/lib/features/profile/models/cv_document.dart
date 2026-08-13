import 'package:flutter/foundation.dart';

@immutable
class CVDocument {
  final String id;
  final String displayName;
  final String fileName;
  final String? localPath;
  final String? remotePath;
  final String? professionalProfileId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isActive;

  const CVDocument({
    required this.id,
    required this.displayName,
    required this.fileName,
    this.localPath,
    this.remotePath,
    this.professionalProfileId,
    required this.createdAt,
    required this.updatedAt,
    this.isActive = false,
  });

  CVDocument copyWith({
    String? id,
    String? displayName,
    String? fileName,
    String? localPath,
    String? remotePath,
    String? professionalProfileId,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isActive,
  }) {
    return CVDocument(
      id: id ?? this.id,
      displayName: displayName ?? this.displayName,
      fileName: fileName ?? this.fileName,
      localPath: localPath ?? this.localPath,
      remotePath: remotePath ?? this.remotePath,
      professionalProfileId:
          professionalProfileId ?? this.professionalProfileId,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isActive: isActive ?? this.isActive,
    );
  }

  factory CVDocument.fromJson(Map<String, dynamic> json) {
    return CVDocument(
      id: _string(json['id']),
      displayName:
          _string(json['display_name'] ?? json['displayName']),
      fileName:
          _string(json['file_name'] ?? json['fileName']),
      localPath:
          _nullable(json['local_path'] ?? json['localPath']),
      remotePath:
          _nullable(json['remote_path'] ?? json['remotePath']),
      professionalProfileId: _nullable(
        json['professional_profile_id'] ??
            json['professionalProfileId'],
      ),
      createdAt:
          _date(json['created_at'] ?? json['createdAt']),
      updatedAt:
          _date(json['updated_at'] ?? json['updatedAt']),
      isActive:
          json['is_active'] == true ||
          json['isActive'] == true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'file_name': fileName,
      'local_path': localPath,
      'remote_path': remotePath,
      'professional_profile_id': professionalProfileId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'is_active': isActive,
    };
  }

  static String _string(dynamic value) {
    return value?.toString().trim() ?? '';
  }

  static String? _nullable(dynamic value) {
    final valueString = _string(value);
    return valueString.isEmpty ? null : valueString;
  }

  static DateTime _date(dynamic value) {
    if (value is DateTime) {
      return value;
    }

    return DateTime.tryParse(
          value?.toString() ?? '',
        ) ??
        DateTime.fromMillisecondsSinceEpoch(0);
  }
}
