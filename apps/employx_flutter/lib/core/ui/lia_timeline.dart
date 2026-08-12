import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';
import 'lia_glass_panel.dart';

class LiaTimelineItem {
  final String text;
  final bool isCompleted;
  final String? stage;
  final String? userMessage;
  final String? developerMessage;
  final int duration;
  final bool isError;

  LiaTimelineItem({
    required this.text,
    this.isCompleted = true,
    this.stage,
    this.userMessage,
    this.developerMessage,
    this.duration = 0,
    this.isError = false,
  });
}

class LiaTimeline extends StatelessWidget {
  final List<LiaTimelineItem> items;
  final String emptyText;

  const LiaTimeline({
    Key? key,
    required this.items,
    this.emptyText = 'Sin actividad reciente',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    if (items.isEmpty) {
      return LiaGlassPanel(
        padding: EdgeInsets.all(spacings.lg),
        child: Row(
          children: [
            Icon(Icons.terminal, color: colors.textMuted, size: 20),
            SizedBox(width: spacings.md),
            Text(emptyText, style: typography.bodyMedium.copyWith(color: colors.textMuted)),
          ],
        ),
      );
    }

    // Agrupar por stage
    final Map<String, List<LiaTimelineItem>> grouped = {};
    for (var item in items) {
      final stageKey = item.stage ?? 'GLOBAL';
      grouped.putIfAbsent(stageKey, () => []).add(item);
    }

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: grouped.entries.map((entry) {
          final stage = entry.key;
          final stageItems = entry.value;
          
          return Padding(
            padding: EdgeInsets.only(bottom: spacings.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (stage != 'GLOBAL') ...[
                  Text(
                    stage.replaceAll('_', ' '),
                    style: typography.caption.copyWith(color: colors.accentPrimary, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: spacings.sm),
                ],
                ...stageItems.map((item) {
                  return Padding(
                    padding: EdgeInsets.only(bottom: item == stageItems.last ? 0 : spacings.md),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          margin: const EdgeInsets.only(top: 4),
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: item.isError ? colors.error : (item.isCompleted ? colors.accentPrimary : colors.textMuted),
                              width: 2,
                            ),
                            color: item.isError ? colors.error.withOpacity(0.2) : (item.isCompleted ? colors.accentPrimary.withOpacity(0.2) : Colors.transparent),
                          ),
                        ),
                        SizedBox(width: spacings.md),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.userMessage ?? item.text,
                                style: typography.bodyMedium.copyWith(
                                  color: item.isError ? colors.error : (item.isCompleted ? colors.textPrimary : colors.textSecondary),
                                  fontFamily: 'monospace',
                                ),
                              ),
                              if (item.duration > 0) ...[
                                SizedBox(height: 2),
                                Text(
                                  '${item.duration} ms',
                                  style: typography.caption.copyWith(color: colors.textMuted, fontSize: 10),
                                ),
                              ],
                              if (item.developerMessage != null && item.developerMessage!.isNotEmpty) ...[
                                SizedBox(height: 4),
                                Tooltip(
                                  message: item.developerMessage ?? '',
                                  child: Text(
                                    'Ver detalles tÃ©cnicos',
                                    style: typography.caption.copyWith(color: colors.accentTertiary, decoration: TextDecoration.underline),
                                  ),
                                ),
                              ]
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

