import 'package:flutter/material.dart';

class AgentConnectionPainter extends CustomPainter {
  final Offset start;
  final Offset end;
  final Color color;
  final double progress; // 0.0 to 1.0 representing the light traveling
  
  AgentConnectionPainter({
    required this.start,
    required this.end,
    required this.color,
    required this.progress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.2)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final path = Path();
    
    // Smooth bezier curve between start and end
    path.moveTo(start.dx, start.dy);
    
    // Calculate control points for vertical flow
    final controlPoint1 = Offset(start.dx, start.dy + (end.dy - start.dy) / 2);
    final controlPoint2 = Offset(end.dx, start.dy + (end.dy - start.dy) / 2);
    
    path.cubicTo(
      controlPoint1.dx, controlPoint1.dy,
      controlPoint2.dx, controlPoint2.dy,
      end.dx, end.dy,
    );

    // Draw background line
    canvas.drawPath(path, paint);

    // Draw glowing traveling light if progress > 0
    if (progress > 0.0 && progress < 1.0) {
      final pathMetrics = path.computeMetrics();
      if (pathMetrics.isNotEmpty) {
        final metric = pathMetrics.first;
        final length = metric.length;
        
        final currentPosition = progress * length;
        final segmentLength = length * 0.15; // 15% of path is glowing
        
        final startExtract = (currentPosition - segmentLength).clamp(0.0, length);
        final endExtract = currentPosition.clamp(0.0, length);
        
        final glowPath = metric.extractPath(startExtract, endExtract);
        
        final glowPaint = Paint()
          ..color = color
          ..strokeWidth = 3.0
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8.0);
          
        final solidPaint = Paint()
          ..color = Colors.white
          ..strokeWidth = 2.0
          ..style = PaintingStyle.stroke
          ..strokeCap = StrokeCap.round;

        canvas.drawPath(glowPath, glowPaint);
        canvas.drawPath(glowPath, solidPaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant AgentConnectionPainter oldDelegate) {
    return oldDelegate.progress != progress || 
           oldDelegate.start != start || 
           oldDelegate.end != end || 
           oldDelegate.color != color;
  }
}
