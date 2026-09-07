import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:employx_flutter/features/cvs/data/cv_api.dart';

void main() {
  test('unavailable backend gives a readable error', () async {
    final api = CvApi(
      client: MockClient((_) async => throw http.ClientException('offline')),
    );
    addTearDown(api.close);
    await expectLater(
      api.list(),
      throwsA(
        isA<CvApiException>().having(
          (e) => e.message,
          'message',
          contains('No se pudo conectar'),
        ),
      ),
    );
  });

  test('uploads bytes and selected analysis mode', () async {
    final api = CvApi(
      client: MockClient((request) async {
        expect(request.url.queryParameters['mode'], 'lmstudio');
        expect(
          request.headers['content-type'],
          contains('multipart/form-data'),
        );
        expect(request.body, contains('demo@example.com'));
        return http.Response(jsonEncode({'profile': {}, 'title': 'cv'}), 200);
      }),
    );
    addTearDown(api.close);
    await api.analyze(
      'cv.txt',
      Uint8List.fromList(utf8.encode('demo@example.com')),
      mode: 'lmstudio',
    );
  });

  test('empty and unsupported files are rejected before network', () async {
    final api = CvApi(
      client: MockClient((_) async => throw StateError('Unexpected request')),
    );
    addTearDown(api.close);
    await expectLater(
      api.analyze('cv.txt', Uint8List(0)),
      throwsA(isA<CvApiException>()),
    );
    await expectLater(
      api.analyze('cv.docx', Uint8List(1)),
      throwsA(isA<CvApiException>()),
    );
  });

  test('updates use PUT without sending server metadata', () async {
    final api = CvApi(
      client: MockClient((request) async {
        expect(request.method, 'PUT');
        expect(request.url.path, '/api/cvs/example');
        final payload = jsonDecode(request.body) as Map;
        expect(payload.containsKey('id'), false);
        expect(payload.containsKey('created_at'), false);
        expect(payload['profile']['summary'], 'Edited');
        return http.Response(request.body, 200);
      }),
    );
    addTearDown(api.close);
    await api.save({
      'id': 'example',
      'created_at': 'date',
      'title': 'CV',
      'profile': {'summary': 'Edited'},
      'source_text': 'Original',
      'extraction_method': 'local',
      'warnings': <String>[],
    });
  });
}
