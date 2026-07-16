import 'package:flutter/material.dart';

import 'core/theme/lia_theme.dart';
import 'core/layout/main_layout.dart';

import 'features/dashboard/views/command_center_screen.dart';
import 'features/dashboard/views/professional_goal_screen.dart';
import 'features/agents/views/mission_center_screen.dart';
import 'features/agents/views/marketplace_screen.dart';
import 'features/cvs/views/my_cvs_screen.dart';
import 'features/vacancies/views/vacancies_screen.dart';
import 'features/dashboard/views/dashboard_screen.dart';

void main() {
  // Asegurar que las fuentes se cargan
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LiaEmployXApp());
}

class LiaEmployXApp extends StatelessWidget {
  const LiaEmployXApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LIA EmployX',
      debugShowCheckedModeBanner: false,
      theme: LiaTheme.darkTheme,
      home: const _AppRoot(),
    );
  }
}

class _AppRoot extends StatefulWidget {
  const _AppRoot({Key? key}) : super(key: key);

  @override
  State<_AppRoot> createState() => _AppRootState();
}

class _AppRootState extends State<_AppRoot> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    CommandCenterScreen(),       // 0 - Centro de Comando
    ProfessionalGoalScreen(),    // 1 - Objetivo Profesional
    MissionCenterScreen(),       // 2 - Mission Center (NASA)
    MarketplaceScreen(),         // 3 - Agent Hub
    MyCvsScreen(),               // 4 - Mis CVs
    VacanciesScreen(),           // 5 - Vacantes
    DashboardScreen(),           // 6 - Dashboard
  ];

  @override
  Widget build(BuildContext context) {
    return MainLayout(
      selectedIndex: _selectedIndex,
      onItemSelected: (index) {
        setState(() {
          _selectedIndex = index;
        });
      },
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: _screens[_selectedIndex],
      ),
    );
  }
}
