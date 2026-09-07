import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_button.dart';
import '../../../core/ui/lia_card.dart';
import '../data/cv_api.dart';
import 'profile_editor.dart';

class SelectedCv {
  final String name;
  final Uint8List bytes;
  const SelectedCv(this.name, this.bytes);
}

class MyCvsScreen extends StatefulWidget {
  final CvApi? api;
  final Future<SelectedCv?> Function()? pickFile;
  const MyCvsScreen({super.key, this.api, this.pickFile});
  @override
  State<MyCvsScreen> createState() => _MyCvsScreenState();
}

class _MyCvsScreenState extends State<MyCvsScreen> {
  late final CvApi _api;
  List<Map<String, dynamic>> _profiles = [];
  bool _busy = false;
  String? _error;
  String _progress = '';
  String _mode = 'local';

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? CvApi();
    _load();
  }

  @override
  void dispose() {
    if (widget.api == null) _api.close();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _busy = true;
      _error = null;
      _progress = 'Cargando perfiles…';
    });
    try {
      final profiles = await _api.list();
      if (mounted) setState(() => _profiles = profiles);
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _showError(Object error) {
    if (mounted)
      setState(
        () => _error = error is CvApiException
            ? error.message
            : 'No se pudo completar la operación. Vuelve a intentar.',
      );
  }

  Future<SelectedCv?> _pick() async {
    if (widget.pickFile != null) return widget.pickFile!();
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'txt'],
      allowMultiple: false,
      withData: true,
    );
    if (result == null) return null;
    final file = result.files.single;
    if (file.size > CvApi.maxFileBytes)
      throw const CvApiException('El archivo supera el límite de 10 MB.');
    if (file.bytes == null)
      throw const CvApiException('No se pudo leer el archivo seleccionado.');
    return SelectedCv(file.name, file.bytes!);
  }

  Future<void> _newCv() async {
    setState(() {
      _busy = true;
      _error = null;
      _progress = 'Seleccionando CV…';
    });
    Map<String, dynamic>? draft;
    try {
      final selected = await _pick();
      if (selected == null || !mounted) return;
      setState(
        () => _progress = _mode == 'local'
            ? 'Leyendo el CV…'
            : 'Analizando con LM Studio…',
      );
      draft = await _api.analyze(selected.name, selected.bytes, mode: _mode);
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
    if (mounted && draft != null) await _edit(draft);
  }

  Future<void> _open(String id) async {
    setState(() {
      _busy = true;
      _error = null;
      _progress = 'Abriendo perfil…';
    });
    Map<String, dynamic>? draft;
    try {
      draft = await _api.get(id);
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
    if (mounted && draft != null) await _edit(draft);
  }

  Future<void> _edit(Map<String, dynamic> draft) async {
    final result = await showDialog<dynamic>(
      context: context,
      barrierDismissible: false,
      builder: (_) => ProfileEditor(draft: draft, api: _api),
    );
    if (mounted && result is Map) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Perfil guardado.')));
      await _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    return Scaffold(
      backgroundColor: colors.background,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(context.liaSpacings.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Mis CVs',
              style: typography.h2.copyWith(color: colors.textPrimary),
            ),
            const SizedBox(height: 8),
            Text(
              'Importa, revisa y guarda tus perfiles profesionales.',
              style: typography.bodyMedium.copyWith(
                color: colors.textSecondary,
              ),
            ),
            const SizedBox(height: 20),
            Wrap(
              spacing: 16,
              runSpacing: 12,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                DropdownButton<String>(
                  value: _mode,
                  onChanged: _busy
                      ? null
                      : (value) => setState(() => _mode = value!),
                  items: const [
                    DropdownMenuItem(
                      value: 'local',
                      child: Text('Extracción básica sin IA'),
                    ),
                    DropdownMenuItem(
                      value: 'lmstudio',
                      child: Text('Analizar con LM Studio'),
                    ),
                  ],
                ),
                LiaButton(
                  text: 'Nuevo CV',
                  icon: Icons.add,
                  onPressed: _busy ? null : _newCv,
                ),
                LiaButton(
                  text: 'Actualizar',
                  variant: LiaButtonVariant.secondary,
                  onPressed: _busy ? null : _load,
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text('PDF con texto o TXT · Máximo 10 MB'),
            if (_busy) ...[
              const SizedBox(height: 16),
              const LinearProgressIndicator(),
              const SizedBox(height: 8),
              Text(_progress),
            ],
            if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: LiaCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(_error!),
                      const SizedBox(height: 8),
                      LiaButton(
                        text: 'Reintentar',
                        onPressed: _busy ? null : _load,
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 24),
            if (_profiles.isEmpty && !_busy && _error == null)
              const LiaCard(
                child: Text(
                  'Aún no tienes perfiles guardados. Pulsa Nuevo CV para comenzar.',
                ),
              ),
            for (final profile in _profiles)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: LiaCard(
                  isHoverable: !_busy,
                  onTap: _busy ? null : () => _open(profile['id'] as String),
                  child: Row(
                    children: [
                      Icon(
                        Icons.description_outlined,
                        color: colors.textSecondary,
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              profile['title'] as String,
                              style: typography.h3.copyWith(
                                color: colors.textPrimary,
                              ),
                            ),
                            if ((profile['full_name'] as String? ?? '')
                                .isNotEmpty)
                              Text(profile['full_name'] as String),
                            Text(
                              'Guardado: ${profile['updated_at']}',
                              style: typography.caption.copyWith(
                                color: colors.textMuted,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
