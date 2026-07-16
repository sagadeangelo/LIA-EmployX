import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

enum LiaButtonVariant {
  primary,
  secondary,
  ghost,
}

class LiaButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final LiaButtonVariant variant;
  final IconData? icon;
  final bool isLoading;
  final bool isFullWidth;

  const LiaButton({
    Key? key,
    required this.text,
    this.onPressed,
    this.variant = LiaButtonVariant.primary,
    this.icon,
    this.isLoading = false,
    this.isFullWidth = false,
  }) : super(key: key);

  @override
  State<LiaButton> createState() => _LiaButtonState();
}

class _LiaButtonState extends State<LiaButton> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.98).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    if (widget.onPressed != null && !widget.isLoading) {
      _controller.forward();
    }
  }

  void _handleTapUp(TapUpDetails details) {
    if (widget.onPressed != null && !widget.isLoading) {
      _controller.reverse();
    }
  }

  void _handleTapCancel() {
    if (widget.onPressed != null && !widget.isLoading) {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final bool isDisabled = widget.onPressed == null || widget.isLoading;

    Color backgroundColor;
    Color foregroundColor;
    Border? border;

    switch (widget.variant) {
      case LiaButtonVariant.primary:
        backgroundColor = isDisabled ? colors.surfaceHover : colors.textPrimary;
        foregroundColor = isDisabled ? colors.textMuted : colors.background;
        break;
      case LiaButtonVariant.secondary:
        backgroundColor = _isHovered && !isDisabled ? colors.surfaceHover : Colors.transparent;
        foregroundColor = isDisabled ? colors.textMuted : colors.textPrimary;
        border = Border.all(color: isDisabled ? colors.border : (_isHovered ? colors.borderFocus : colors.border));
        break;
      case LiaButtonVariant.ghost:
        backgroundColor = _isHovered && !isDisabled ? colors.surfaceHover : Colors.transparent;
        foregroundColor = isDisabled ? colors.textMuted : colors.textSecondary;
        break;
    }

    Widget content = Row(
      mainAxisSize: widget.isFullWidth ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (widget.isLoading) ...[
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(foregroundColor),
            ),
          ),
          SizedBox(width: spacings.xs),
        ] else if (widget.icon != null) ...[
          Icon(widget.icon, size: 18, color: foregroundColor),
          SizedBox(width: spacings.xs),
        ],
        Text(
          widget.text,
          style: typography.button.copyWith(color: foregroundColor),
        ),
      ],
    );

    return MouseRegion(
      cursor: isDisabled ? SystemMouseCursors.basic : SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTapDown: _handleTapDown,
        onTapUp: _handleTapUp,
        onTapCancel: _handleTapCancel,
        onTap: widget.isLoading ? null : widget.onPressed,
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeInOut,
            padding: EdgeInsets.symmetric(
              horizontal: spacings.lg,
              vertical: spacings.sm,
            ),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: spacings.radiusMd,
              border: border,
            ),
            child: content,
          ),
        ),
      ),
    );
  }
}
