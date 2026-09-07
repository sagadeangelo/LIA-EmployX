import 'dart:convert';
import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_button.dart';
import '../data/cv_api.dart';

const _labels = {
  'personal_info': 'Datos personales',
  'full_name': 'Nombre completo',
  'first_name': 'Nombre(s)',
  'last_name': 'Apellidos',
  'email': 'Correo',
  'phone': 'Teléfono',
  'city': 'Ciudad',
  'state': 'Estado',
  'country': 'País',
  'address': 'Dirección',
  'summary': 'Resumen profesional',
  'experience': 'Experiencia',
  'education': 'Educación',
  'skills': 'Habilidades',
  'languages': 'Idiomas',
  'certifications': 'Certificaciones',
  'projects': 'Proyectos',
  'social_links': 'Enlaces',
  'preferences': 'Preferencias',
  'company': 'Empresa',
  'position': 'Puesto',
  'start_date': 'Fecha de inicio',
  'end_date': 'Fecha de fin',
  'location': 'Ubicación',
  'description': 'Descripción',
  'employment_type': 'Tipo de empleo',
  'current': 'En curso',
  'achievements': 'Logros',
  'institution': 'Institución',
  'degree': 'Título o estudios',
  'field_of_study': 'Área de estudio',
  'grade': 'Calificación',
  'name': 'Nombre',
  'level': 'Nivel',
  'years': 'Años (vacío si no se indica)',
  'issuer': 'Emisor',
  'issue_date': 'Fecha de emisión',
  'expiration_date': 'Vencimiento',
  'credential_id': 'Identificador',
  'credential_url': 'Enlace de credencial',
  'confidence': 'Confianza (opcional)',
  'technologies': 'Tecnologías',
  'url': 'Enlace',
  'linkedin': 'LinkedIn',
  'github': 'GitHub',
  'portfolio': 'Portafolio',
  'website': 'Sitio web',
  'desired_salary': 'Salario deseado (opcional)',
  'preferred_country': 'País preferido',
  'preferred_city': 'Ciudad preferida',
  'remote_only': 'Solo remoto',
  'relocation': 'Reubicación',
};
const _templates = <String, Map<String, dynamic>>{
  'experience': {
    'company': '',
    'position': '',
    'start_date': '',
    'end_date': '',
    'location': '',
    'description': '',
    'employment_type': '',
    'current': false,
    'achievements': <String>[],
  },
  'education': {
    'institution': '',
    'degree': '',
    'field_of_study': '',
    'start_date': '',
    'end_date': '',
    'current': false,
    'description': '',
    'location': '',
    'grade': '',
  },
  'skills': {'name': '', 'level': '', 'years': null},
  'languages': {'name': '', 'level': ''},
  'certifications': {
    'name': '',
    'issuer': '',
    'issue_date': '',
    'expiration_date': '',
    'credential_id': '',
    'credential_url': '',
    'description': '',
    'confidence': null,
  },
  'projects': {
    'name': '',
    'description': '',
    'technologies': <String>[],
    'url': '',
  },
};

class ProfileEditor extends StatefulWidget {
  final Map<String, dynamic> draft;
  final CvApi api;
  const ProfileEditor({super.key, required this.draft, required this.api});
  @override
  State<ProfileEditor> createState() => _ProfileEditorState();
}

class _ProfileEditorState extends State<ProfileEditor> {
  final _form = GlobalKey<FormState>();
  late Map<String, dynamic> _draft;
  bool _dirty = false;
  bool _saving = false;
  String? _error;
  int _revision = 0;

  @override
  void initState() {
    super.initState();
    _draft = jsonDecode(jsonEncode(widget.draft)) as Map<String, dynamic>;
    _dirty = _draft['id'] == null;
  }

  Future<void> _cancel() async {
    if (_saving) return;
    if (_dirty) {
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar cambios?'),
          content: const Text(
            'Los cambios de este perfil aún no se han guardado.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir editando'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Descartar'),
            ),
          ],
        ),
      );
      if (discard != true) return;
    }
    if (mounted) Navigator.pop(context, false);
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      final saved = await widget.api.save(_draft);
      if (mounted) Navigator.pop(context, saved);
    } catch (error) {
      if (mounted)
        setState(() {
          _error = error is CvApiException
              ? error.message
              : 'No se pudo guardar. Tus cambios siguen aquí; vuelve a intentar.';
        });
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Widget _fields(Map<String, dynamic> values, String path) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: values.keys.map((key) {
      final value = values[key];
      final label = _labels[key] ?? key;
      if (value is Map<String, dynamic>) {
        return ExpansionTile(
          title: Text(label),
          initiallyExpanded: key == 'personal_info',
          children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: _fields(value, '$path.$key'),
            ),
          ],
        );
      }
      if (value is List || key == 'technologies') {
        final items = value as List? ?? [];
        values[key] = items;
        final template = _templates[key];
        if (template == null) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: TextFormField(
              key: ValueKey('$_revision.$path.$key'),
              initialValue: items.join('\n'),
              decoration: InputDecoration(labelText: '$label (uno por línea)'),
              minLines: 2,
              maxLines: 6,
              onChanged: (text) {
                values[key] = text
                    .split('\n')
                    .where((e) => e.trim().isNotEmpty)
                    .toList();
                _dirty = true;
              },
            ),
          );
        }
        return ExpansionTile(
          title: Text('$label (${items.length})'),
          children: [
            for (var i = 0; i < items.length; i++)
              Padding(
                key: ValueKey('$_revision.$path.$key.$i'),
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Expanded(child: Text('$label ${i + 1}')),
                        IconButton(
                          tooltip: 'Quitar elemento',
                          icon: const Icon(Icons.delete_outline),
                          onPressed: () => setState(() {
                            items.removeAt(i);
                            _dirty = true;
                            _revision++;
                          }),
                        ),
                      ],
                    ),
                    _fields(items[i] as Map<String, dynamic>, '$path.$key.$i'),
                    const Divider(),
                  ],
                ),
              ),
            TextButton.icon(
              icon: const Icon(Icons.add),
              label: Text('Añadir: $label'),
              onPressed: () => setState(() {
                items.add(jsonDecode(jsonEncode(template)));
                _dirty = true;
                _revision++;
              }),
            ),
          ],
        );
      }
      if (value is bool) {
        return CheckboxListTile(
          title: Text(label),
          value: value,
          controlAffinity: ListTileControlAffinity.leading,
          onChanged: (next) => setState(() {
            values[key] = next ?? false;
            _dirty = true;
          }),
        );
      }
      final numeric = ['years', 'desired_salary', 'confidence'].contains(key);
      return Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: TextFormField(
          key: ValueKey('$_revision.$path.$key'),
          initialValue: value?.toString() ?? '',
          decoration: InputDecoration(labelText: label),
          minLines: key == 'summary' || key == 'description' ? 3 : 1,
          maxLines: key == 'summary' || key == 'description' ? 8 : 1,
          keyboardType: numeric
              ? const TextInputType.numberWithOptions(decimal: true)
              : TextInputType.text,
          validator: (text) {
            if (numeric && text != null && text.isNotEmpty) {
              final number = double.tryParse(text);
              if (number == null || !number.isFinite || number < 0)
                return 'Escribe un número válido o deja vacío.';
            }
            return null;
          },
          onChanged: (text) {
            values[key] = numeric
                ? (text.isEmpty ? null : (double.tryParse(text) ?? text))
                : text;
            _dirty = true;
          },
        ),
      );
    }).toList(),
  );

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _cancel();
      },
      child: Dialog(
        child: SizedBox(
          width: 1040,
          height: MediaQuery.sizeOf(context).height * .88,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Revisar perfil profesional',
                  style: context.liaTypography.h2.copyWith(
                    color: colors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _draft['extraction_method'] == 'lmstudio'
                      ? 'Análisis con LM Studio · Revisión necesaria'
                      : 'Extracción básica sin IA · Completa los datos pendientes',
                ),
                const SizedBox(height: 8),
                if (_error != null)
                  Text(_error!, style: TextStyle(color: colors.accentPrimary)),
                Expanded(
                  child: AbsorbPointer(
                    absorbing: _saving,
                    child: SingleChildScrollView(
                      child: Form(
                        key: _form,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            for (final warning
                                in (_draft['warnings'] as List? ?? []))
                              Padding(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 8,
                                ),
                                child: Text(warning.toString()),
                              ),
                            TextFormField(
                              initialValue: _draft['title'] as String,
                              maxLength: 160,
                              decoration: const InputDecoration(
                                labelText: 'Nombre de este CV',
                              ),
                              validator: (v) => v == null || v.trim().isEmpty
                                  ? 'Escribe un nombre para el CV.'
                                  : null,
                              onChanged: (v) {
                                _draft['title'] = v;
                                _dirty = true;
                              },
                            ),
                            ExpansionTile(
                              title: const Text('Consultar texto original'),
                              children: [
                                Padding(
                                  padding: const EdgeInsets.all(12),
                                  child: SelectableText(
                                    _draft['source_text'] as String? ?? '',
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            _fields(
                              _draft['profile'] as Map<String, dynamic>,
                              'profile',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  alignment: WrapAlignment.end,
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    LiaButton(
                      text: 'Cancelar',
                      variant: LiaButtonVariant.secondary,
                      onPressed: _saving ? null : _cancel,
                    ),
                    LiaButton(
                      text: 'Guardar perfil',
                      icon: Icons.save_outlined,
                      isLoading: _saving,
                      onPressed: _save,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
