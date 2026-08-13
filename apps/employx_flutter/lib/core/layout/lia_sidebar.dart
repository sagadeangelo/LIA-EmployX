import 'package:flutter/material.dart';

import '../theme/lia_theme.dart';

class LiaSidebar extends StatelessWidget {
  final bool isCollapsed;
  final VoidCallback onToggle;
  final int selectedIndex;
  final Function(int) onItemSelected;

  const LiaSidebar({
    super.key,
    required this.isCollapsed,
    required this.onToggle,
    required this.selectedIndex,
    required this.onItemSelected,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    final typography = context.liaTypography;

    final double width = isCollapsed ? 80.0 : 260.0;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
      width: width,
      decoration: BoxDecoration(
        color: colors.surface,
        border: Border(
          right: BorderSide(
            color: colors.border,
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          // ============================================================
          // LOGO / TOGGLE
          // ============================================================
          SizedBox(
            height: 72,
            child: Padding(
              padding: EdgeInsets.symmetric(
                horizontal: isCollapsed ? 0 : spacings.md,
              ),
              child: isCollapsed
                  ? Center(
                      child: IconButton(
                        constraints: const BoxConstraints(
                          minWidth: 40,
                          minHeight: 40,
                          maxWidth: 40,
                          maxHeight: 40,
                        ),
                        padding: EdgeInsets.zero,
                        icon: Icon(
                          Icons.menu,
                          color: colors.textSecondary,
                        ),
                        onPressed: onToggle,
                        tooltip: 'Expandir',
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: Text(
                            'LIA-EmployX',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: typography.h2.copyWith(
                              color: colors.textPrimary,
                              letterSpacing: 2,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton(
                          constraints: const BoxConstraints(
                            minWidth: 40,
                            minHeight: 40,
                          ),
                          padding: EdgeInsets.zero,
                          icon: Icon(
                            Icons.chevron_left,
                            color: colors.textSecondary,
                          ),
                          onPressed: onToggle,
                          tooltip: 'Colapsar',
                        ),
                      ],
                    ),
            ),
          ),

          SizedBox(height: spacings.lg),

          // ============================================================
          // MENU
          // ============================================================
          Expanded(
            child: ListView(
              padding: EdgeInsets.symmetric(
                horizontal: isCollapsed ? 8 : spacings.sm,
              ),
              children: [
                // ========================================================
                // 0 — CENTRO DE COMANDO
                // ========================================================
                _SidebarItem(
                  icon: Icons.home_outlined,
                  label: 'Centro de Comando',
                  isSelected: selectedIndex == 0,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(0),
                ),

                // ========================================================
                // 1 — PERFIL PROFESIONAL
                // ========================================================
                _SidebarItem(
                  icon: Icons.person_outline,
                  label: 'Perfil Profesional',
                  isSelected: selectedIndex == 1,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(1),
                ),

                // ========================================================
                // 2 — MIS CVs
                // ========================================================
                _SidebarItem(
                  icon: Icons.description_outlined,
                  label: 'Mis CVs',
                  isSelected: selectedIndex == 2,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(2),
                ),

                // ========================================================
                // 3 — OBJETIVO PROFESIONAL
                // ========================================================
                _SidebarItem(
                  icon: Icons.flag_outlined,
                  label: 'Objetivo Profesional',
                  isSelected: selectedIndex == 3,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(3),
                ),

                // ========================================================
                // 4 — MISSION TIMELINE
                // ========================================================
                _SidebarItem(
                  icon: Icons.timeline,
                  label: 'Mission Timeline',
                  isSelected: selectedIndex == 4,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(4),
                ),

                // ========================================================
                // 5 — MISSION CENTER
                // ========================================================
                _SidebarItem(
                  icon: Icons.rocket_launch,
                  label: 'Mission Center',
                  isSelected: selectedIndex == 5,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(5),
                ),

                // ========================================================
                // 6 — AGENT HUB
                // ========================================================
                _SidebarItem(
                  icon: Icons.storefront,
                  label: 'Agent Hub',
                  isSelected: selectedIndex == 6,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(6),
                ),

                // ========================================================
                // 7 — KNOWLEDGE BASE
                // ========================================================
                _SidebarItem(
                  icon: Icons.library_books,
                  label: 'Knowledge Base',
                  isSelected: selectedIndex == 7,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(7),
                ),

                // ========================================================
                // 8 — VACANTES / JOB HUNTER
                // ========================================================
                _SidebarItem(
                  icon: Icons.work_outline,
                  label: 'Vacantes',
                  isSelected: selectedIndex == 8,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(8),
                ),

                // ========================================================
                // 9 — DASHBOARD
                // ========================================================
                _SidebarItem(
                  icon: Icons.dashboard_outlined,
                  label: 'Dashboard',
                  isSelected: selectedIndex == 9,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(9),
                ),
              ],
            ),
          ),

          // ============================================================
          // USER PROFILE
          // ============================================================
          Padding(
            padding: EdgeInsets.all(
              isCollapsed ? 8 : spacings.md,
            ),
            child: isCollapsed
                ? Center(
                    child: Tooltip(
                      message: 'Miguel Tovar — Premium',
                      child: CircleAvatar(
                        radius: 16,
                        backgroundColor: colors.surfaceHover,
                        child: Text(
                          'MT',
                          style: typography.caption,
                        ),
                      ),
                    ),
                  )
                : Row(
                    children: [
                      CircleAvatar(
                        radius: 16,
                        backgroundColor: colors.surfaceHover,
                        child: Text(
                          'MT',
                          style: typography.caption,
                        ),
                      ),
                      SizedBox(width: spacings.sm),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              'Miguel Tovar',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: typography.bodySmall,
                            ),
                            Text(
                              'Premium',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: typography.caption.copyWith(
                                color: colors.accentPrimary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(
                        Icons.settings_outlined,
                        size: 18,
                        color: colors.textSecondary,
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

// ==========================================================================
// SIDEBAR ITEM
// ==========================================================================

class _SidebarItem extends StatefulWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final bool isCollapsed;
  final VoidCallback onTap;

  const _SidebarItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.isCollapsed,
    required this.onTap,
  });

  @override
  State<_SidebarItem> createState() => _SidebarItemState();
}

class _SidebarItemState extends State<_SidebarItem> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;
    final typography = context.liaTypography;

    final Color bgColor = widget.isSelected
        ? colors.surfaceHover
        : (_isHovered
            ? colors.surfaceHover.withValues(alpha: 0.5)
            : Colors.transparent);

    final Color iconColor = widget.isSelected
        ? colors.textPrimary
        : colors.textSecondary;

    final Widget item = AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      margin: EdgeInsets.only(
        bottom: spacings.xs,
      ),
      padding: EdgeInsets.symmetric(
        horizontal: widget.isCollapsed ? 0 : spacings.md,
        vertical: spacings.sm,
      ),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: spacings.radiusMd,
      ),
      child: widget.isCollapsed
          ? Center(
              child: Icon(
                widget.icon,
                color: iconColor,
                size: 20,
              ),
            )
          : Row(
              children: [
                Icon(
                  widget.icon,
                  color: iconColor,
                  size: 20,
                ),
                SizedBox(width: spacings.md),
                Expanded(
                  child: Text(
                    widget.label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: typography.bodyMedium.copyWith(
                      color: widget.isSelected
                          ? colors.textPrimary
                          : colors.textSecondary,
                      fontWeight: widget.isSelected
                          ? FontWeight.w500
                          : FontWeight.w400,
                    ),
                  ),
                ),
              ],
            ),
    );

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) {
        setState(() {
          _isHovered = true;
        });
      },
      onExit: (_) {
        setState(() {
          _isHovered = false;
        });
      },
      child: GestureDetector(
        onTap: widget.onTap,
        child: widget.isCollapsed
            ? Tooltip(
                message: widget.label,
                waitDuration: const Duration(milliseconds: 350),
                child: item,
              )
            : item,
      ),
    );
  }
}