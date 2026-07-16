import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';
import 'lia_sidebar.dart';

class MainLayout extends StatefulWidget {
  final Widget child;
  final int selectedIndex;
  final Function(int) onItemSelected;

  const MainLayout({
    Key? key,
    required this.child,
    required this.selectedIndex,
    required this.onItemSelected,
  }) : super(key: key);

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  bool _isSidebarCollapsed = false;

  void _toggleSidebar() {
    setState(() {
      _isSidebarCollapsed = !_isSidebarCollapsed;
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;

    return Scaffold(
      backgroundColor: colors.background,
      body: Row(
        children: [
          // Sidebar
          LiaSidebar(
            isCollapsed: _isSidebarCollapsed,
            onToggle: _toggleSidebar,
            selectedIndex: widget.selectedIndex,
            onItemSelected: widget.onItemSelected,
          ),
          
          // Main Content Area
          Expanded(
            child: Column(
              children: [
                // Minimal Top Bar (Command Palette Hint, etc)
                _TopBar(),
                
                // Actual Page Content
                Expanded(
                  child: ClipRect(
                    child: widget.child,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Container(
      height: 72,
      padding: EdgeInsets.symmetric(horizontal: spacings.xl),
      decoration: BoxDecoration(
        color: colors.background,
        border: Border(
          bottom: BorderSide(color: colors.border, width: 1),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // Command Palette Hint (Cmd + K)
          Container(
            padding: EdgeInsets.symmetric(horizontal: spacings.sm, vertical: spacings.xxs),
            decoration: BoxDecoration(
              color: colors.surfaceHover,
              borderRadius: spacings.radiusSm,
              border: Border.all(color: colors.border),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.search, size: 14, color: colors.textSecondary),
                SizedBox(width: spacings.xs),
                Text('Search', style: typography.caption.copyWith(color: colors.textSecondary)),
                SizedBox(width: spacings.md),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                  decoration: BoxDecoration(
                    color: colors.surface,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text('⌘K', style: typography.caption.copyWith(fontSize: 10, color: colors.textMuted)),
                ),
              ],
            ),
          ),
          SizedBox(width: spacings.md),
          IconButton(
            icon: Icon(Icons.notifications_none, color: colors.textSecondary),
            onPressed: () {},
          ),
        ],
      ),
    );
  }
}
