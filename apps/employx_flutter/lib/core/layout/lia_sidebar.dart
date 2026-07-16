import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class LiaSidebar extends StatelessWidget {
  final bool isCollapsed;
  final VoidCallback onToggle;
  final int selectedIndex;
  final Function(int) onItemSelected;

  const LiaSidebar({
    Key? key,
    required this.isCollapsed,
    required this.onToggle,
    required this.selectedIndex,
    required this.onItemSelected,
  }) : super(key: key);

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
          right: BorderSide(color: colors.border, width: 1),
        ),
      ),
      child: Column(
        children: [
          // Logo & Toggle Area
          Container(
            height: 72,
            padding: EdgeInsets.symmetric(horizontal: spacings.md),
            child: Row(
              mainAxisAlignment: isCollapsed 
                ? MainAxisAlignment.center 
                : MainAxisAlignment.spaceBetween,
              children: [
                if (!isCollapsed)
                  Text(
                    'LIA-EmployX',
                    style: typography.h2.copyWith(
                      color: colors.textPrimary,
                      letterSpacing: 2,
                    ),
                  ),
                IconButton(
                  icon: Icon(
                    isCollapsed ? Icons.menu : Icons.chevron_left,
                    color: colors.textSecondary,
                  ),
                  onPressed: onToggle,
                  tooltip: isCollapsed ? 'Expandir' : 'Colapsar',
                ),
              ],
            ),
          ),
          
          SizedBox(height: spacings.lg),

          // Menu Items
          Expanded(
            child: ListView(
              padding: EdgeInsets.symmetric(horizontal: spacings.sm),
              children: [
                _SidebarItem(
                  icon: Icons.home_outlined,
                  label: 'Centro de Comando',
                  isSelected: selectedIndex == 0,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(0),
                ),
                _SidebarItem(
                  icon: Icons.flag_outlined,
                  label: 'Objetivo Profesional',
                  isSelected: selectedIndex == 1,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(1),
                ),
                _SidebarItem(
                  icon: Icons.rocket_launch,
                  label: 'Mission Center',
                  isSelected: selectedIndex == 2,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(2),
                ),
                _SidebarItem(
                  icon: Icons.storefront,
                  label: 'Agent Hub',
                  isSelected: selectedIndex == 3,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(3),
                ),
                _SidebarItem(
                  icon: Icons.description_outlined,
                  label: 'Mis CVs',
                  isSelected: selectedIndex == 4,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(4),
                ),
                _SidebarItem(
                  icon: Icons.work_outline,
                  label: 'Vacantes',
                  isSelected: selectedIndex == 5,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(5),
                ),
                _SidebarItem(
                  icon: Icons.dashboard_outlined,
                  label: 'Dashboard',
                  isSelected: selectedIndex == 6,
                  isCollapsed: isCollapsed,
                  onTap: () => onItemSelected(6),
                ),
              ],
            ),
          ),

          // User Profile Area at bottom
          Padding(
            padding: EdgeInsets.all(spacings.md),
            child: Row(
              mainAxisAlignment: isCollapsed ? MainAxisAlignment.center : MainAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 16,
                  backgroundColor: colors.surfaceHover,
                  child: Text('MT', style: typography.caption),
                ),
                if (!isCollapsed) ...[
                  SizedBox(width: spacings.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Miguel Tovar', style: typography.bodySmall, overflow: TextOverflow.ellipsis),
                        Text('Premium', style: typography.caption.copyWith(color: colors.accentPrimary)),
                      ],
                    ),
                  ),
                  Icon(Icons.settings_outlined, size: 18, color: colors.textSecondary),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

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
        : (_isHovered ? colors.surfaceHover.withOpacity(0.5) : Colors.transparent);
    
    final Color iconColor = widget.isSelected 
        ? colors.textPrimary 
        : colors.textSecondary;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          margin: EdgeInsets.only(bottom: spacings.xs),
          padding: EdgeInsets.symmetric(
            horizontal: widget.isCollapsed ? 0 : spacings.md,
            vertical: spacings.sm,
          ),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: spacings.radiusMd,
          ),
          child: Row(
            mainAxisAlignment: widget.isCollapsed ? MainAxisAlignment.center : MainAxisAlignment.start,
            children: [
              Icon(widget.icon, color: iconColor, size: 20),
              if (!widget.isCollapsed) ...[
                SizedBox(width: spacings.md),
                Expanded(
                  child: Text(
                    widget.label,
                    style: typography.bodyMedium.copyWith(
                      color: widget.isSelected ? colors.textPrimary : colors.textSecondary,
                      fontWeight: widget.isSelected ? FontWeight.w500 : FontWeight.w400,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
