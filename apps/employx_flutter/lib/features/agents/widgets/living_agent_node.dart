import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../models/agent_models.dart';
import 'agent_animations.dart';

class LivingAgentNode extends StatefulWidget {
  final AgentModel agent;
  final bool isConnectedAbove;
  final bool isConnectedBelow;

  const LivingAgentNode({
    Key? key,
    required this.agent,
    this.isConnectedAbove = false,
    this.isConnectedBelow = false,
  }) : super(key: key);

  @override
  State<LivingAgentNode> createState() => _LivingAgentNodeState();
}

class _LivingAgentNodeState extends State<LivingAgentNode> with TickerProviderStateMixin {
  late AnimationController _breathController;
  late AnimationController _glowController;
  
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    // Breathing effect
    _breathController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);
    
    // Glow pulsing
    _glowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    
    if (widget.agent.status != AgentStatus.idle) {
      _glowController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(covariant LivingAgentNode oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.agent.status != AgentStatus.idle && oldWidget.agent.status == AgentStatus.idle) {
      _glowController.repeat(reverse: true);
    } else if (widget.agent.status == AgentStatus.idle && oldWidget.agent.status != AgentStatus.idle) {
      _glowController.stop();
    }
  }

  @override
  void dispose() {
    _breathController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final isActive = widget.agent.status != AgentStatus.idle && widget.agent.status != AgentStatus.disabled;
    
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: AnimatedBuilder(
        animation: Listenable.merge([_breathController, _glowController]),
        builder: (context, child) {
          // Calculate organic scales and glows
          final breathScale = isActive ? 1.0 + (_breathController.value * 0.01) : 1.0;
          final hoverScale = _isHovered ? 1.02 : 1.0;
          final combinedScale = breathScale * hoverScale;
          
          final glowOpacity = isActive ? 0.05 + (_glowController.value * 0.1) : 0.0;
          
          return Transform.scale(
            scale: combinedScale,
            child: Container(
              margin: EdgeInsets.symmetric(vertical: spacings.md),
              decoration: BoxDecoration(
                color: colors.surface.withAlpha(200), // Slightly transparent for glass effect
                borderRadius: spacings.radiusLg,
                border: Border.all(
                  color: _isHovered 
                    ? widget.agent.color.withAlpha(128) 
                    : colors.border.withAlpha(128),
                  width: 1,
                ),
                boxShadow: [
                  // Magnetic Glow Aura
                  if (isActive)
                    BoxShadow(
                      color: widget.agent.color.withAlpha((glowOpacity * 255).toInt()),
                      blurRadius: 40,
                      spreadRadius: 5,
                    ),
                  // Drop shadow
                  BoxShadow(
                    color: Colors.black.withAlpha(100),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: spacings.radiusLg,
                child: Padding(
                  padding: EdgeInsets.all(spacings.lg),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // Agent Core Icon (The "Brain")
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          color: widget.agent.color.withAlpha(25),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: widget.agent.color.withAlpha(50),
                          ),
                        ),
                        child: Center(
                          child: AgentIconAnimation(
                            type: widget.agent.type,
                            color: widget.agent.color,
                            icon: widget.agent.icon,
                            isActive: isActive,
                            isCoordinating: widget.agent.status == AgentStatus.coordinating,
                          ),
                        ),
                      ),
                      
                      SizedBox(width: spacings.xl),
                      
                      // Agent Thoughts & Progress
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  widget.agent.name,
                                  style: typography.h3.copyWith(
                                    color: colors.textPrimary,
                                    fontSize: 18,
                                  ),
                                ),
                                // Status Chip
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: isActive ? widget.agent.color.withAlpha(25) : colors.surfaceHover,
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(
                                      color: isActive ? widget.agent.color.withAlpha(76) : colors.border,
                                    ),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      if (isActive) ...[
                                        Container(
                                          width: 6,
                                          height: 6,
                                          decoration: BoxDecoration(
                                            color: widget.agent.color,
                                            shape: BoxShape.circle,
                                            boxShadow: [
                                              BoxShadow(
                                                color: widget.agent.color,
                                                blurRadius: 4,
                                              ),
                                            ]
                                          ),
                                        ),
                                        const SizedBox(width: 6),
                                      ],
                                      Text(
                                        _getStatusText(widget.agent.status).toUpperCase(),
                                        style: typography.caption.copyWith(
                                          color: isActive ? widget.agent.color : colors.textSecondary,
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            
                            SizedBox(height: spacings.sm),
                            
                            // Thought Stream (Current Action)
                            AnimatedSwitcher(
                              duration: const Duration(milliseconds: 500),
                              transitionBuilder: (Widget child, Animation<double> animation) {
                                return FadeTransition(
                                  opacity: animation,
                                  child: SlideTransition(
                                    position: Tween<Offset>(
                                      begin: const Offset(0.0, 0.2),
                                      end: Offset.zero,
                                    ).animate(animation),
                                    child: child,
                                  ),
                                );
                              },
                              child: Text(
                                isActive ? widget.agent.execution.currentActionText : "En espera de contexto...",
                                key: ValueKey<String>(widget.agent.execution.currentActionText),
                                style: typography.bodyMedium.copyWith(
                                  color: isActive ? colors.textPrimary : colors.textMuted,
                                  fontFamily: 'monospace', // Gives a terminal/AI feel
                                ),
                              ),
                            ),
                            
                            SizedBox(height: spacings.md),
                            
                            // Organic Progress Bar
                            if (isActive)
                              OrganicProgressBar(
                                color: widget.agent.color,
                                progress: widget.agent.execution.currentProgress,
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  String _getStatusText(AgentStatus status) {
    switch (status) {
      case AgentStatus.idle: return 'Dormido';
      case AgentStatus.active: return 'Procesando';
      case AgentStatus.thinking: return 'Pensando';
      case AgentStatus.planning: return 'Planeando';
      case AgentStatus.coordinating: return 'Coordinando';
      case AgentStatus.executing: return 'Ejecutando';
      case AgentStatus.waiting: return 'Esperando';
      case AgentStatus.success: return 'Éxito';
      case AgentStatus.warning: return 'Alerta';
      case AgentStatus.error: return 'Error';
      case AgentStatus.disabled: return 'Apagado';
    }
  }
}

class OrganicProgressBar extends StatefulWidget {
  final Color color;
  final double progress;

  const OrganicProgressBar({
    Key? key,
    required this.color,
    required this.progress,
  }) : super(key: key);

  @override
  State<OrganicProgressBar> createState() => _OrganicProgressBarState();
}

class _OrganicProgressBarState extends State<OrganicProgressBar> with SingleTickerProviderStateMixin {
  late AnimationController _flowController;

  @override
  void initState() {
    super.initState();
    _flowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
  }

  @override
  void dispose() {
    _flowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    
    return Stack(
      children: [
        // Base track
        Container(
          height: 4,
          decoration: BoxDecoration(
            color: colors.surfaceHover,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        // Progress Fill
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOutCubic,
          height: 4,
          width: MediaQuery.of(context).size.width * 0.6 * widget.progress, // Assuming max width roughly 60% of screen in this context
          decoration: BoxDecoration(
            color: widget.color,
            borderRadius: BorderRadius.circular(2),
            boxShadow: [
              BoxShadow(
                color: widget.color.withAlpha(128),
                blurRadius: 8,
                spreadRadius: 1,
              ),
            ],
          ),
        ),
        // Flowing particles/light
        AnimatedBuilder(
          animation: _flowController,
          builder: (context, child) {
            return Positioned(
              left: _flowController.value * (MediaQuery.of(context).size.width * 0.6 * widget.progress.clamp(0.1, 1.0)),
              child: Container(
                width: 20,
                height: 4,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.white.withAlpha(0),
                      Colors.white.withAlpha(200),
                      Colors.white.withAlpha(0),
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
}
