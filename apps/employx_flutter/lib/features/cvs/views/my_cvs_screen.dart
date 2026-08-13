import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';

import '../../../core/actions/mission_actions.dart';
import '../../../core/providers/upload_provider.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_button.dart';
import '../../../core/ui/lia_card.dart';
import '../../../core/utils/app_logger.dart';

import '../../profile/models/cv_document.dart';
import '../../profile/providers/profile_hub_provider.dart';

class MyCvsScreen extends StatefulWidget {
  const MyCvsScreen({super.key});

  @override
  State<MyCvsScreen> createState() => _MyCvsScreenState();
}

class _MyCvsScreenState extends State<MyCvsScreen> {
  bool _isUploading = false;

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Consumer<ProfileHubProvider>(
        builder: (
          context,
          profileHub,
          _,
        ) {
          final cvs = profileHub.cvs;
          final activeCv = profileHub.activeCv;

          return Stack(
            children: [
              SingleChildScrollView(
                padding: EdgeInsets.all(
                  spacings.xl,
                ),
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    _buildHeader(
                      context,
                      profileHub,
                    ),
                    SizedBox(
                      height: spacings.xxl,
                    ),
                    if (cvs.isEmpty)
                      _buildEmptyState(context)
                    else
                      _buildCvSection(
                        context,
                        cvs,
                        activeCv,
                      ),
                  ],
                ),
              ),
              if (_isUploading)
                _buildUploadingOverlay(context),
            ],
          );
        },
      ),
    );
  }

  // ============================================================
  // HEADER
  // ============================================================

  Widget _buildHeader(
    BuildContext context,
    ProfileHubProvider profileHub,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Row(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                'Mis CVs',
                style: typography.h2.copyWith(
                  color: colors.textPrimary,
                ),
              ),
              SizedBox(
                height: spacings.xs,
              ),
              Text(
                profileHub.hasCvs
                    ? 'Administra tus diferentes perfiles profesionales.'
                    : 'Crea y administra tus diferentes perfiles profesionales.',
                style:
                    typography.bodyMedium.copyWith(
                  color: colors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        SizedBox(
          width: spacings.md,
        ),
        LiaButton(
          text: 'Nuevo CV',
          icon: Icons.add,
          onPressed: _isUploading
              ? null
              : () => _pickAndUploadCv(context),
        ),
      ],
    );
  }

  // ============================================================
  // CV SECTION
  // ============================================================

  Widget _buildCvSection(
    BuildContext context,
    List<CVDocument> cvs,
    CVDocument? activeCv,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        if (activeCv != null) ...[
          Text(
            'CV activo',
            style: typography.h3.copyWith(
              color: colors.textPrimary,
            ),
          ),
          SizedBox(
            height: spacings.md,
          ),
          _buildActiveCvCard(
            context,
            activeCv,
          ),
          SizedBox(
            height: spacings.xxl,
          ),
        ],
        Text(
          'Todos tus CVs',
          style: typography.h3.copyWith(
            color: colors.textPrimary,
          ),
        ),
        SizedBox(
          height: spacings.md,
        ),
        LayoutBuilder(
          builder: (
            context,
            constraints,
          ) {
            final width = constraints.maxWidth;

            final crossAxisCount = width >= 1200
                ? 3
                : width >= 750
                    ? 2
                    : 1;

            return GridView.builder(
              shrinkWrap: true,
              physics:
                  const NeverScrollableScrollPhysics(),
              gridDelegate:
                  SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount:
                    crossAxisCount,
                crossAxisSpacing:
                    spacings.lg,
                mainAxisSpacing:
                    spacings.lg,
                childAspectRatio:
                    crossAxisCount == 1
                        ? 3.0
                        : 1.45,
              ),
              itemCount: cvs.length,
              itemBuilder: (
                context,
                index,
              ) {
                return _buildCvCard(
                  context,
                  cvs[index],
                );
              },
            );
          },
        ),
      ],
    );
  }

  // ============================================================
  // ACTIVE CV CARD
  // ============================================================

  Widget _buildActiveCvCard(
    BuildContext context,
    CVDocument cv,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaCard(
      isHoverable: false,
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color:
                  colors.accentPrimary.withValues(
                alpha: 0.12,
              ),
              borderRadius:
                  BorderRadius.circular(14),
            ),
            child: Icon(
              Icons.description_outlined,
              color: colors.accentPrimary,
              size: 28,
            ),
          ),
          SizedBox(
            width: spacings.lg,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Text(
                  cv.displayName.isNotEmpty
                      ? cv.displayName
                      : cv.fileName,
                  style:
                      typography.h3.copyWith(
                    color: colors.textPrimary,
                  ),
                ),
                SizedBox(
                  height: spacings.xs,
                ),
                Text(
                  cv.fileName,
                  style:
                      typography.bodySmall.copyWith(
                    color:
                        colors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding:
                EdgeInsets.symmetric(
              horizontal: spacings.md,
              vertical: spacings.xs,
            ),
            decoration: BoxDecoration(
              color:
                  colors.accentPrimary.withValues(
                alpha: 0.12,
              ),
              borderRadius:
                  BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                Icon(
                  Icons.star,
                  size: 15,
                  color:
                      colors.accentPrimary,
                ),
                SizedBox(
                  width: spacings.xs,
                ),
                Text(
                  'Activo',
                  style:
                      typography.caption.copyWith(
                    color:
                        colors.accentPrimary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ============================================================
  // CV CARD
  // ============================================================

  Widget _buildCvCard(
    BuildContext context,
    CVDocument cv,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaCard(
      isHoverable: true,
      onTap: () {
        if (!cv.isActive) {
          _selectCv(
            context,
            cv,
          );
        }
      },
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color:
                      colors.surfaceHover,
                  borderRadius:
                      BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.description_outlined,
                  color:
                      colors.textSecondary,
                ),
              ),
              const Spacer(),
              if (cv.isActive)
                Icon(
                  Icons.star,
                  color:
                      colors.accentPrimary,
                  size: 19,
                ),
              PopupMenuButton<String>(
                tooltip: 'Opciones',
                onSelected: (value) {
                  switch (value) {
                    case 'activate':
                      _selectCv(
                        context,
                        cv,
                      );
                      break;

                    case 'delete':
                      _confirmDelete(
                        context,
                        cv,
                      );
                      break;
                  }
                },
                itemBuilder:
                    (context) => [
                  if (!cv.isActive)
                    const PopupMenuItem<String>(
                      value: 'activate',
                      child:
                          Text('Usar este CV'),
                    ),
                  const PopupMenuItem<String>(
                    value: 'delete',
                    child:
                        Text('Eliminar'),
                  ),
                ],
              ),
            ],
          ),
          const Spacer(),
          Text(
            cv.displayName.isNotEmpty
                ? cv.displayName
                : cv.fileName,
            maxLines: 2,
            overflow:
                TextOverflow.ellipsis,
            style:
                typography.h3.copyWith(
              color:
                  colors.textPrimary,
            ),
          ),
          SizedBox(
            height: spacings.xs,
          ),
          Text(
            cv.fileName,
            maxLines: 1,
            overflow:
                TextOverflow.ellipsis,
            style:
                typography.caption.copyWith(
              color:
                  colors.textMuted,
            ),
          ),
          SizedBox(
            height: spacings.sm,
          ),
          Row(
            children: [
              Icon(
                Icons.update_outlined,
                size: 14,
                color:
                    colors.textMuted,
              ),
              SizedBox(
                width: spacings.xs,
              ),
              Text(
                _formatDate(cv.updatedAt),
                style:
                    typography.caption.copyWith(
                  color:
                      colors.textMuted,
                ),
              ),
              const Spacer(),
              if (cv.isActive)
                Text(
                  'CV activo',
                  style:
                      typography.caption.copyWith(
                    color:
                        colors.accentPrimary,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  // ============================================================
  // EMPTY STATE
  // ============================================================

  Widget _buildEmptyState(
    BuildContext context,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Center(
      child: ConstrainedBox(
        constraints:
            const BoxConstraints(
          maxWidth: 560,
        ),
        child: LiaCard(
          isHoverable: false,
          child: Padding(
            padding:
                EdgeInsets.all(
              spacings.xxl,
            ),
            child: Column(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                Container(
                  width: 76,
                  height: 76,
                  decoration:
                      BoxDecoration(
                    color: colors
                        .accentPrimary
                        .withValues(
                      alpha: 0.10,
                    ),
                    shape:
                        BoxShape.circle,
                  ),
                  child: Icon(
                    Icons
                        .description_outlined,
                    size: 38,
                    color:
                        colors.accentPrimary,
                  ),
                ),
                SizedBox(
                  height: spacings.lg,
                ),
                Text(
                  'Todavía no tienes CVs',
                  textAlign:
                      TextAlign.center,
                  style:
                      typography.h3.copyWith(
                    color:
                        colors.textPrimary,
                  ),
                ),
                SizedBox(
                  height: spacings.sm,
                ),
                Text(
                  'Cuando agregues tus CVs aparecerán aquí. '
                  'Podrás conservar diferentes perfiles profesionales '
                  'y elegir cuál quieres utilizar como CV activo.',
                  textAlign:
                      TextAlign.center,
                  style:
                      typography.bodyMedium.copyWith(
                    color:
                        colors.textSecondary,
                  ),
                ),
                SizedBox(
                  height: spacings.lg,
                ),
                LiaButton(
                  text:
                      'Agregar mi primer CV',
                  icon: Icons.upload_file,
                  onPressed: _isUploading
                      ? null
                      : () =>
                          _pickAndUploadCv(
                            context,
                          ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // UPLOAD OVERLAY
  // ============================================================

  Widget _buildUploadingOverlay(
    BuildContext context,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Positioned.fill(
      child: Container(
        color: Colors.black.withValues(
          alpha: 0.72,
        ),
        child: Center(
          child: ConstrainedBox(
            constraints:
                const BoxConstraints(
              maxWidth: 520,
            ),
            child: LiaCard(
              isHoverable: false,
              child: Padding(
                padding:
                    EdgeInsets.all(
                  spacings.xxl,
                ),
                child: Consumer<UploadProvider>(
                  builder: (
                    context,
                    upload,
                    _,
                  ) {
                    final progress =
                        upload.transferProgress;

                    final isAnalysis =
                        upload.currentPhase ==
                            UploadPhase.analysis;

                    return Column(
                      mainAxisSize:
                          MainAxisSize.min,
                      children: [
                        Container(
                          width: 72,
                          height: 72,
                          decoration:
                              BoxDecoration(
                            color: colors
                                .accentPrimary
                                .withValues(
                              alpha: 0.12,
                            ),
                            shape:
                                BoxShape.circle,
                          ),
                          child:
                              isAnalysis
                                  ? Icon(
                                      Icons
                                          .auto_awesome,
                                      size: 36,
                                      color:
                                          colors.accentPrimary,
                                    )
                                  : const SizedBox(
                                      width: 36,
                                      height: 36,
                                      child:
                                          CircularProgressIndicator(),
                                    ),
                        ),
                        SizedBox(
                          height: spacings.lg,
                        ),
                        Text(
                          isAnalysis
                              ? 'Procesando CV'
                              : 'Subiendo CV',
                          style:
                              typography.h3.copyWith(
                            color:
                                colors.textPrimary,
                          ),
                        ),
                        SizedBox(
                          height: spacings.sm,
                        ),
                        Text(
                          upload.fileName.isEmpty
                              ? 'Preparando archivo...'
                              : upload.fileName,
                          maxLines: 2,
                          overflow:
                              TextOverflow.ellipsis,
                          textAlign:
                              TextAlign.center,
                          style:
                              typography.bodyMedium.copyWith(
                            color:
                                colors.textSecondary,
                          ),
                        ),
                        SizedBox(
                          height: spacings.lg,
                        ),
                        LinearProgressIndicator(
                          value: isAnalysis
                              ? upload.analysisProgress
                                  .clamp(0.0, 1.0)
                              : progress.clamp(
                                  0.0,
                                  1.0,
                                ),
                        ),
                        SizedBox(
                          height: spacings.sm,
                        ),
                        Text(
                          isAnalysis
                              ? _analysisStageLabel(
                                  upload.missionStage,
                                )
                              : '${(progress * 100).round()}%',
                          style:
                              typography.caption.copyWith(
                            color:
                                colors.textMuted,
                          ),
                        ),
                        if (upload.hasError) ...[
                          SizedBox(
                            height: spacings.md,
                          ),
                          Text(
                            upload.errorMessage,
                            textAlign:
                                TextAlign.center,
                            style:
                                typography.bodySmall.copyWith(
                              color:
                                  colors.textSecondary,
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ============================================================
  // PICK AND UPLOAD
  // ============================================================

  Future<void> _pickAndUploadCv(
    BuildContext context,
  ) async {
    if (_isUploading) {
      return;
    }

    final uploadProvider = context.read<UploadProvider>();
    final missionActions = context.read<MissionActions>();
    final messenger = ScaffoldMessenger.of(context);

    // ==========================================================
    // 1. FILE PICKER
    // ==========================================================
    FilePickerResult? result;

    try {
      AppLogger.info(
        'MyCVs',
        'Abriendo FilePicker para agregar CV...',
      );

      result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: [
          'pdf',
          'doc',
          'docx',
          'txt',
        ],
        // Web: necesitamos los bytes. Windows: usamos la ruta local.
        withData: kIsWeb,
      );
    } catch (e) {
      // IMPORTANTE:
      // Este catch SOLO cubre el selector. Los errores de HTTP, parser o
      // backend se manejan abajo y ya no aparecerán como "selector".
      AppLogger.error(
        'MyCVs',
        'Error real abriendo FilePicker.',
        error: e,
      );

      if (!mounted) {
        return;
      }

      _showSnackBar(
        messenger,
        'No se pudo abrir el selector de archivos: $e',
        isError: true,
      );
      return;
    }

    if (result == null || result.files.isEmpty) {
      AppLogger.info(
        'MyCVs',
        'Selección de CV cancelada.',
      );
      return;
    }

    final file = result.files.single;
    final filePath = file.path;
    final fileBytes = file.bytes;
    final fileName = file.name;

    // ==========================================================
    // 2. VALIDACIÓN DEL CONTENIDO DEL ARCHIVO
    // ==========================================================

    if (kIsWeb && (fileBytes == null || fileBytes.isEmpty)) {
      AppLogger.error(
        'MyCVs',
        'FilePicker devolvió "$fileName" pero no devolvió bytes en Web.',
      );

      if (!mounted) {
        return;
      }

      _showSnackBar(
        messenger,
        'El navegador seleccionó el archivo, pero no se pudieron leer sus datos.',
        isError: true,
      );
      return;
    }

    if (!kIsWeb && (filePath == null || filePath.isEmpty)) {
      AppLogger.error(
        'MyCVs',
        'FilePicker devolvió "$fileName" sin ruta local.',
      );

      if (!mounted) {
        return;
      }

      _showSnackBar(
        messenger,
        'No se pudo obtener la ruta del archivo seleccionado.',
        isError: true,
      );
      return;
    }

    AppLogger.info(
      'MyCVs',
      'CV seleccionado: $fileName '
      '(${file.size} bytes, web=$kIsWeb)',
    );

    if (!mounted) {
      return;
    }

    // ==========================================================
    // 3. UPLOAD / ANÁLISIS
    // ==========================================================

    setState(() {
      _isUploading = true;
    });

    // Para Web el identificador visual es el nombre, no file.path.
    uploadProvider.startUpload(fileName);

    try {
      await missionActions.uploadCV(
        // Web => bytes. Windows => path.
        filePath: kIsWeb ? null : filePath,
        fileBytes: kIsWeb ? fileBytes : null,
        fileName: fileName,
        onSendProgress: (sent, total) {
          if (!mounted) {
            return;
          }

          uploadProvider.updateDioProgress(
            sent,
            total,
          );
        },
      );

      if (!mounted) {
        return;
      }

      uploadProvider.completeTransfer();
      uploadProvider.completeProcess();

      AppLogger.info(
        'MyCVs',
        'CV procesado correctamente: $fileName',
      );

      setState(() {
        _isUploading = false;
      });

      _showSnackBar(
        messenger,
        'CV agregado correctamente.',
      );
    } catch (e) {
      final message = e.toString().replaceFirst(
        'Exception: ',
        '',
      );

      AppLogger.error(
        'MyCVs',
        'Error real procesando/subiendo CV.',
        error: e,
      );

      if (!mounted) {
        return;
      }

      uploadProvider.setError(
        message.isEmpty
            ? 'No se pudo procesar el CV.'
            : message,
      );

      setState(() {
        _isUploading = false;
      });

      _showSnackBar(
        messenger,
        'No se pudo agregar el CV.\n\n$message',
        isError: true,
      );
    }
  }

  // ============================================================
  // SELECT CV + LOAD PROFESSIONAL PROFILE
  // ============================================================

  Future<void> _selectCv(
  BuildContext context,
  CVDocument cv,
) async {
  final profileHub =
      context.read<ProfileHubProvider>();

  final missionActions =
      context.read<MissionActions>();

  final messenger =
      ScaffoldMessenger.of(context);

  // ==========================================================
  // 1. CAMBIAR CV ACTIVO
  // ==========================================================

  profileHub.selectActiveCv(
    cv.id,
  );

  final profileId =
      cv.professionalProfileId?.trim();

  // ==========================================================
  // 2. VALIDAR RELACIÓN CV → PROFILE
  // ==========================================================

  if (profileId == null ||
      profileId.isEmpty) {
    AppLogger.warning(
      'MyCVs',
      'El CV seleccionado no tiene '
      'professionalProfileId. '
      'No se puede cargar su perfil profesional.',
    );

    return;
  }

  try {
    AppLogger.info(
      'MyCVs',
      'Seleccionando CV: ${cv.displayName}',
    );

    AppLogger.info(
      'MyCVs',
      'Cargando ProfessionalProfile [$profileId].',
    );

    // ========================================================
    // 3. CARGAR EL PROFILE CORRESPONDIENTE
    // ========================================================

    await missionActions.loadProfileForCv(
      cv,
    );

    if (!mounted) {
      return;
    }

    AppLogger.info(
      'MyCVs',
      'ProfessionalProfile cargado correctamente '
      'para ${cv.displayName}.',
    );
  } catch (e) {
    AppLogger.error(
      'MyCVs',
      'No se pudo cargar el ProfessionalProfile '
      'del CV seleccionado.',
      error: e,
    );

    if (!mounted) {
      return;
    }

    messenger
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(
          content: Text(
            'No se pudo cargar el perfil profesional '
            'de este CV.',
          ),
          duration: Duration(
            seconds: 5,
          ),
        ),
      );
  }
}

  // ============================================================
  // DELETE CV
  // ============================================================

  Future<void> _confirmDelete(
    BuildContext context,
    CVDocument cv,
  ) async {
    final profileHub =
        context.read<ProfileHubProvider>();

    final typography =
        context.liaTypography;

    final colors =
        context.liaColors;

    final confirmed =
        await showDialog<bool>(
      context: context,
      builder: (
        dialogContext,
      ) {
        return AlertDialog(
          title: Text(
            'Eliminar CV',
            style:
                typography.h3.copyWith(
              color:
                  colors.textPrimary,
            ),
          ),
          content: Text(
            '¿Quieres eliminar "${cv.displayName.isNotEmpty ? cv.displayName : cv.fileName}" de tu perfil?',
            style:
                typography.bodyMedium.copyWith(
              color:
                  colors.textSecondary,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(
                  dialogContext,
                ).pop(false);
              },
              child:
                  const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(
                  dialogContext,
                ).pop(true);
              },
              child:
                  const Text('Eliminar'),
            ),
          ],
        );
      },
    );

    if (confirmed != true ||
        !mounted) {
      return;
    }

    profileHub.removeCv(
      cv.id,
    );
  }

  // ============================================================
  // SNACKBAR
  // ============================================================

  void _showSnackBar(
    ScaffoldMessengerState messenger,
    String message, {
    bool isError = false,
  }) {
    messenger
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          duration: Duration(
            seconds: isError ? 5 : 3,
          ),
        ),
      );
  }

  // ============================================================
  // ANALYSIS STAGE
  // ============================================================

  String _analysisStageLabel(
    MissionStage stage,
  ) {
    switch (stage) {
      case MissionStage.receiveFile:
        return 'Recibiendo archivo...';

      case MissionStage.storeFile:
        return 'Guardando CV...';

      case MissionStage.detectFormat:
        return 'Detectando formato...';

      case MissionStage.readDocument:
        return 'Leyendo documento...';

      case MissionStage.extractText:
        return 'Extrayendo información...';

      case MissionStage.normalizeText:
        return 'Normalizando información...';

      case MissionStage.buildProfile:
        return 'Construyendo perfil profesional...';

      case MissionStage.saveProfile:
        return 'Guardando perfil...';

      case MissionStage.updateRuntime:
        return 'Actualizando EmployX...';

      case MissionStage.complete:
        return 'Proceso completado.';
    }
  }

  // ============================================================
  // DATE
  // ============================================================

  String _formatDate(
    DateTime date,
  ) {
    final local = date.toLocal();

    final day = local.day
        .toString()
        .padLeft(2, '0');

    final month = local.month
        .toString()
        .padLeft(2, '0');

    final year =
        local.year.toString();

    return '$day/$month/$year';
  }
}