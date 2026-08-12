import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';

class MissionTimelineScreen extends StatelessWidget {
  const MissionTimelineScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Scaffold(
      backgroundColor: colors.background,
      body: Center(
        child: Text(
          'Mission Timeline (En Construcción)',
          style: typography.h2.copyWith(color: colors.textPrimary),
        ),
      ),
    );
  }
}
