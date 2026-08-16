import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/theme/lia_theme.dart';
import '../../../core/providers/mission_provider.dart';
import '../../../core/actions/mission_actions.dart';
import '../../../core/ui/lia_glass_panel.dart';
import '../../../core/ui/lia_status_indicator.dart';
import '../../../core/ui/lia_progress_bar.dart';
import '../../../core/ui/lia_metric.dart';
import '../../../core/ui/lia_timeline.dart';
import '../../../core/utils/app_logger.dart';
import '../../../core/providers/upload_provider.dart';
import '../../profile/providers/profile_hub_provider.dart';
import '../widgets/cv_upload_overlay.dart';

class CommandCenterScreen extends StatefulWidget {
  const CommandCenterScreen({Key? key}) : super(key: key);

  @override
  State<CommandCenterScreen> createState() => _CommandCenterScreenState();
}

class _CommandCenterScreenState extends State<CommandCenterScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final missionProvider = context.read<MissionProvider>();
    final missionActions = context.read<MissionActions>();

    if (missionProvider.snapshot == null) {
      await missionActions.loadActiveMission();
      if (missionActions.currentMission != null) {
        missionProvider.startMonitoring(missionActions.currentMission!.id);
      }
    }
  }

  Future<void> _pickAndUploadCV() async {
    final startTime = DateTime.now();
    AppLogger.info('Flutter', 'Abriendo FilePicker...');

    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx'],
      withData: kIsWeb,
    );

    final pickerDuration = DateTime.now().difference(startTime).inMilliseconds;

    if (result == null || result.files.isEmpty) {
      AppLogger.warning('Flutter', 'FilePicker cancelado o falló.',
          durationMs: pickerDuration);
      return;
    }

    final file = result.files.single;
    final filePath = file.path;
    final fileBytes = file.bytes;
    final fileName = file.name;
    final fileSize = file.size;

    AppLogger.info(
      'UploadFlow',
      '1. Archivo seleccionado: nombre: $fileName, ruta: $filePath, tamaño: $fileSize bytes',
      durationMs: pickerDuration,
    );

    if (kIsWeb && (fileBytes == null || fileBytes.isEmpty)) {
      AppLogger.error('Flutter', 'FilePicker devolvió un archivo pero no se pudieron leer los bytes (Web).');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error: No se pudieron leer los datos del archivo.')),
        );
      }
      return;
    }

    if (!kIsWeb && (filePath == null || filePath.isEmpty)) {
      AppLogger.error('Flutter',
          'FilePicker devolvió un archivo pero la ruta es null (¿plataforma web?).');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content:
                  Text('Error: Ruta de archivo no disponible.')),
        );
      }
      return;
    }

    if (!mounted) return;

    final confirmed = await _showFileConfirmation(
      context,
      fileName: fileName,
      fileSizeBytes: fileSize,
    );

    if (!confirmed || !mounted) return;

    await _startUploadFlow(filePath, fileBytes, file.name);
  }

  Future<bool> _showFileConfirmation(
    BuildContext context, {
    required String fileName,
    required int fileSizeBytes,
  }) async {
    final colors = context.liaColors;
    final double sizeMB = fileSizeBytes / (1024 * 1024);
    final String ext = fileName.contains('.')
        ? fileName.split('.').last.toUpperCase()
        : '?';

    final result = await showModalBottomSheet<bool>(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (ctx) {
        return Container(
          padding: const EdgeInsets.fromLTRB(28, 28, 28, 36),
          decoration: const BoxDecoration(
            color: Color(0xFF0E1420),
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 24),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade700,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              Text(
                'CV seleccionado',
                style: GoogleFonts.inter(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.5,
                  color: colors.accentPrimary,
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.04),
                  borderRadius: BorderRadius.circular(14),
                  border:
                      Border.all(color: Colors.white.withOpacity(0.07)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF8A2BE2).withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.description_outlined,
                          color: Color(0xFF8A2BE2), size: 28),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            fileName,
                            style: GoogleFonts.inter(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              _buildFileBadge(
                                  '${sizeMB.toStringAsFixed(2)} MB'),
                              const SizedBox(width: 8),
                              _buildFileBadge(ext,
                                  color: const Color(0xFF8A2BE2)),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      style: OutlinedButton.styleFrom(
                        padding:
                            const EdgeInsets.symmetric(vertical: 16),
                        side:
                            BorderSide(color: Colors.grey.shade700),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: Text(
                        'Cancelar',
                        style: GoogleFonts.inter(
                            color: Colors.grey.shade400,
                            fontWeight: FontWeight.w500),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton.icon(
                      onPressed: () => Navigator.of(ctx).pop(true),
                      icon: const Icon(Icons.analytics_outlined, size: 20),
                      label: Text(
                        'Analizar CV',
                        style: GoogleFonts.inter(
                            fontWeight: FontWeight.w700, fontSize: 15),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: colors.accentPrimary,
                        foregroundColor: colors.background,
                        padding:
                            const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                        elevation: 8,
                        shadowColor:
                            colors.accentPrimary.withValues(alpha: 0.4),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
    return result ?? false;
  }

  Widget _buildFileBadge(String text, {Color? color}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: (color ?? Colors.grey.shade600).withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
            color: (color ?? Colors.grey.shade600).withOpacity(0.3)),
      ),
      child: Text(
        text,
        style: GoogleFonts.inter(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: color ?? Colors.grey.shade400,
        ),
      ),
    );
  }

  Future<void> _startUploadFlow(String? filePath, List<int>? fileBytes, String fileName) async {
    if (!mounted) return;

    final missionActions = context.read<MissionActions>();
    final uploadProvider = context.read<UploadProvider>();
    final missionProvider = context.read<MissionProvider>();

    uploadProvider.startUpload(fileName);

    AppLogger.info(
      'UploadFlow',
      '2. Overlay mostrado inmediatamente. Archivo: $fileName',
    );

    CVUploadOverlay.show(
      context,
      onRetry: _handleRetry,
      onPickNew: _handlePickNew,
      onClose: _handleCloseOverlay,
    );

    try {
      AppLogger.info(
        'UploadFlow',
        '3. POST a /api/v1/cv/upload iniciado '
        '(web=${kIsWeb && fileBytes != null})',
      );

      final response = await missionActions.uploadCV(
        filePath: kIsWeb ? null : filePath,
        fileBytes: kIsWeb ? fileBytes : null,
        fileName: fileName,
        onSendProgress: (sent, total) {
          uploadProvider.updateDioProgress(sent, total);
        },
      );

      AppLogger.info(
        'UploadFlow',
        '6. Respuesta backend recibida con éxito',
      );
      AppLogger.info(
        'UploadFlow',
        '7. Cambio a Fase 2 (Análisis)',
      );

      uploadProvider.completeTransfer();

      missionProvider.startMonitoring(
        response.snapshot.mission.id,
        initialSnapshot: response.snapshot,
      );
    } catch (e) {
      final message = e.toString().replaceFirst('Exception: ', '');

      AppLogger.error(
        'UploadFlow',
        'Error real en el flujo de upload: $message',
        error: e,
      );

      uploadProvider.setError(
        message.isEmpty
            ? 'No se pudo procesar el CV. Intenta nuevamente.'
            : message,
      );
    }
  }

  Future<void> _handleRetry() async {
    final uploadProvider = context.read<UploadProvider>();
    final missionActions = context.read<MissionActions>();

    uploadProvider.clearError();

    try {
      await missionActions.resumeMission();
    } catch (e) {
      AppLogger.error('CommandCenter', 'Error al reintentar misión: $e');
      uploadProvider.setError('No se pudo reintentar. Por favor intenta más tarde.');
    }
  }

  Future<void> _handlePickNew() async {
    final uploadProvider = context.read<UploadProvider>();
    final missionProvider = context.read<MissionProvider>();
    final missionActions = context.read<MissionActions>();

    missionActions.detachCurrentMission();
    missionProvider.stopMonitoring();
    uploadProvider.reset();

    AppLogger.info('UploadFlow', '[PickNew] Abriendo FilePicker desde el Overlay...');
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx'],
      withData: kIsWeb,
    );

    if (result == null || result.files.isEmpty) {
      return;
    }

    final file = result.files.single;
    final filePath = file.path;
    final fileBytes = file.bytes;

    if (!kIsWeb && (filePath == null || filePath.isEmpty)) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error: No se pudo obtener la ruta del archivo.')),
      );
      return;
    }

    if (kIsWeb && (fileBytes == null || fileBytes.isEmpty)) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error: No se pudieron leer los datos del archivo.')),
      );
      return;
    }

    if (!mounted) return;
    final confirmed = await _showFileConfirmation(
      context,
      fileName: file.name,
      fileSizeBytes: file.size,
    );

    if (!confirmed || !mounted) return;

    uploadProvider.startUpload(file.name);

    final missionActionsForUpload = context.read<MissionActions>();
    final missionProviderForUpload = context.read<MissionProvider>();

    try {
      AppLogger.info('UploadFlow', '[PickNew] POST iniciado con nuevo archivo');
      final response = await missionActionsForUpload.uploadCV(
            filePath: kIsWeb ? null : filePath,
            fileBytes: kIsWeb ? fileBytes : null,
            fileName: file.name,
            onSendProgress: (sent, total) {
              uploadProvider.updateDioProgress(sent, total);
            },
          );

      uploadProvider.completeTransfer();
      missionProviderForUpload.startMonitoring(
            response.snapshot.mission.id,
            initialSnapshot: response.snapshot,
          );
    } catch (e) {
      AppLogger.error('UploadFlow', '[PickNew] Error en nuevo upload: $e');
      uploadProvider.setError(
          'No pudimos procesar el nuevo archivo. Por favor intenta nuevamente.');
    }
  }

  void _handleCloseOverlay() {
    final uploadProvider = context.read<UploadProvider>();
    final missionProvider = context.read<MissionProvider>();
    final missionActions = context.read<MissionActions>();

    missionActions.detachCurrentMission();
    missionProvider.stopMonitoring();
    uploadProvider.reset();

    AppLogger.info('CommandCenter', 'Overlay cerrado por el usuario. Misión archivada.');
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    final missionProvider = context.watch<MissionProvider>();
    final missionActions = context.watch<MissionActions>();
    final profileHub = context.watch<ProfileHubProvider>();
    final professionalProfile = profileHub.activeProfessionalProfile;
    final snapshot = missionProvider.snapshot;
    final hasMission = snapshot != null;

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          _buildCommandBackground(context),
          SingleChildScrollView(
            padding: EdgeInsets.fromLTRB(
              spacings.xl,
              spacings.lg,
              spacings.xl,
              spacings.xxl,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCommandHero(
                  context,
                  snapshot: snapshot,
                  hasMission: hasMission,
                ),
                SizedBox(height: spacings.lg),
                _buildCommandTelemetry(context, snapshot),
                SizedBox(height: spacings.xl),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final compact = constraints.maxWidth < 1100;

                    if (compact) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _buildMissionStatus(context, snapshot),
                          SizedBox(height: spacings.lg),
                          _buildRuntimeHealth(context, snapshot),
                          SizedBox(height: spacings.lg),
                          _buildCareerHealth(
                            context,
                            snapshot,
                            professionalProfile,
                          ),
                          SizedBox(height: spacings.lg),
                          _buildMetricsPanel(
                            context,
                            hasMission,
                            missionActions.currentProfile,
                          ),
                          SizedBox(height: spacings.lg),
                          _buildAgentReadiness(context),
                          SizedBox(height: spacings.lg),
                          _buildActivityTimeline(context, snapshot),
                          SizedBox(height: spacings.lg),
                          _buildRoadmap(context),
                        ],
                      );
                    }

                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          flex: 34,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              _buildMissionStatus(context, snapshot),
                              SizedBox(height: spacings.lg),
                              _buildRuntimeHealth(context, snapshot),
                              SizedBox(height: spacings.lg),
                              _buildCareerHealth(
                                context,
                                snapshot,
                                professionalProfile,
                              ),
                              SizedBox(height: spacings.lg),
                              _buildRoadmap(context),
                            ],
                          ),
                        ),
                        SizedBox(width: spacings.xl),
                        Expanded(
                          flex: 66,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              _buildMetricsPanel(
                                context,
                                hasMission,
                                missionActions.currentProfile,
                              ),
                              SizedBox(height: spacings.lg),
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    child: _buildAgentReadiness(context),
                                  ),
                                  SizedBox(width: spacings.lg),
                                  Expanded(
                                    child: _buildActivityTimeline(
                                      context,
                                      snapshot,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandBackground(BuildContext context) {
    final colors = context.liaColors;

    return IgnorePointer(
      child: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  colors.background,
                  colors.background.withValues(alpha: 0.96),
                  const Color(0xFF0B1220),
                  const Color(0xFF10091A),
                ],
              ),
            ),
          ),
          Positioned(
            top: -180,
            right: -120,
            child: Container(
              width: 420,
              height: 420,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: colors.accentPrimary.withValues(alpha: 0.06),
              ),
            ),
          ),
          Positioned(
            bottom: -220,
            left: -140,
            child: Container(
              width: 500,
              height: 500,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: colors.accentTertiary.withValues(alpha: 0.045),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandHero(
    BuildContext context, {
    required dynamic snapshot,
    required bool hasMission,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final mission = snapshot?.mission;
    final status = mission?.status ?? 'STANDBY';
    final active = snapshot != null &&
        const [
          'CREATED',
          'UPLOADING',
          'STORED',
          'QUEUED',
          'PROCESSING',
          'WAITING_AGENT',
          'RUNNING',
        ].contains(status);

    final accent = status == 'FAILED'
        ? colors.error
        : active
            ? colors.accentPrimary
            : colors.success;

    return LiaGlassPanel(
      hasGlow: true,
      glowColor: accent,
      padding: EdgeInsets.all(spacings.xl),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 720;

          final identity = Row(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  color: accent.withValues(alpha: 0.12),
                  border: Border.all(color: accent.withValues(alpha: 0.35)),
                  boxShadow: [
                    BoxShadow(
                      color: accent.withValues(alpha: 0.16),
                      blurRadius: 22,
                      spreadRadius: 1,
                    ),
                  ],
                ),
                child: Icon(Icons.hub_outlined, color: accent, size: 30),
              ),
              SizedBox(width: spacings.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'LIA CAREER OS',
                      style: typography.caption.copyWith(
                        color: accent,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 2.2,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'CENTRO DE COMANDO',
                      style: typography.h2.copyWith(
                        color: colors.textPrimary,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );

          final statusCard = Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: colors.background.withValues(alpha: 0.38),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: accent.withValues(alpha: 0.22)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 9,
                  height: 9,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: accent,
                    boxShadow: [
                      BoxShadow(
                        color: accent.withValues(alpha: 0.65),
                        blurRadius: 9,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  status,
                  style: typography.caption.copyWith(
                    color: colors.textPrimary,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.2,
                  ),
                ),
              ],
            ),
          );

          final description = Text(
            hasMission
                ? 'Misión activa conectada al runtime. LIA está procesando tu trayectoria profesional.'
                : 'Tu estación de control profesional está lista. Carga tu CV para iniciar una nueva misión.',
            style: typography.bodyMedium.copyWith(
              color: colors.textSecondary,
              height: 1.45,
            ),
          );

          if (compact) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                identity,
                SizedBox(height: spacings.lg),
                statusCard,
                SizedBox(height: spacings.md),
                description,
                SizedBox(height: spacings.lg),
                if (!hasMission)
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton.icon(
                      onPressed: _pickAndUploadCV,
                      icon: const Icon(Icons.upload_file_outlined),
                      label: const Text('INICIAR ANÁLISIS'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: accent,
                        foregroundColor: colors.background,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
              ],
            );
          }

          return Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    identity,
                    SizedBox(height: spacings.md),
                    description,
                  ],
                ),
              ),
              SizedBox(width: spacings.xl),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  statusCard,
                  if (!hasMission) ...[
                    SizedBox(height: spacings.md),
                    SizedBox(
                      height: 46,
                      child: ElevatedButton.icon(
                        onPressed: _pickAndUploadCV,
                        icon: const Icon(Icons.upload_file_outlined, size: 18),
                        label: const Text('INICIAR ANÁLISIS'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: accent,
                          foregroundColor: colors.background,
                          padding: const EdgeInsets.symmetric(horizontal: 18),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCommandTelemetry(BuildContext context, dynamic snapshot) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final progress = snapshot?.progress ?? 0;
    final agents = snapshot?.runtime.activeAgents.length ?? 0;
    final events = snapshot?.timeline.length ?? 0;
    final currentStep = snapshot?.currentStep ?? 'Esperando misión';

    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 850;
        final cards = [
          _buildTelemetryCard(
            context,
            icon: Icons.track_changes,
            label: 'MISSION PROGRESS',
            value: '$progress%',
            detail: currentStep,
          ),
          _buildTelemetryCard(
            context,
            icon: Icons.smart_toy_outlined,
            label: 'ACTIVE AGENTS',
            value: '$agents',
            detail: agents == 0 ? 'Runtime en standby' : 'Agentes conectados',
          ),
          _buildTelemetryCard(
            context,
            icon: Icons.bolt_outlined,
            label: 'EVENT STREAM',
            value: '$events',
            detail: events == 0 ? 'Sin eventos todavía' : 'Eventos registrados',
          ),
        ];

        if (compact) {
          return Column(
            children: [
              cards[0],
              SizedBox(height: spacings.sm),
              cards[1],
              SizedBox(height: spacings.sm),
              cards[2],
            ],
          );
        }

        return Row(
          children: [
            Expanded(child: cards[0]),
            SizedBox(width: spacings.sm),
            Expanded(child: cards[1]),
            SizedBox(width: spacings.sm),
            Expanded(child: cards[2]),
          ],
        );
      },
    );
  }

  Widget _buildTelemetryCard(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    required String detail,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Container(
      constraints: const BoxConstraints(minHeight: 92),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.72),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: colors.border.withValues(alpha: 0.8)),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: colors.accentPrimary.withValues(alpha: 0.09),
              borderRadius: BorderRadius.circular(11),
            ),
            child: Icon(icon, color: colors.accentPrimary, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label,
                  style: typography.caption.copyWith(
                    color: colors.textMuted,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.0,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 3),
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        value,
                        style: typography.h3.copyWith(
                          color: colors.textPrimary,
                          fontWeight: FontWeight.w800,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        detail,
                        style: typography.caption.copyWith(
                          color: colors.textSecondary,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMissionStatus(BuildContext context, dynamic snapshot) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    if (snapshot == null) {
      return LiaGlassPanel(
        hasGlow: true,
        glowColor: colors.accentPrimary,
        padding: EdgeInsets.all(spacings.xxl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(Icons.rocket_launch, size: 64, color: colors.accentPrimary),
            SizedBox(height: spacings.lg),
            Text('Career OS',
                style: typography.h2.copyWith(color: colors.textPrimary)),
            SizedBox(height: spacings.sm),
            Text(
              'El centro de control de tu carrera profesional. Esperando inicialización.',
              textAlign: TextAlign.center,
              style:
                  typography.bodyMedium.copyWith(color: colors.textSecondary),
            ),
            SizedBox(height: spacings.xl),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _pickAndUploadCV,
                icon: const Icon(Icons.upload_file),
                label: const Text('SUBIR MI CV',
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colors.accentPrimary,
                  foregroundColor: colors.background,
                  shape: RoundedRectangleBorder(
                      borderRadius: spacings.radiusSm),
                  elevation: 10,
                  shadowColor: colors.accentPrimary.withValues(alpha: 0.5),
                ),
              ),
            ),
          ],
        ),
      );
    }

    final mission = snapshot.mission;
    final lastEvent = snapshot.timeline.isNotEmpty
        ? (snapshot.timeline.last.userMessage ?? snapshot.timeline.last.title)
        : 'Iniciando...';

    final activeStatuses = const [
      'CREATED', 'UPLOADING', 'STORED', 'QUEUED',
      'PROCESSING', 'WAITING_AGENT', 'RUNNING'
    ];
    final isRunning = activeStatuses.contains(mission.status);
    final isFailed = mission.status == 'FAILED';

    final Color glowColor = isFailed
        ? colors.error
        : (isRunning ? colors.accentPrimary : colors.success);

    return LiaGlassPanel(
      hasGlow: true,
      glowColor: glowColor,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('MISSION STATUS',
                  style: typography.caption.copyWith(color: glowColor)),
              LiaStatusIndicator(
                  color: glowColor,
                  label: mission.status,
                  isPulsing: isRunning),
            ],
          ),
          SizedBox(height: spacings.md),
          Text(mission.currentStep,
              style: typography.h3.copyWith(color: colors.textPrimary)),
          SizedBox(height: spacings.sm),
          Text(
            lastEvent,
            style: typography.bodyMedium.copyWith(color: colors.textSecondary),
          ),
          if (isFailed && snapshot.availableActions.isNotEmpty) ...[
            SizedBox(height: spacings.lg),
            Row(
              children: [
                if (snapshot.availableActions.contains('RESTART'))
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _pickAndUploadCV,
                      icon: const Icon(Icons.refresh, size: 16),
                      label: const Text('SUBIR NUEVO CV'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF3B82F6),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                if (snapshot.availableActions.contains('RESTART') &&
                    snapshot.availableActions.contains('RESUME'))
                  SizedBox(width: spacings.sm),
                if (snapshot.availableActions.contains('RESUME'))
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        await context.read<MissionActions>().resumeMission();
                      },
                      icon: const Icon(Icons.play_arrow, size: 16),
                      label: const Text('REINTENTAR'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: colors.accentPrimary,
                        foregroundColor: colors.background,
                      ),
                    ),
                  ),
              ],
            ),
          ]
        ],
      ),
    );
  }

  Widget _buildRuntimeHealth(BuildContext context, dynamic snapshot) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    if (snapshot == null) {
      return const SizedBox.shrink();
    }

    final health = snapshot.health;
    final runtime = snapshot.runtime;

    return LiaGlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('SYSTEM & RUNTIME HEALTH',
              style: typography.caption.copyWith(color: colors.textMuted)),
          SizedBox(height: spacings.md),
          _buildHealthRow(context, 'Mission Runtime', runtime.online),
          SizedBox(height: spacings.sm),
          _buildHealthRow(context, 'Database', health.database),
          SizedBox(height: spacings.sm),
          _buildHealthRow(context, 'Storage', health.storage),
          Divider(color: colors.border, height: spacings.xl),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Versión',
                  style: typography.bodyMedium
                      .copyWith(color: colors.textSecondary)),
              Text(health.version,
                  style: typography.bodyMedium.copyWith(
                      color: colors.textPrimary,
                      fontFamily: 'monospace')),
            ],
          ),
          SizedBox(height: spacings.xs),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Agentes Activos',
                  style: typography.bodyMedium
                      .copyWith(color: colors.textSecondary)),
              Text('${runtime.activeAgents.length}',
                  style: typography.bodyMedium.copyWith(
                      color: colors.textPrimary,
                      fontFamily: 'monospace')),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHealthRow(
      BuildContext context, String label, bool isOnline) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Flexible(
          child: Text(
            label,
            style:
                typography.bodyMedium.copyWith(color: colors.textSecondary),
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 8),
        LiaStatusIndicator(
          color: isOnline ? colors.accentPrimary : colors.error,
          label: isOnline ? 'ONLINE' : 'OFF',
        ),
      ],
    );
  }

  Widget _buildCareerHealth(
    BuildContext context,
    dynamic snapshot,
    dynamic profile,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final isFailed = snapshot?.mission.status == 'FAILED';
    final missionProgress =
        snapshot != null ? snapshot.progress.toDouble() / 100 : 0.0;

    final career = profile?.careerMetrics;
    final level = career?.employabilityLevel?.toString().trim() ?? '';
    final careerScore = _careerVisualScore(level.toLowerCase());
    final hasCareerScore = profile != null && career != null;

    final Color missionBarColor =
        isFailed ? colors.error : colors.accentPrimary;

    return LiaGlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('CAREER HEALTH',
              style: typography.caption.copyWith(color: colors.textMuted)),
          SizedBox(height: spacings.md),
          LiaProgressBar(
            progress: hasCareerScore ? careerScore / 100.0 : 0.0,
            color: colors.accentTertiary,
            label: 'Score General',
            trailingText: hasCareerScore
                ? '$careerScore'
                : 'Esperando perfil profesional',
          ),
          SizedBox(height: spacings.lg),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('MISSION PROGRESS',
                  style: typography.caption.copyWith(color: colors.textMuted)),
              if (isFailed)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: colors.error.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                        color: colors.error.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.stop_circle_outlined,
                          color: colors.error, size: 12),
                      const SizedBox(width: 4),
                      Text(
                        'DETENIDO',
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.8,
                          color: colors.error,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          SizedBox(height: spacings.md),

          _buildMissionProgressBar(
            context,
            progress: missionProgress,
            color: missionBarColor,
            isFailed: isFailed,
            snapshot: snapshot,
          ),

          if (isFailed) ...[
            SizedBox(height: spacings.sm),
            Row(
              children: [
                Icon(Icons.info_outline, size: 13, color: colors.error),
                const SizedBox(width: 6),
                Text(
                  'Proceso detenido en ${(missionProgress * 100).toInt()}%',
                  style: typography.bodyMedium.copyWith(
                    color: colors.error.withValues(alpha: 0.8),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  int _careerVisualScore(String level) {
    switch (level) {
      case 'high':
        return 100;
      case 'medium':
        return 60;
      case 'low':
        return 30;
      default:
        return 0;
    }
  }

  Widget _buildMissionProgressBar(
    BuildContext context, {
    required double progress,
    required Color color,
    required bool isFailed,
    required dynamic snapshot,
  }) {
    final typography = context.liaTypography;

    if (!isFailed) {
      return LiaProgressBar(
        progress: progress,
        color: color,
        label: 'Ejecución de Misión',
        trailingText: snapshot != null
            ? '${(progress * 100).toInt()}%'
            : 'Esperando primera misión',
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Ejecución de Misión',
                style: typography.bodyMedium
                    .copyWith(color: context.liaColors.textSecondary)),
            Text(
              '${(progress * 100).toInt()}%',
              style: typography.bodyMedium
                  .copyWith(color: color, fontWeight: FontWeight.w600),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: SizedBox(
            height: 8,
            child: Stack(
              children: [
                Container(
                  color: color.withValues(alpha: 0.12),
                ),
                FractionallySizedBox(
                  widthFactor: progress.clamp(0.0, 1.0),
                  child: Container(
                    decoration: BoxDecoration(
                      color: color,
                      boxShadow: [
                        BoxShadow(
                          color: color.withValues(alpha: 0.5),
                          blurRadius: 6,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRoadmap(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaGlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('ROADMAP',
              style: typography.caption.copyWith(color: colors.textMuted)),
          SizedBox(height: spacings.md),
          _buildRoadmapItem(context, 'Fase 1: Engine', true, true),
          _buildRoadmapItem(context, 'Fase 2: Conexión Real', true, true),
          _buildRoadmapItem(context, 'Fase 3: IA & Agents', false, true),
          _buildRoadmapItem(context, 'Fase 4: Multi-Agent Comms', false, false),
        ],
      ),
    );
  }

  Widget _buildRoadmapItem(
      BuildContext context, String title, bool isCompleted, bool hasLine) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 4),
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                    color: isCompleted ? colors.accentPrimary : colors.border,
                    width: 2),
                color: isCompleted
                    ? colors.accentPrimary.withValues(alpha: 0.2)
                    : Colors.transparent,
              ),
            ),
            if (hasLine)
              Container(
                width: 2,
                height: 24,
                color: isCompleted
                    ? colors.accentPrimary.withValues(alpha: 0.5)
                    : colors.border,
              ),
          ],
        ),
        SizedBox(width: spacings.md),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(
              title,
              style: typography.bodyMedium.copyWith(
                color: isCompleted ? colors.textPrimary : colors.textMuted,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricsPanel(BuildContext context, bool hasMission, dynamic profile) {
    final spacings = context.liaSpacings;

    String? atsScore;
    String? linkedinScore;
    String? jobMatch;
    String? skillsCoverage;
    String? execScore;

    if (profile != null) {
      atsScore = '${profile.atsMetrics.atsScore}/100';
      linkedinScore = '${profile.linkedinMetrics.score}/100';
      jobMatch = profile.careerMetrics.employabilityLevel;
      skillsCoverage = '${profile.skills.technicalSkills.length} skills';
      execScore = profile.cvScore != null ? '${profile.cvScore}/100' : 'N/A';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('PANEL DE MÉTRICAS',
            style: context.liaTypography.caption
                .copyWith(color: context.liaColors.textMuted)),
        SizedBox(height: spacings.sm),
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                  child:
                      LiaMetric(title: 'ATS Score', value: atsScore, icon: Icons.document_scanner)),
              SizedBox(width: spacings.md),
              Expanded(
                  child: LiaMetric(
                      title: 'LinkedIn Score', value: linkedinScore, icon: Icons.work_outline)),
              SizedBox(width: spacings.md),
              Expanded(
                  child:
                      LiaMetric(title: 'Job Match', value: jobMatch, icon: Icons.pie_chart_outline)),
              SizedBox(width: spacings.md),
              Expanded(
                  child: LiaMetric(
                      title: 'Skills Coverage',
                      value: skillsCoverage,
                      icon: Icons.psychology_outlined)),
              SizedBox(width: spacings.md),
              Expanded(
                  child: LiaMetric(
                      title: 'CV Score', value: execScore, icon: Icons.star_border)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAgentReadiness(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    final snapshot = context.watch<MissionProvider>().snapshot;

    final agents = [
      'Career Agent',
      'CV Expert',
      'ATS Analyzer',
      'Job Hunter',
      'LinkedIn Optimizer',
      'Cover Letter AI',
      'Interview Coach',
      'Negotiation Coach'
    ];

    String normalizeName(String value) {
      return value.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
    }

    String backendNameFor(String uiName) {
      switch (uiName) {
        case 'Cover Letter AI':
          return 'Cover Letter Generator';
        default:
          return uiName;
      }
    }

    dynamic findAgentStatus(String uiName) {
      if (snapshot == null) return null;

      final target = normalizeName(backendNameFor(uiName));
      for (final agentStatus in snapshot.agentStatuses) {
        if (normalizeName(agentStatus.name) == target) {
          return agentStatus;
        }
      }
      return null;
    }

    String displayStatus(dynamic agentStatus) {
      if (agentStatus == null) return 'N/A';

      final status = agentStatus.status.toString().trim().toUpperCase();
      switch (status) {
        case 'COMPLETED':
        case 'SUCCESS':
        case 'READY':
          return 'READY';
        case 'RUNNING':
          return 'RUNNING';
        case 'SKIPPED':
          return 'SKIPPED';
        case 'ERROR':
        case 'FAILED':
          return 'ERROR';
        case '':
          return 'N/A';
        default:
          return status;
      }
    }

    Color statusColor(String status) {
      switch (status) {
        case 'READY':
          return colors.success;
        case 'RUNNING':
          return colors.accentPrimary;
        case 'ERROR':
          return colors.error;
        case 'SKIPPED':
        case 'N/A':
          return colors.textMuted;
        default:
          return colors.textSecondary;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('AGENT READINESS',
            style: typography.caption.copyWith(color: colors.textMuted)),
        SizedBox(height: spacings.sm),
        LiaGlassPanel(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: agents.map((agent) {
              final status = displayStatus(findAgentStatus(agent));
              return Padding(
                padding: EdgeInsets.only(
                    bottom: agent == agents.last ? 0 : spacings.sm),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Flexible(
                      child: Text(
                        agent,
                        style: typography.bodyMedium.copyWith(
                          color: colors.textPrimary,
                          fontFamily: 'monospace',
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    LiaStatusIndicator(
                      color: statusColor(status),
                      label: status,
                      isPulsing: status == 'RUNNING',
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildActivityTimeline(BuildContext context, dynamic snapshot) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('ACTIVIDAD DEL SISTEMA',
            style: typography.caption.copyWith(color: colors.textMuted)),
        SizedBox(height: spacings.sm),
        if (snapshot == null || snapshot.timeline.isEmpty)
          LiaTimeline(
            items: [
              LiaTimelineItem(
                  text: 'Sistema iniciado correctamente.', isCompleted: true),
              LiaTimelineItem(
                  text: 'Mission Runtime listo.', isCompleted: true),
              LiaTimelineItem(
                  text: 'Esperando primera misión.', isCompleted: false),
            ],
          )
        else
          LiaTimeline(
            items: (snapshot.timeline as List).map<LiaTimelineItem>((event) {
              final severity =
                  event.severity.toString().trim().toLowerCase();
              final isError =
                  severity == 'error' || severity == 'critical';
              final isCompleted =
                  severity == 'info' || severity == 'success';

              return LiaTimelineItem(
                text: event.title,
                isCompleted: isCompleted,
                stage: event.stage,
                userMessage: event.userMessage,
                developerMessage: event.developerMessage,
                duration: event.duration ?? 0,
                isError: isError,
              );
            }).toList(),
          )
      ],
    );
  }
}
