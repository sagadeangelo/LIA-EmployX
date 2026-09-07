import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:employx_flutter/core/theme/lia_colors.dart';
import 'package:employx_flutter/core/theme/lia_spacings.dart';
import 'package:employx_flutter/core/theme/lia_typography.dart';
import 'package:employx_flutter/core/ui/lia_button.dart';
import 'package:employx_flutter/features/cvs/data/cv_api.dart';
import 'package:employx_flutter/features/cvs/views/my_cvs_screen.dart';

class FakeApi extends CvApi {
  Map<String, dynamic>? saved;
  bool offline = false;
  bool saveFails = false;
  @override
  Future<List<Map<String, dynamic>>> list() async {
    if (offline)
      throw const CvApiException('No se pudo conectar con el servidor.');
    return saved == null
        ? []
        : [
            {
              'id': '1',
              'title': saved!['title'],
              'full_name': saved!['profile']['personal_info']['full_name'],
              'updated_at': '2026-09-07',
            },
          ];
  }

  @override
  Future<Map<String, dynamic>> analyze(
    String name,
    Uint8List bytes, {
    String mode = 'local',
  }) async => {
    'title': 'CV de prueba',
    'profile': {
      'personal_info': {
        'full_name': 'Persona de prueba',
        'email': 'demo@example.com',
      },
      'summary': '',
      'experience': [],
      'education': [],
      'skills': [],
      'languages': [],
      'certifications': [],
      'projects': [],
      'social_links': {},
      'preferences': {},
    },
    'source_text': 'Documento original',
    'extraction_method': 'local',
    'warnings': <String>[],
  };
  @override
  Future<Map<String, dynamic>> save(Map<String, dynamic> draft) async {
    if (saveFails)
      throw const CvApiException('No se pudo guardar. Vuelve a intentar.');
    saved =
        jsonDecode(jsonEncode({...draft, 'id': '1'})) as Map<String, dynamic>;
    return saved!;
  }

  @override
  Future<Map<String, dynamic>> get(String id) async => saved!;
}

Finder button(String text) => find.widgetWithText(LiaButton, text);
Finder field(String label) => find.widgetWithText(TextFormField, label);

void main() {
  Future<void> open(WidgetTester tester, FakeApi api) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData(
          brightness: Brightness.dark,
          extensions: [
            LiaColors.dark,
            LiaSpacings.modern,
            const LiaTypography(
              display: TextStyle(fontSize: 48),
              h1: TextStyle(fontSize: 32),
              h2: TextStyle(fontSize: 24),
              h3: TextStyle(fontSize: 20),
              bodyLarge: TextStyle(fontSize: 18),
              bodyMedium: TextStyle(fontSize: 15),
              bodySmall: TextStyle(fontSize: 14),
              caption: TextStyle(fontSize: 13),
              button: TextStyle(fontSize: 14),
            ),
          ],
        ),
        home: MyCvsScreen(
          api: api,
          pickFile: () async => SelectedCv('cv.txt', Uint8List.fromList([65])),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('select, edit, save, reopen profile', (tester) async {
    final api = FakeApi();
    addTearDown(api.close);
    await open(tester, api);
    await tester.tap(button('Nuevo CV'));
    await tester.pumpAndSettle();
    await tester.enterText(field('Nombre completo'), 'Nombre corregido');
    await tester.tap(button('Guardar perfil'));
    await tester.pumpAndSettle();
    expect(find.text('Nombre corregido'), findsOneWidget);
    expect(api.saved!['source_text'], 'Documento original');
    await tester.tap(find.text('CV de prueba'));
    await tester.pumpAndSettle();
    expect(
      find.widgetWithText(TextFormField, 'Nombre corregido'),
      findsOneWidget,
    );
  });

  testWidgets('save failure preserves edits and can retry', (tester) async {
    final api = FakeApi()..saveFails = true;
    addTearDown(api.close);
    await open(tester, api);
    await tester.tap(button('Nuevo CV'));
    await tester.pumpAndSettle();
    await tester.enterText(field('Nombre completo'), 'No perder');
    await tester.tap(button('Guardar perfil'));
    await tester.pumpAndSettle();
    expect(find.text('No se pudo guardar. Vuelve a intentar.'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'No perder'), findsOneWidget);
    api.saveFails = false;
    await tester.tap(button('Guardar perfil'));
    await tester.pumpAndSettle();
    expect(api.saved!['profile']['personal_info']['full_name'], 'No perder');
  });

  testWidgets('offline list has retry', (tester) async {
    final api = FakeApi()..offline = true;
    addTearDown(api.close);
    await open(tester, api);
    expect(find.text('No se pudo conectar con el servidor.'), findsOneWidget);
    api.offline = false;
    await tester.tap(button('Reintentar'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Aún no tienes perfiles'), findsOneWidget);
  });
}
