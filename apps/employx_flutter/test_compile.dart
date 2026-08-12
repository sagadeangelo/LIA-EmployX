import 'package:file_picker/file_picker.dart';

void main() async {
  final result = await FilePicker.pickFiles(
    type: FileType.custom,
    allowedExtensions: ['pdf', 'docx'],
  );
  print(result);
}
