import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaTextField extends StatefulWidget {
  final String? hintText;
  final TextEditingController? controller;
  final bool obscureText;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final String? errorText;
  final void Function(String)? onChanged;
  final int maxLines;

  const LiaTextField({
    Key? key,
    this.hintText,
    this.controller,
    this.obscureText = false,
    this.prefixIcon,
    this.suffixIcon,
    this.errorText,
    this.onChanged,
    this.maxLines = 1,
  }) : super(key: key);

  @override
  State<LiaTextField> createState() => _LiaTextFieldState();
}

class _LiaTextFieldState extends State<LiaTextField> {
  final FocusNode _focusNode = FocusNode();
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      setState(() {
        _isFocused = _focusNode.hasFocus;
      });
    });
  }

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final bool hasError = widget.errorText != null;

    Color borderColor = Colors.transparent;
    if (hasError) {
      borderColor = colors.error;
    } else if (_isFocused) {
      borderColor = colors.accentPrimary.withOpacity(0.5);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            color: _isFocused ? colors.surface : colors.surfaceHover,
            borderRadius: spacings.radiusSm,
            border: Border.all(
              color: borderColor,
              width: 1.5,
            ),
          ),
          child: TextField(
            controller: widget.controller,
            focusNode: _focusNode,
            obscureText: widget.obscureText,
            onChanged: widget.onChanged,
            maxLines: widget.maxLines,
            style: typography.bodyMedium.copyWith(color: colors.textPrimary),
            cursorColor: colors.accentPrimary,
            decoration: InputDecoration(
              hintText: widget.hintText,
              hintStyle: typography.bodyMedium.copyWith(color: colors.textMuted),
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(
                horizontal: spacings.md,
                vertical: spacings.md,
              ),
              prefixIcon: widget.prefixIcon != null 
                ? IconTheme(
                    data: IconThemeData(
                      color: _isFocused ? colors.accentPrimary : colors.textMuted,
                      size: 20,
                    ),
                    child: widget.prefixIcon!,
                  )
                : null,
              suffixIcon: widget.suffixIcon,
            ),
          ),
        ),
        if (hasError) ...[
          SizedBox(height: spacings.xs),
          Text(
            widget.errorText!,
            style: typography.caption.copyWith(color: colors.error),
          ),
        ],
      ],
    );
  }
}
