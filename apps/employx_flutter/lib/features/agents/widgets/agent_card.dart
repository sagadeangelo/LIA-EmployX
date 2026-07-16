import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../models/agent_models.dart';
import 'agent_animations.dart';

class AgentCard extends StatefulWidget {
  final AgentModel agent;
  final VoidCallback onTap;

  const AgentCard({
    Key? key,
    required this.agent,
    required this.onTap,
  }) : super(key: key);

  @override
  State<AgentCard> createState() => _AgentCardState();
}

class _AgentCardState extends State<AgentCard> with SingleTickerProviderStateMixin {
  bool _isHovered = false;
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final isActive = widget.agent.status != AgentStatus.idle && widget.agent.status != AgentStatus.disabled;
    final progress = widget.agent.execution.currentProgress;

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: () {
          setState(() {
            _isExpanded = !_isExpanded;
          });
          widget.onTap();
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOutQuart,
          // Premium subtle scale effect on hover
          transform: Matrix4.diagonal3Values(_isHovered ? 1.01 : 1.0, _isHovered ? 1.01 : 1.0, 1.0),
          transformAlignment: Alignment.center,
          decoration: BoxDecoration(
            color: colors.surface,
            borderRadius: spacings.radiusLg,
            border: Border.all(
              color: _isHovered ? widget.agent.color.withOpacity(0.5) : colors.border,
              width: 1,
            ),
            boxShadow: [
              if (_isHovered)
                BoxShadow(
                  color: widget.agent.color.withOpacity(0.15),
                  blurRadius: 24,
                  spreadRadius: 2,
                  offset: const Offset(0, 8),
                )
              else
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
            ],
          ),
          child: ClipRRect(
            borderRadius: spacings.radiusLg,
            child: Stack(
              children: [
                // Premium Top Indicator Glow Line
                Positioned(
                  top: 0,
                  left: 0,
                  right: 0,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    height: 3,
                    decoration: BoxDecoration(
                      color: isActive ? widget.agent.color : colors.border,
                      boxShadow: isActive ? [
                        BoxShadow(
                          color: widget.agent.color.withOpacity(0.5),
                          blurRadius: 6,
                          spreadRadius: 1,
                        )
                      ] : null,
                    ),
                  ),
                ),
                
                Padding(
                  padding: EdgeInsets.all(spacings.lg),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Header Row
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Icon with specific animation
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: widget.agent.color.withOpacity(0.1),
                              borderRadius: spacings.radiusMd,
                              border: Border.all(
                                color: widget.agent.color.withOpacity(0.2),
                              ),
                            ),
                            child: AgentIconAnimation(
                              type: widget.agent.type,
                              color: widget.agent.color,
                              icon: widget.agent.icon,
                              isActive: isActive,
                              isCoordinating: widget.agent.status == AgentStatus.coordinating,
                            ),
                          ),
                          SizedBox(width: spacings.md),
                          
                          // Titles
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  widget.agent.name,
                                  style: typography.h3.copyWith(
                                    color: colors.textPrimary,
                                    fontSize: 18,
                                  ),
                                ),
                                SizedBox(height: 2),
                                Text(
                                  widget.agent.subtitle,
                                  style: typography.bodySmall.copyWith(
                                    color: widget.agent.color,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          
                          // Status Badge
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: isActive ? widget.agent.color.withOpacity(0.1) : colors.surfaceHover,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: isActive ? widget.agent.color.withOpacity(0.3) : colors.border,
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
                                    ),
                                  ),
                                  const SizedBox(width: 6),
                                ],
                                Text(
                                  _getStatusText(widget.agent.status).toUpperCase(),
                                  style: typography.caption.copyWith(
                                    color: isActive ? widget.agent.color : colors.textSecondary,
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      
                      SizedBox(height: spacings.lg),

                      // Current Action & Progress
                      if (isActive) ...[
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Actualmente',
                              style: typography.caption.copyWith(color: colors.textSecondary),
                            ),
                            Text(
                              '${(progress * 100).toInt()}%',
                              style: typography.caption.copyWith(
                                color: widget.agent.color,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        SizedBox(height: spacings.xs),
                        Text(
                          widget.agent.execution.currentActionText,
                          style: typography.bodyMedium.copyWith(
                            color: colors.textPrimary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        SizedBox(height: spacings.md),
                        
                        // Progress Bar (Linear Scanner or Standard)
                        AgentProgressBar(
                          color: widget.agent.color,
                          progress: progress,
                          type: widget.agent.type,
                        ),
                      ] else ...[
                        Text(
                          'Esperando instrucciones...',
                          style: typography.bodyMedium.copyWith(color: colors.textSecondary, fontStyle: FontStyle.italic),
                        ),
                      ],

                      // Smooth Size Expansion for Details
                      AnimatedSize(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOutQuart,
                        alignment: Alignment.topCenter,
                        child: _isExpanded ? _buildExpandedDetails(context) : const SizedBox(width: double.infinity),
                      ),
                      
                      SizedBox(height: spacings.md),
                      
                      // Footer (Last/Next Action & Active Time)
                      Divider(color: colors.border),
                      SizedBox(height: spacings.md),
                      
                      if (widget.agent.execution.lastActionText.isNotEmpty) ...[
                        _buildActionRow(context, 'Última acción', widget.agent.execution.lastActionText),
                        SizedBox(height: spacings.xs),
                      ],
                      if (widget.agent.execution.nextActionText.isNotEmpty) ...[
                        _buildActionRow(context, 'Próxima acción', widget.agent.execution.nextActionText),
                        SizedBox(height: spacings.md),
                      ],

                      // Footer Bottom actions
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.timer_outlined, size: 14, color: colors.textSecondary),
                              const SizedBox(width: 4),
                              Text(
                                'Activo: ${widget.agent.metrics.timeSaved.inHours}h ${widget.agent.metrics.timeSaved.inMinutes % 60}m',
                                style: typography.caption.copyWith(color: colors.textSecondary),
                              ),
                            ],
                          ),
                          Row(
                            children: [
                              Text(
                                _isExpanded ? 'Ocultar detalles' : 'Ver detalles',
                                style: typography.caption.copyWith(
                                  color: colors.textPrimary,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Icon(
                                _isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                                size: 16,
                                color: colors.textSecondary,
                              ),
                            ],
                          ),
                        ],
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
  }

  Widget _buildActionRow(BuildContext context, String label, String action) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 100,
          child: Text(
            label,
            style: typography.caption.copyWith(color: colors.textSecondary),
          ),
        ),
        Expanded(
          child: Text(
            action,
            style: typography.caption.copyWith(color: colors.textPrimary),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _buildExpandedDetails(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Padding(
      padding: EdgeInsets.only(top: spacings.lg, bottom: spacings.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Capacidades',
            style: typography.caption.copyWith(
              color: colors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: spacings.sm),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.agent.capabilities.skills.map((skill) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: colors.surfaceHover,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: colors.border),
                ),
                child: Text(
                  skill, 
                  style: typography.caption.copyWith(color: colors.textPrimary),
                ),
              );
            }).toList(),
          ),
          
          SizedBox(height: spacings.xl),
          
          Container(
            padding: EdgeInsets.all(spacings.md),
            decoration: BoxDecoration(
              color: colors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: colors.border),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetricItem(context, 'Tareas', '${widget.agent.metrics.tasksCompleted}'),
                Container(width: 1, height: 30, color: colors.border),
                _buildMetricItem(context, 'Ahorro', '${widget.agent.metrics.timeSaved.inMinutes}m'),
                Container(width: 1, height: 30, color: colors.border),
                _buildMetricItem(context, 'Uso CPU', '${(widget.agent.metrics.cpuUsage * 100).toInt()}%'),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMetricItem(BuildContext context, String label, String value) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(value, style: typography.h3.copyWith(color: colors.textPrimary, fontSize: 18)),
        const SizedBox(height: 2),
        Text(label, style: typography.caption.copyWith(color: colors.textSecondary)),
      ],
    );
  }

  String _getStatusText(AgentStatus status) {
    switch (status) {
      case AgentStatus.idle: return 'En espera';
      case AgentStatus.active: return 'Activo';
      case AgentStatus.thinking: return 'Pensando';
      case AgentStatus.planning: return 'Planeando';
      case AgentStatus.coordinating: return 'Coordinando';
      case AgentStatus.executing: return 'Ejecutando';
      case AgentStatus.waiting: return 'Esperando';
      case AgentStatus.success: return 'Éxito';
      case AgentStatus.warning: return 'Advertencia';
      case AgentStatus.error: return 'Error';
      case AgentStatus.disabled: return 'Inactivo';
    }
  }
}
