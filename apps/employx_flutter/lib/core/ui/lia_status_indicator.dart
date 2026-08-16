import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme/lia_theme.dart';
import '../models/mission_snapshot_model.dart';
import '../providers/mission_provider.dart';

class LiaStatusIndicator extends StatelessWidget {
  final Color color;
  final String label;
  final String? value;
  final bool isPulsing;

  const LiaStatusIndicator({
    Key? key,
    required this.color,
    required this.label,
    this.value,
    this.isPulsing = false,
  }) : super(key: key);

  AgentStatusModel? _resolveAgentStatus(BuildContext context) {
    if (label != 'N/A') return null;

    final row = context.findAncestorWidgetOfExactType<Row>();
    if (row == null || row.children.isEmpty) return null;

    final firstChild = row.children.first;
    if (firstChild is! Flexible || firstChild.child is! Text) return null;

    final agentName = (firstChild.child as Text).data;
    if (agentName == null) return null;

    const supportedAgents = {
      'Career Agent',
      'CV Expert',
      'ATS Analyzer',
      'Job Hunter',
      'LinkedIn Optimizer',
      'Cover Letter AI',
      'Interview Coach',
      'Negotiation Coach',
    };

    if (!supportedAgents.contains(agentName)) return null;

    try {
      final snapshot = context.read<MissionProvider>().snapshot;
      if (snapshot == null) return null;

      final target = agentName.trim().toLowerCase();
      for (final status in snapshot.agentStatuses) {
        if (status.name.trim().toLowerCase() == target) {
          return status;
        }
      }
    } catch (_) {
      // This indicator is also used outside Command Center where
      // MissionProvider may not be present in the widget tree.
    }

    return null;
  }

  @override
  Widget build(BuildContext context) {
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    final colors = context.liaColors;

    final resolvedAgent = _resolveAgentStatus(context);
    final resolvedLabel = resolvedAgent == null
        ? label
        : _displayStatus(resolvedAgent);
    final resolvedColor = resolvedAgent == null
        ? color
        : _statusColor(colors, resolvedAgent);
    final resolvedPulsing = resolvedAgent != null &&
            _isRunning(resolvedAgent.status)
        ? true
        : isPulsing;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (resolvedPulsing)
          _PulsingDot(color: resolvedColor)
        else
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: resolvedColor,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: resolvedColor.withValues(alpha: 0.5),
                  blurRadius: 4,
                  spreadRadius: 1,
                ),
              ],
            ),
          ),
        SizedBox(width: spacings.sm),
        Text(
          resolvedLabel,
          style: typography.bodyMedium.copyWith(color: colors.textSecondary),
        ),
        if (value != null) ...[
          SizedBox(width: spacings.xs),
          Text(
            value!,
            style: typography.bodyMedium.copyWith(
              color: colors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ],
    );
  }

  bool _isRunning(String status) {
    final normalized = status.trim().toLowerCase().replaceAll('_', ' ');
    return normalized == 'running' ||
        normalized == 'processing' ||
        normalized == 'executing';
  }

  String _displayStatus(AgentStatusModel status) {
    final normalized = status.status.trim().toLowerCase().replaceAll('_', ' ');
    switch (normalized) {
      case 'completed':
      case 'complete':
      case 'success':
        return 'READY';
      case 'running':
      case 'processing':
      case 'executing':
        return '${status.progress}%';
      case 'failed':
      case 'error':
        return 'ERROR';
      case 'paused':
        return 'PAUSED';
      case 'skipped':
        return 'SKIPPED';
      default:
        return status.progress > 0
            ? '${status.progress}%'
            : status.status.toUpperCase();
    }
  }

  Color _statusColor(LiaColors colors, AgentStatusModel status) {
    final normalized = status.status.trim().toLowerCase().replaceAll('_', ' ');
    switch (normalized) {
      case 'completed':
      case 'complete':
      case 'success':
        return colors.success;
      case 'failed':
      case 'error':
        return colors.error;
      case 'running':
      case 'processing':
      case 'executing':
        return colors.accentPrimary;
      default:
        return status.progress > 0 ? colors.accentPrimary : colors.textSecondary;
    }
  }
}

class _PulsingDot extends StatefulWidget {
  final Color color;
  const _PulsingDot({required this.color});

  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: widget.color,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: widget.color.withValues(alpha: _controller.value * 0.8),
                blurRadius: 8,
                spreadRadius: 2,
              ),
            ],
          ),
        );
      },
    );
  }
}
