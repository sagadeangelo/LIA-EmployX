import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../models/agent_models.dart';
import '../../../core/theme/lia_theme.dart';

class AgentIconAnimation extends StatefulWidget {
  final AgentType type;
  final Color color;
  final IconData icon;
  final bool isActive;
  final bool isCoordinating;

  const AgentIconAnimation({
    Key? key,
    required this.type,
    required this.color,
    required this.icon,
    this.isActive = false,
    this.isCoordinating = false,
  }) : super(key: key);

  @override
  State<AgentIconAnimation> createState() => _AgentIconAnimationState();
}

class _AgentIconAnimationState extends State<AgentIconAnimation> with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _radarController;
  
  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    
    _radarController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );

    if (widget.isActive) {
      _pulseController.repeat(reverse: true);
      _radarController.repeat();
    }
  }

  @override
  void didUpdateWidget(AgentIconAnimation oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      _pulseController.repeat(reverse: true);
      _radarController.repeat();
    } else if (!widget.isActive && oldWidget.isActive) {
      _pulseController.stop();
      _radarController.stop();
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _radarController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isActive) {
      return Icon(widget.icon, color: widget.color, size: 24);
    }

    if (widget.type == AgentType.career) {
      // Pulse animation with ring
      return AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          final scale = 1.0 + (_pulseController.value * 0.15);
          final opacity = 1.0 - (_pulseController.value * 0.3);
          
          return Stack(
            alignment: Alignment.center,
            children: [
              if (widget.isCoordinating)
                Transform.scale(
                  scale: 1.0 + (_pulseController.value * 1.5),
                  child: Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: widget.color.withOpacity(1.0 - _pulseController.value),
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: widget.color.withOpacity((1.0 - _pulseController.value) * 0.5),
                          blurRadius: 10,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  ),
                ),
              Transform.scale(
                scale: scale,
                child: Icon(widget.icon, color: widget.color.withOpacity(opacity), size: 24),
              ),
            ],
          );
        },
      );
    }
    
    if (widget.type == AgentType.hunter) {
      // Radar animation
      return AnimatedBuilder(
        animation: _radarController,
        builder: (context, child) {
          return Stack(
            alignment: Alignment.center,
            children: [
              Icon(widget.icon, color: widget.color.withOpacity(0.5), size: 24),
              // Radar sweeping hand
              Transform.rotate(
                angle: _radarController.value * 2 * math.pi,
                child: Align(
                  alignment: Alignment.topCenter,
                  child: Container(
                    width: 2,
                    height: 12,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          widget.color.withOpacity(0.8),
                          widget.color.withOpacity(0.0),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              // Orbiting dots
              ...List.generate(3, (index) {
                final offset = (index * 0.33);
                final value = (_radarController.value + offset) % 1.0;
                return Transform.rotate(
                  angle: value * 2 * math.pi,
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Container(
                      width: 4,
                      height: 4,
                      margin: const EdgeInsets.only(top: 2),
                      decoration: BoxDecoration(
                        color: widget.color,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: widget.color.withOpacity(0.8),
                            blurRadius: 4,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }),
            ],
          );
        },
      );
    }

    // Default active state
    return Icon(widget.icon, color: widget.color, size: 24);
  }
}

class AgentProgressBar extends StatefulWidget {
  final Color color;
  final double progress;
  final AgentType type;

  const AgentProgressBar({
    Key? key,
    required this.color,
    required this.progress,
    required this.type,
  }) : super(key: key);

  @override
  State<AgentProgressBar> createState() => _AgentProgressBarState();
}

class _AgentProgressBarState extends State<AgentProgressBar> with SingleTickerProviderStateMixin {
  late AnimationController _scanController;

  @override
  void initState() {
    super.initState();
    _scanController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1, milliseconds: 500),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _scanController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    
    return LayoutBuilder(
      builder: (context, constraints) {
        final double maxWidth = constraints.maxWidth;
        
        return Stack(
          children: [
            // Background
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: colors.surfaceHover,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
            // Progress Fill
            FractionallySizedBox(
              widthFactor: widget.progress.clamp(0.0, 1.0),
              child: Container(
                height: 6,
                decoration: BoxDecoration(
                  color: widget.color,
                  borderRadius: BorderRadius.circular(3),
                  boxShadow: [
                    BoxShadow(
                      color: widget.color.withOpacity(0.3),
                      blurRadius: 4,
                      offset: const Offset(0, 1),
                    ),
                  ],
                ),
              ),
            ),
            // Scanner effect for CV Agent
            if (widget.type == AgentType.cv)
              AnimatedBuilder(
                animation: _scanController,
                builder: (context, child) {
                  return Positioned(
                    left: _scanController.value * (maxWidth - 30),
                    child: Container(
                      width: 30,
                      height: 6,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.white.withOpacity(0.0),
                            Colors.white.withOpacity(0.9),
                            Colors.white.withOpacity(0.0),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
          ],
        );
      }
    );
  }
}
