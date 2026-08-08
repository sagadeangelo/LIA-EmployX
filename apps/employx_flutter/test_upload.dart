import 'package:dio/dio.dart';
import 'dart:io';

void main() async {
  final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000'));
  
  // Create a dummy file
  final file = File('test_cv.pdf');
  await file.writeAsString('Dummy PDF content');

  try {
    final multipartFile = await MultipartFile.fromFile(file.path, filename: 'test_cv.pdf');
    
    FormData formData = FormData.fromMap({
      "file": multipartFile,
    });

    print('Sending request...');
    final response = await dio.post(
      '/api/v1/cv/upload', 
      data: formData,
    );
    
    print('Status code: ${response.statusCode}');
    print('Response: ${response.data}');
  } on DioException catch (e) {
    print('Dio Error: ${e.message}');
    if (e.response != null) {
      print('Status: ${e.response?.statusCode}');
      print('Data: ${e.response?.data}');
    }
  } finally {
    if (await file.exists()) {
      await file.delete();
    }
  }
}
