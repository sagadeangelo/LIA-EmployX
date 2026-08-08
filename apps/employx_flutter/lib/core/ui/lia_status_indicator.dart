import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

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

  @override
  Widget build(BuildContext context) {
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    final colors = context.liaColors;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (isPulsing)
          _PulsingDot(color: color)
        else
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 4, spreadRadius: 1),
              ],
            ),
          ),
        SizedBox(width: spacings.sm),
        Text(label, style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
        if (value != null) ...[
          SizedBox(width: spacings.xs),
          Text(value!, style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.bold)),
        ]
      ],
    );
  }
}

class _PulsingDot extends StatefulWidget {
  final Color color;
  const _PulsingDot({required this.color});

  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 1))..repeat(reverse: true);
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
