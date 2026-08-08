import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/providers/upload_provider.dart';

class NeonProgressBar extends StatefulWidget {
  final double progress; // 0.0 to 1.0
  final UploadPhase phase;
  final String? centerText;

  const NeonProgressBar({
    Key? key,
    required this.progress,
    required this.phase,
    this.centerText,
  }) : super(key: key);

  @override
  State<NeonProgressBar> createState() => _NeonProgressBarState();
}

class _NeonProgressBarState extends State<NeonProgressBar> with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _breatheController;
  late Animation<double> _glowAnimation;
  late Animation<double> _breatheAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _glowAnimation = Tween<double>(begin: 8.0, end: 18.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Subtle breathing for the whole bar
    _breatheController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);

    _breatheAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _breatheController, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _breatheController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final gradientColors = [
      const Color(0xFF8A2BE2),
      const Color(0xFF3B82F6),
      const Color(0xFF06D6A0),
      const Color(0xFF00FF8B),
    ];

    final clampedProgress = widget.progress.clamp(0.0, 1.0);
    final percentage = (clampedProgress * 100).toInt();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Percentage or Center Text with glow
        AnimatedBuilder(
          animation: _glowAnimation,
          builder: (context, child) {
            return Text(
              widget.centerText ?? '$percentage%',
              style: GoogleFonts.inter(
                fontSize: widget.centerText != null ? 32 : 64,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                shadows: [
                  Shadow(
                    color: const Color(0xFF06D6A0).withOpacity(0.6),
                    blurRadius: _glowAnimation.value,
                  ),
                ],
              ),
              textAlign: TextAlign.center,
            );
          },
        ),
        const SizedBox(height: 16),
        // Progress Bar
        AnimatedBuilder(
          animation: Listenable.merge([_glowAnimation, _breatheAnimation]),
          builder: (context, child) {
            return Opacity(
              opacity: widget.phase == UploadPhase.analysis ? _breatheAnimation.value : 1.0,
              child: Container(
                height: 24,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.4),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFF8A2BE2).withOpacity(0.3),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF8A2BE2).withOpacity(0.2),
                      blurRadius: _glowAnimation.value / 2,
                      spreadRadius: 1,
                    ),
                  ],
                ),
                child: Stack(
                  children: [
                    LayoutBuilder(
                      builder: (context, constraints) {
                        return AnimatedContainer(
                          duration: Duration(milliseconds: widget.phase == UploadPhase.transfer ? 300 : 1200),
                          curve: Curves.easeOutCubic,
                          width: constraints.maxWidth * clampedProgress,
                          height: constraints.maxHeight,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(12),
                            gradient: LinearGradient(
                              colors: gradientColors,
                              stops: const [0.0, 0.33, 0.66, 1.0],
                              begin: Alignment.centerLeft,
                              end: Alignment.centerRight,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF00FF8B).withOpacity(0.5),
                                blurRadius: _glowAnimation.value,
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            );
          }
        ),
      ],
    );
  }
}
