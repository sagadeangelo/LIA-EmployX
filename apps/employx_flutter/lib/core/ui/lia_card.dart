import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;
  final bool isHoverable;

  const LiaCard({
    Key? key,
    required this.child,
    this.padding,
    this.onTap,
    this.isHoverable = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    Widget cardContent = Container(
      padding: padding ?? EdgeInsets.all(spacings.lg),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: spacings.radiusLg,
        border: Border.all(
          color: colors.border,
          width: 1,
        ),
      ),
      child: child,
    );

    if (onTap != null || isHoverable) {
      return _HoverableCard(
        onTap: onTap,
        borderRadius: spacings.radiusLg,
        child: cardContent,
      );
    }

    return cardContent;
  }
}

class _HoverableCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final BorderRadius borderRadius;

  const _HoverableCard({
    required this.child,
    this.onTap,
    required this.borderRadius,
  });

  @override
  State<_HoverableCard> createState() => _HoverableCardState();
}

class _HoverableCardState extends State<_HoverableCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: widget.onTap != null ? SystemMouseCursors.click : SystemMouseCursors.basic,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius,
            boxShadow: _isHovered
                ? [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 30,
                      offset: const Offset(0, 10),
                    ),
                  ]
                : [],
          ),
          child: Stack(
            children: [
              widget.child,
              // Sutil overlay al hover
              Positioned.fill(
                child: AnimatedOpacity(
                  opacity: _isHovered ? 0.05 : 0.0,
                  duration: const Duration(milliseconds: 200),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: widget.borderRadius,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
