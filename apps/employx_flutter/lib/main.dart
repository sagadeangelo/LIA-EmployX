import 'package:flutter/material.dart';

import 'package:provider/provider.dart';

import 'core/theme/lia_theme.dart';
import 'core/layout/main_layout.dart';
import 'core/di/service_locator.dart';
import 'core/actions/mission_actions.dart';
import 'core/actions/command_actions.dart';
import 'core/actions/system_actions.dart';

import 'features/dashboard/views/command_center_wow_screen.dart';
import 'features/profile/views/professional_profile_screen.dart';
import 'core/ui/feature_in_progress.dart';
import 'core/providers/mission_provider.dart';
import 'core/providers/upload_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  setupServiceLocator();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => sl<MissionActions>()),
        ChangeNotifierProvider(create: (_) => sl<CommandActions>()),
        ChangeNotifierProvider(create: (_) => sl<SystemActions>()),
        ChangeNotifierProvider(create: (_) => sl<MissionProvider>()),
        ChangeNotifierProvider(create: (_) => sl<UploadProvider>()),
      ],
      child: const LiaEmployXApp(),
    ),
  );
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
    CommandCenterWowScreen(),                                      // 0 - Centro de Comando
    ProfessionalProfileScreen(),                                  // 1 - Perfil Profesional
    FeatureInProgressWidget(featureName: 'Objetivo Profesional'), // 2
    FeatureInProgressWidget(featureName: 'Mission Timeline'),     // 3
    FeatureInProgressWidget(featureName: 'Mission Center'),       // 4
    FeatureInProgressWidget(featureName: 'Agent Hub'),            // 5
    FeatureInProgressWidget(featureName: 'Knowledge Base'),       // 6
    FeatureInProgressWidget(featureName: 'Vacantes'),              // 7
    FeatureInProgressWidget(featureName: 'Dashboard'),            // 8
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
