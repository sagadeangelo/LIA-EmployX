import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/theme/lia_theme.dart';
import 'core/layout/main_layout.dart';
import 'core/di/service_locator.dart';
import 'core/actions/mission_actions.dart';
import 'core/actions/command_actions.dart';
import 'core/actions/system_actions.dart';

import 'features/dashboard/views/command_center_screen.dart';
import 'features/profile/views/professional_profile_screen.dart';
import 'features/vacancies/views/vacancies_screen.dart';
import 'features/vacancies/providers/vacancy_provider.dart';

import 'core/ui/feature_in_progress.dart';
import 'core/providers/mission_provider.dart';
import 'core/providers/upload_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  setupServiceLocator();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => sl<MissionProvider>(),
        ),
        ChangeNotifierProvider(
          create: (_) => sl<UploadProvider>(),
        ),
        ChangeNotifierProvider(
          create: (_) => sl<MissionActions>(),
        ),
        ChangeNotifierProvider(
          create: (_) => sl<CommandActions>(),
        ),
        ChangeNotifierProvider(
          create: (_) => sl<SystemActions>(),
        ),

        // ============================================================
        // JOB HUNTER
        // ============================================================
        ChangeNotifierProvider(
          create: (_) => VacancyProvider(),
        ),
      ],
      child: const LiaEmployXApp(),
    ),
  );
}

class LiaEmployXApp extends StatelessWidget {
  const LiaEmployXApp({super.key});

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
  const _AppRoot();

  @override
  State<_AppRoot> createState() => _AppRootState();
}

class _AppRootState extends State<_AppRoot> {
  int _selectedIndex = 0;

  static const List<Widget> _screens = [
    // ================================================================
    // 0 — CENTRO DE COMANDO
    // ================================================================
    CommandCenterScreen(),

    // ================================================================
    // 1 — PERFIL PROFESIONAL
    // ================================================================
    ProfessionalProfileScreen(),

    // ================================================================
    // 2 — OBJETIVO PROFESIONAL
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Objetivo Profesional',
    ),

    // ================================================================
    // 3 — MISSION TIMELINE
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Mission Timeline',
    ),

    // ================================================================
    // 4 — MISSION CENTER
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Mission Center',
    ),

    // ================================================================
    // 5 — AGENT HUB
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Agent Hub',
    ),

    // ================================================================
    // 6 — KNOWLEDGE BASE
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Knowledge Base',
    ),

    // ================================================================
    // 7 — VACANTES / JOB HUNTER
    // ================================================================
    VacanciesScreen(),

    // ================================================================
    // 8 — DASHBOARD
    // ================================================================
    FeatureInProgressWidget(
      featureName: 'Dashboard',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return MainLayout(
      selectedIndex: _selectedIndex,
      onItemSelected: (index) {
        if (index < 0 || index >= _screens.length) {
          return;
        }

        setState(() {
          _selectedIndex = index;
        });
      },
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: KeyedSubtree(
          key: ValueKey<int>(_selectedIndex),
          child: _screens[_selectedIndex],
        ),
      ),
    );
  }
}
