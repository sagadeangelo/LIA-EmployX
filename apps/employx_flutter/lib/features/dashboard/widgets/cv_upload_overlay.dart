import 'dart:ui';
import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/providers/upload_provider.dart';
import '../../../core/providers/mission_provider.dart';
import '../../../core/models/mission_event_model.dart';
import 'neon_progress_bar.dart';

/// Callbacks that the Overlay exposes — all business logic lives in the parent.
///
/// [onRetry]   → Resume the current failed mission (backend decides if possible).
/// [onPickNew] → Pick a new CV file; the parent handles FilePicke + new mission.
/// [onClose]   → Close/hide the overlay; parent handles cleanup.
typedef OverlayRetryCallback = void Function();
typedef OverlayPickNewCallback = void Function();
typedef OverlayCloseCallback = void Function();

class CVUploadOverlay extends StatefulWidget {
  final VoidCallback onComplete;
  final OverlayRetryCallback onRetry;
  final OverlayPickNewCallback onPickNew;
  final OverlayCloseCallback onClose;

  const CVUploadOverlay({
    Key? key,
    required this.onComplete,
    required this.onRetry,
    required this.onPickNew,
    required this.onClose,
  }) : super(key: key);

  static void show(
    BuildContext context, {
    required OverlayRetryCallback onRetry,
    required OverlayPickNewCallback onPickNew,
    required OverlayCloseCallback onClose,
  }) {
    showGeneralDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.5),
      transitionDuration: const Duration(milliseconds: 400),
      pageBuilder: (ctx, animation, secondaryAnimation) {
        return CVUploadOverlay(
          onComplete: () => Navigator.of(ctx).pop(),
          onRetry: onRetry,
          onPickNew: onPickNew,
          onClose: () {
            onClose();
            Navigator.of(ctx).pop();
          },
        );
      },
      transitionBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: CurvedAnimation(parent: animation, curve: Curves.easeOut),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
            child: child,
          ),
        );
      },
    );
  }

  @override
  State<CVUploadOverlay> createState() => _CVUploadOverlayState();
}

class _CVUploadOverlayState extends State<CVUploadOverlay>
    with TickerProviderStateMixin {
  late AnimationController _successController;
  late AnimationController _fadeController;
  late AnimationController _errorShakeController;

  @override
  void initState() {
    super.initState();
    _successController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
      value: 1.0,
    );
    _errorShakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
  }

  @override
  void dispose() {
    _successController.dispose();
    _fadeController.dispose();
    _errorShakeController.dispose();
    super.dispose();
  }

  void _checkCompletion(
      UploadProvider uploadProvider, MissionProvider missionProvider) {
    final snapshot = missionProvider.snapshot;

    if (snapshot != null &&
        uploadProvider.currentPhase == UploadPhase.analysis &&
        !uploadProvider.isCompleted &&
        !uploadProvider.hasError) {
      final stepStr = snapshot.mission.currentStep;
      uploadProvider.updateAnalysisStep(stepStr);

      if (snapshot.mission.status == 'COMPLETED' ||
          snapshot.mission.status == 'WAITING_AGENT' ||
          stepStr == 'COMPLETE') {
        uploadProvider.completeProcess();
      } else if (snapshot.mission.status == 'FAILED') {
        // Extract user-friendly error from the timeline
        String userMessage = 'No pudimos procesar tu CV. Por favor intenta nuevamente.';
        try {
          final failedEvent = snapshot.timeline
              .lastWhere((e) => e.severity == 'error');
          userMessage = failedEvent.userMessage ?? userMessage;
        } catch (_) {
          // No error event found; use default message
        }
        uploadProvider.setError(userMessage);
        // Trigger shake animation when error first appears
        _errorShakeController.forward(from: 0);
      }
    }

    if (uploadProvider.isCompleted) {
      if (!_successController.isAnimating && !_successController.isCompleted) {
        _successController.forward().then((_) {
          Future.delayed(const Duration(seconds: 1), () {
            if (mounted) {
              _fadeController.reverse().then((_) {
                if (mounted) widget.onComplete();
              });
            }
          });
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final uploadProvider = context.watch<UploadProvider>();
    final missionProvider = context.watch<MissionProvider>();

    // Auto-check completion every rebuild (post-frame to avoid setState during build)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkCompletion(uploadProvider, missionProvider);
    });

    final isSuccess = uploadProvider.isCompleted;
    final hasError = uploadProvider.hasError;

    // Border and glow color driven purely by real state
    final Color accentColor = hasError
        ? const Color(0xFFEF4444)   // Red on error
        : isSuccess
            ? const Color(0xFF00FF8B) // Green on success
            : const Color(0xFF8A2BE2); // Purple during progress

    return FadeTransition(
      opacity: _fadeController,
      child: Center(
        child: Material(
          color: Colors.transparent,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 600),
            curve: Curves.easeInOutBack,
            width: 750,
            padding: const EdgeInsets.all(40),
            decoration: BoxDecoration(
              color: const Color(0xFF0B0F1A).withOpacity(0.90),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: accentColor.withOpacity(0.5),
                width: 1.5,
              ),
              boxShadow: [
                BoxShadow(
                  color: accentColor.withOpacity(0.18),
                  blurRadius: 50,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxHeight: MediaQuery.of(context).size.height * 0.85,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHeader(uploadProvider),
                    const SizedBox(height: 32),

                    if (hasError) ...[
                      _buildErrorScreen(uploadProvider, missionProvider),
                    ] else if (!isSuccess) ...[
                      _buildFileDetails(uploadProvider),
                      const SizedBox(height: 32),

                      NeonProgressBar(
                        progress: uploadProvider.currentPhase ==
                                UploadPhase.transfer
                            ? uploadProvider.transferProgress
                            : uploadProvider.analysisProgress,
                        phase: uploadProvider.currentPhase,
                        centerText:
                            uploadProvider.currentPhase == UploadPhase.analysis
                                ? _getAnalysisMainText(
                                    uploadProvider.missionStage)
                                : null,
                      ),

                      const SizedBox(height: 24),

                      AnimatedSize(
                        duration: const Duration(milliseconds: 400),
                        child: uploadProvider.currentPhase ==
                                UploadPhase.transfer
                            ? _buildUploadStats(uploadProvider)
                            : const SizedBox.shrink(),
                      ),

                      const SizedBox(height: 32),
                      _buildStepsArea(uploadProvider),
                      const SizedBox(height: 32),

                      const DynamicTip(),
                    ] else ...[
                      _buildSuccessMessage(uploadProvider),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Header
  // ---------------------------------------------------------------------------

  Widget _buildHeader(UploadProvider provider) {
    final hasError = provider.hasError;

    final String label;
    final Color labelColor;
    final String subtitle;

    if (hasError) {
      label = 'ERROR EN EL PROCESAMIENTO';
      labelColor = const Color(0xFFEF4444);
      subtitle = 'El proceso fue detenido. Selecciona una acción para continuar.';
    } else if (provider.currentPhase == UploadPhase.transfer) {
      label = 'FASE 1: TRANSFERENCIA';
      labelColor = const Color(0xFF3B82F6);
      subtitle = 'Subiendo documento al ecosistema seguro.';
    } else {
      label = 'FASE 2: ANÁLISIS INTELIGENTE';
      labelColor = const Color(0xFF8A2BE2);
      subtitle = 'El Mission Runtime está construyendo tu perfil.';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            letterSpacing: 2.0,
            color: labelColor,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: GoogleFonts.inter(
            fontSize: 14,
            color: Colors.grey.shade400,
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // Error Screen — the key piece of this refactor
  // ---------------------------------------------------------------------------

  Widget _buildErrorScreen(
      UploadProvider uploadProvider, MissionProvider missionProvider) {
    final snapshot = missionProvider.snapshot;

    // Find the last error event for technical details
    MissionEventModel? failedEvent;
    try {
      failedEvent =
          snapshot?.timeline.lastWhere((e) => e.severity == 'error');
    } catch (_) {
      failedEvent = null;
    }

    final String devMessage =
        [failedEvent?.developerMessage, failedEvent?.logs]
            .where((s) => s != null && s.isNotEmpty)
            .join('\n\n');

    // retryMode comes from the backend — Flutter never decides this
    final String retryMode = snapshot?.retryMode ?? 'NONE';
    final bool canResume = retryMode == 'RESUME_ALLOWED';

    return Column(
      children: [
        // --- Error Icon (animated shake) ---
        AnimatedBuilder(
          animation: _errorShakeController,
          builder: (context, child) {
            final shake = sin(_errorShakeController.value * 3 * pi) * 8;
            return Transform.translate(
              offset: Offset(shake, 0),
              child: child,
            );
          },
          child: Container(
            padding: const EdgeInsets.all(28),
            decoration: BoxDecoration(
              color: const Color(0xFFEF4444).withOpacity(0.1),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFEF4444).withOpacity(0.2),
                  blurRadius: 40,
                  spreadRadius: 8,
                ),
              ],
            ),
            child: const Icon(
              Icons.error_outline_rounded,
              color: Color(0xFFEF4444),
              size: 80,
            ),
          ),
        ),

        const SizedBox(height: 28),

        // --- User-friendly error title ---
        Text(
          'No pudimos procesar tu CV',
          style: GoogleFonts.inter(
            fontSize: 26,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            letterSpacing: 0.3,
          ),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 12),

        // --- User-friendly error message (from backend's userMessage) ---
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          decoration: BoxDecoration(
            color: const Color(0xFFEF4444).withOpacity(0.07),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: const Color(0xFFEF4444).withOpacity(0.2),
            ),
          ),
          child: Text(
            uploadProvider.errorMessage.isNotEmpty
                ? uploadProvider.errorMessage
                : 'Ocurrió un error inesperado durante el análisis.',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 15,
              color: Colors.grey.shade300,
              height: 1.6,
            ),
          ),
        ),

        // --- Technical details (collapsed by default) ---
        if (devMessage.isNotEmpty) ...[
          const SizedBox(height: 16),
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              title: Row(
                children: [
                  Icon(Icons.bug_report_outlined,
                      color: Colors.grey.shade500, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    'Ver detalles técnicos',
                    style: GoogleFonts.inter(
                        color: Colors.grey.shade500, fontSize: 13),
                  ),
                ],
              ),
              iconColor: Colors.grey.shade500,
              collapsedIconColor: Colors.grey.shade600,
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                        color: const Color(0xFFEF4444).withOpacity(0.15)),
                  ),
                  child: SelectableText(
                    devMessage,
                    style: GoogleFonts.firaCode(
                        fontSize: 11,
                        color: const Color(0xFFFF8A80),
                        height: 1.6),
                  ),
                ),
              ],
            ),
          ),
        ],

        const SizedBox(height: 36),

        // --- Action Buttons (always present regardless of availableActions) ---
        Column(
          children: [
            // Primary row: Reintentar + Seleccionar otro CV
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Reintentar — enabled only when backend says RESUME_ALLOWED
                Expanded(
                  child: Opacity(
                    opacity: canResume ? 1.0 : 0.4,
                    child: ElevatedButton.icon(
                      onPressed: canResume ? widget.onRetry : null,
                      icon: const Icon(Icons.play_arrow_rounded, size: 20),
                      label: Text(
                        'Reintentar',
                        style: GoogleFonts.inter(
                            fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        foregroundColor: Colors.white,
                        disabledBackgroundColor:
                            const Color(0xFF10B981).withOpacity(0.3),
                        disabledForegroundColor: Colors.grey.shade400,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 16),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Seleccionar otro CV — always enabled
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: widget.onPickNew,
                    icon: const Icon(Icons.upload_file_rounded, size: 20),
                    label: Text(
                      'Seleccionar otro CV',
                      style: GoogleFonts.inter(
                          fontWeight: FontWeight.w600, fontSize: 14),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3B82F6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Secondary: Cerrar
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: widget.onClose,
                icon: Icon(Icons.close_rounded,
                    size: 18, color: Colors.grey.shade400),
                label: Text(
                  'Cerrar',
                  style: GoogleFonts.inter(
                      color: Colors.grey.shade400,
                      fontWeight: FontWeight.w500,
                      fontSize: 14),
                ),
                style: OutlinedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  side:
                      BorderSide(color: Colors.grey.shade700.withOpacity(0.5)),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),

        // Tooltip explaining Reintentar is disabled when not applicable
        if (!canResume) ...[
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.info_outline,
                  size: 14, color: Colors.grey.shade600),
              const SizedBox(width: 6),
              Text(
                'Reintentar no disponible: el archivo debe subirse nuevamente.',
                style: GoogleFonts.inter(
                    fontSize: 12, color: Colors.grey.shade600),
              ),
            ],
          ),
        ],
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // Success Screen
  // ---------------------------------------------------------------------------

  Widget _buildSuccessMessage(UploadProvider provider) {
    final timeTaken = provider.totalTime.inSeconds;
    return FadeTransition(
      opacity: _successController,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                color: const Color(0xFF00FF8B).withOpacity(0.1),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF00FF8B).withOpacity(0.2),
                    blurRadius: 40,
                    spreadRadius: 10,
                  )
                ],
              ),
              child: const Icon(
                Icons.check_circle_outline,
                color: Color(0xFF00FF8B),
                size: 96,
              ),
            ),
            const SizedBox(height: 32),
            Text(
              'Misión Creada Exitosamente',
              style: GoogleFonts.inter(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Perfil profesional construido en $timeTaken segundos.\nRedirigiendo al espacio de trabajo...',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 16,
                color: Colors.grey.shade400,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // Progress UI helpers
  // ---------------------------------------------------------------------------

  String _getAnalysisMainText(MissionStage step) {
    switch (step) {
      case MissionStage.receiveFile:
        return 'Recibiendo...';
      case MissionStage.storeFile:
        return 'Almacenando...';
      case MissionStage.detectFormat:
        return 'Detectando formato...';
      case MissionStage.readDocument:
        return 'Leyendo documento...';
      case MissionStage.extractText:
        return 'Extrayendo texto...';
      case MissionStage.normalizeText:
        return 'Normalizando texto...';
      case MissionStage.buildProfile:
        return 'Construyendo perfil...';
      case MissionStage.saveProfile:
        return 'Guardando perfil...';
      case MissionStage.updateRuntime:
        return 'Iniciando agente...';
      case MissionStage.complete:
        return 'Finalizando...';
    }
  }

  Widget _buildFileDetails(UploadProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF8A2BE2).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.description_outlined,
              color: Color(0xFF8A2BE2),
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  provider.fileName.isEmpty
                      ? 'Seleccionando archivo...'
                      : provider.fileName,
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  provider.fileSize > 0
                      ? '${(provider.fileSize / (1024 * 1024)).toStringAsFixed(2)} MB'
                      : 'Calculando...',
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    color: Colors.grey.shade400,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUploadStats(UploadProvider provider) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _buildStatItem(
          icon: Icons.speed,
          label: 'Velocidad de subida',
          value: provider.speedMBps > 0
              ? '${provider.speedMBps.toStringAsFixed(1)} MB/s'
              : '-- MB/s',
        ),
        _buildStatItem(
          icon: Icons.timer_outlined,
          label: 'Tiempo restante',
          value: provider.eta.inSeconds > 0
              ? '${provider.eta.inMinutes.toString().padLeft(2, '0')}:${(provider.eta.inSeconds % 60).toString().padLeft(2, '0')}'
              : '--:--',
        ),
      ],
    );
  }

  Widget _buildStatItem(
      {required IconData icon, required String label, required String value}) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFF3B82F6), size: 20),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: GoogleFonts.inter(
                fontSize: 12,
                color: Colors.grey.shade500,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStepsArea(UploadProvider provider) {
    return AnimatedSize(
      duration: const Duration(milliseconds: 500),
      curve: Curves.easeInOut,
      alignment: Alignment.topCenter,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (provider.currentPhase == UploadPhase.analysis) ...[
            // Collapsed Phase 1
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF00FF8B).withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                    color: const Color(0xFF00FF8B).withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle,
                      color: Color(0xFF00FF8B), size: 20),
                  const SizedBox(width: 12),
                  Text(
                    'Subida completada exitosamente',
                    style: GoogleFonts.inter(
                        color: Colors.white, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            _buildAnalysisSteps(provider),
          ] else ...[
            _buildTransferSteps(provider),
          ]
        ],
      ),
    );
  }

  Widget _buildTransferSteps(UploadProvider provider) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _buildStepChip('Preparando', TransferStep.preparing,
            provider.transferStep, Icons.settings_outlined),
        _buildStepDivider(),
        _buildStepChip('Subiendo', TransferStep.uploading, provider.transferStep,
            Icons.cloud_upload_outlined),
        _buildStepDivider(),
        _buildStepChip('Verificando', TransferStep.verifying,
            provider.transferStep, Icons.security_outlined),
      ],
    );
  }

  Widget _buildAnalysisSteps(UploadProvider provider) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildAnalysisChip('Recibir', MissionStage.receiveFile,
                provider.missionStage, Icons.download_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Guardar', MissionStage.storeFile,
                provider.missionStage, Icons.save_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Formato', MissionStage.detectFormat,
                provider.missionStage, Icons.find_in_page_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Lectura', MissionStage.readDocument,
                provider.missionStage, Icons.document_scanner_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Texto', MissionStage.extractText,
                provider.missionStage, Icons.text_snippet_outlined),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildAnalysisChip('Normalizar', MissionStage.normalizeText,
                provider.missionStage, Icons.spellcheck),
            _buildStepDivider(),
            _buildAnalysisChip('Perfil', MissionStage.buildProfile,
                provider.missionStage, Icons.person_outline),
            _buildStepDivider(),
            _buildAnalysisChip('Guardar Perf.', MissionStage.saveProfile,
                provider.missionStage, Icons.save_alt_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Runtime', MissionStage.updateRuntime,
                provider.missionStage, Icons.memory_outlined),
            _buildStepDivider(),
            _buildAnalysisChip('Listo', MissionStage.complete,
                provider.missionStage, Icons.check_circle_outline),
          ],
        ),
      ],
    );
  }

  Widget _buildStepDivider() {
    return Expanded(
      child: Container(
        height: 1,
        color: Colors.white.withOpacity(0.1),
      ),
    );
  }

  Widget _buildStepChip(
      String label, Enum step, Enum currentStep, IconData icon) {
    final bool isCompleted = step.index < currentStep.index;
    final bool isActive = step == currentStep;

    Color color;
    if (isActive) {
      color = const Color(0xFF06D6A0);
    } else if (isCompleted) {
      color = const Color(0xFF8A2BE2);
    } else {
      color = Colors.grey.shade700;
    }

    return AnimatedContainer(
      duration: const Duration(milliseconds: 400),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isActive ? color.withOpacity(0.15) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isActive
              ? color.withOpacity(0.6)
              : (isCompleted
                  ? color.withOpacity(0.3)
                  : Colors.white.withOpacity(0.05)),
        ),
        boxShadow: isActive
            ? [
                BoxShadow(
                  color: color.withOpacity(0.25),
                  blurRadius: 15,
                  spreadRadius: 2,
                )
              ]
            : null,
      ),
      child: Column(
        children: [
          Icon(
            isCompleted ? Icons.check_circle : icon,
            color: color,
            size: 24,
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
              color: isActive || isCompleted ? Colors.white : Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisChip(
      String label, MissionStage step, MissionStage currentStep, IconData icon) {
    return Expanded(
      flex: 3,
      child: _buildStepChip(label, step, currentStep, icon),
    );
  }
}

// ---------------------------------------------------------------------------
// MissionEventModel reference (imported from core)
// ---------------------------------------------------------------------------
// This import is local — the file already imports mission_provider which
// exposes MissionSnapshotModel → MissionEventModel.
// We re-use the type directly since MissionProvider is already in scope.

// ---------------------------------------------------------------------------
// DynamicTip Widget
// ---------------------------------------------------------------------------

class DynamicTip extends StatefulWidget {
  const DynamicTip({Key? key}) : super(key: key);

  @override
  State<DynamicTip> createState() => _DynamicTipState();
}

class _DynamicTipState extends State<DynamicTip> {
  final List<String> _tips = [
    "Un CV bien estructurado mejora el análisis automático.",
    "Detectaremos tus habilidades técnicas y blandas ocultas.",
    "Toda la información se procesa localmente en el servidor.",
    "El sistema generará un perfil profesional unificado.",
    "El parser identificará la mejor ruta profesional para ti.",
  ];
  int _currentIndex = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _currentIndex = Random().nextInt(_tips.length);
    _timer = Timer.periodic(const Duration(seconds: 4), (timer) {
      setState(() {
        _currentIndex = (_currentIndex + 1) % _tips.length;
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF3B82F6).withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF3B82F6).withOpacity(0.1)),
      ),
      child: Row(
        children: [
          const Icon(Icons.lightbulb_outline,
              color: Color(0xFF3B82F6), size: 24),
          const SizedBox(width: 16),
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 500),
              child: Text(
                _tips[_currentIndex],
                key: ValueKey<int>(_currentIndex),
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: Colors.grey.shade300,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
