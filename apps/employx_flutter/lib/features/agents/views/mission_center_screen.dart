import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math' as math;
import '../../../core/theme/lia_theme.dart';
import '../models/agent_models.dart';
import '../models/agent_activity.dart';
import '../widgets/living_agent_node.dart';
import '../widgets/agent_connection_painter.dart';
import 'agent_hub_screen.dart';

class MissionCenterScreen extends StatefulWidget {
  const MissionCenterScreen({Key? key}) : super(key: key);

  @override
  State<MissionCenterScreen> createState() => _MissionCenterScreenState();
}

class _MissionCenterScreenState extends State<MissionCenterScreen> with TickerProviderStateMixin {
  // Models
  List<AgentModel> _agents = [];
  
  // Ticker Activities
  final List<AgentActivity> _recentActivities = [];
  final GlobalKey<AnimatedListState> _listKey = GlobalKey<AnimatedListState>();
  
  // Simulation
  Timer? _simulationTimer;
  double _globalMissionProgress = 0.68;
  
  // Animation for the connections
  late AnimationController _connectionFlowController;

  final Map<AgentType, List<String>> _agentActions = {
    AgentType.career: [
      'Cargando contexto del usuario',
      'Analizando objetivo profesional',
      'Evaluando brechas de habilidades',
      'Diseñando tu estrategia profesional',
    ],
    AgentType.cv: [
      'Cada palabra cuenta',
      'Analizando CV',
      'Optimizando ATS',
      'Generando Cover Letter',
    ],
    AgentType.hunter: [
      'Siempre buscando la siguiente oportunidad',
      'Analizando salarios',
      'Comparando ofertas',
      'Encontrando nuevas vacantes',
    ],
  };

  @override
  void initState() {
    super.initState();
    _initializeAgents();
    
    _connectionFlowController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();

    _startSimulation();
  }

  void _initializeAgents() {
    _agents = [
      AgentModel(
        id: '1',
        name: 'Career Agent IA',
        subtitle: 'Estratega',
        description: 'Diseñando tu estrategia profesional.',
        icon: Icons.psychology,
        color: const Color(0xFF10B981), // Emerald
        accentColor: const Color(0xFF059669),
        type: AgentType.career,
        status: AgentStatus.active,
        connectedTo: '2', // Connects to CV Expert
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.career]![3],
          currentProgress: 0.25,
        ),
        
      AgentModel(
        id: '2',
        name: 'CV Expert Agent',
        subtitle: 'Optimización',
        description: 'Cada palabra cuenta.',
        icon: Icons.document_scanner,
        color: const Color(0xFF3B82F6), // Electric Blue
        accentColor: const Color(0xFF2563EB),
        type: AgentType.cv,
        status: AgentStatus.active,
        connectedTo: '3', // Connects to Job Hunter
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.cv]![2],
          currentProgress: 0.8,
        ),

      AgentModel(
        id: '3',
        name: 'Job Hunter Agent',
        subtitle: 'Explorador',
        description: 'Siempre buscando la siguiente oportunidad.',
        icon: Icons.radar,
        color: const Color(0xFFF59E0B), // Amber
        accentColor: const Color(0xD97706),
        type: AgentType.hunter,
        status: AgentStatus.active,
        connectedTo: null, // End of the line for now
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.hunter]![0],
          currentProgress: 0.4,
        ),
    ];
  }

  void _startSimulation() {
    _simulationTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
      if (!mounted) return;
      
      setState(() {
        // Global progress slowly increments
        if (_globalMissionProgress < 0.99) {
          _globalMissionProgress += 0.001;
        }

        // Agent Progress
        for (var agent in _agents) {
          double newProgress = agent.execution.currentProgress + (math.Random().nextDouble() * 0.15);
          if (newProgress >= 1.0) {
            newProgress = 0.0;
            // Shift actions
            final actions = _agentActions[agent.type]!;
            int currentIndex = actions.indexOf(agent.execution.currentActionText);
            if (currentIndex == -1) currentIndex = 0;
            int nextIndex = (currentIndex + 1) % actions.length;
            agent.execution.currentActionText = actions[nextIndex];
          }
          agent.execution.currentProgress = newProgress;
        }

        // Random Activity Events (Ticker)
        if (timer.tick % 4 == 0) {
          final msgs = [
            '✓ Encontré 4 nuevas vacantes compatibles',
            '✓ ATS Compatibility Score aumentó +8%',
            '✓ Detecté una habilidad faltante: GraphQL',
            '✓ Recruiter en Acme Corp ha respondido',
            '✓ Encontré salario promedio actualizado',
            '✓ Preparando simulación de entrevista',
          ];
          final randomMsg = msgs[math.Random().nextInt(msgs.length)];
          
          final newActivity = AgentActivity(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            agentId: _agents[math.Random().nextInt(_agents.length)].id,
            agentName: '',
            timestamp: DateTime.now(),
            title: randomMsg,
            description: '',
            type: ActivityType.success,
          );
          
          _recentActivities.insert(0, newActivity);
          _listKey.currentState?.insertItem(0, duration: const Duration(milliseconds: 500));
          
          // Keep only last 5 items
          if (_recentActivities.length > 5) {
            final removedItem = _recentActivities.removeLast();
            _listKey.currentState?.removeItem(
              5,
              (context, animation) => _buildTickerItem(removedItem, animation),
              duration: const Duration(milliseconds: 500),
            );
          }
        }
      });
    });
  }

  @override
  void dispose() {
    _simulationTimer?.cancel();
    _connectionFlowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          // Background Gradient (Cybernetic feel)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.topCenter,
                  radius: 1.5,
                  colors: [
                    colors.surfaceHover.withAlpha(128),
                    colors.background,
                  ],
                ),
              ),
            ),
          ),
          
          // Main Scrollable Content
          SingleChildScrollView(
            padding: EdgeInsets.symmetric(horizontal: spacings.xxxl, vertical: spacings.xxl),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // MISSION HEADER
                Text(
                  'MISIÓN ACTUAL',
                  style: typography.caption.copyWith(
                    color: colors.accentPrimary,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                SizedBox(height: spacings.sm),
                Text(
                  'Conseguir empleo Flutter Senior',
                  style: typography.display.copyWith(
                    color: colors.textPrimary,
                    fontSize: 48,
                  ),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: spacings.xl),
                
                // Massive Glowing Progress Bar
                Container(
                  width: 600,
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Progreso Global', style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
                          Text('${(_globalMissionProgress * 100).toInt()}%', style: typography.h2.copyWith(color: colors.textPrimary)),
                        ],
                      ),
                      SizedBox(height: spacings.sm),
                      Container(
                        height: 12,
                        decoration: BoxDecoration(
                          color: colors.surfaceHover,
                          borderRadius: BorderRadius.circular(6),
                          boxShadow: [
                            BoxShadow(
                              color: colors.background,
                              blurRadius: 4,
                            ),
                          ],
                        ),
                        child: Stack(
                          children: [
                            FractionallySizedBox(
                              widthFactor: _globalMissionProgress,
                              child: Container(
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(6),
                                  gradient: LinearGradient(
                                    colors: [
                                      colors.accentSecondary,
                                      colors.accentPrimary,
                                    ],
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: colors.accentPrimary.withAlpha(128),
                                      blurRadius: 20,
                                      spreadRadius: 2,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: spacings.xxxl),

                // THE PIPELINE (Agents connecting vertically)
                Container(
                  width: 600,
                  child: ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _agents.length,
                    itemBuilder: (context, index) {
                      final agent = _agents[index];
                      final hasNext = index < _agents.length - 1;
                      final nextAgent = hasNext ? _agents[index + 1] : null;

                      return Column(
                        children: [
                          LivingAgentNode(
                            agent: agent,
                            isConnectedAbove: index > 0,
                            isConnectedBelow: hasNext,
                          ),
                          // Connection Line Drawing
                          if (hasNext && nextAgent != null)
                            AnimatedBuilder(
                              animation: _connectionFlowController,
                              builder: (context, child) {
                                return Container(
                                  height: 80,
                                  width: 400, // Provides space for the custom painter
                                  child: CustomPaint(
                                    painter: AgentConnectionPainter(
                                      start: const Offset(200, 0), // Centered top
                                      end: const Offset(200, 80),  // Centered bottom
                                      color: agent.color, // Takes the color of the source agent
                                      progress: _connectionFlowController.value,
                                    ),
                                  ),
                                );
                              },
                            ),
                        ],
                      );
                    },
                  ),
                ),

                SizedBox(height: spacings.xxxl),

                // APP STORE LINK
                Center(
                  child: MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          PageRouteBuilder(
                            pageBuilder: (context, animation, secondaryAnimation) => const AgentHubScreen(),
                            transitionsBuilder: (context, animation, secondaryAnimation, child) {
                              return FadeTransition(opacity: animation, child: child);
                            },
                          ),
                        );
                      },
                      child: Container(
                        padding: EdgeInsets.symmetric(horizontal: spacings.xl, vertical: spacings.lg),
                        decoration: BoxDecoration(
                          color: colors.surface.withAlpha(128), // Glass effect
                          borderRadius: BorderRadius.circular(100),
                          border: Border.all(color: colors.border.withAlpha(100)),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withAlpha(50),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.add_circle_outline, color: colors.textPrimary),
                            SizedBox(width: spacings.md),
                            Text(
                              'Expandir Equipo de Agentes IA',
                              style: typography.button.copyWith(
                                color: colors.textPrimary,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 100),
              ],
            ),
          ),
          
          // EPHEMERAL ACTIVITY TICKER (Bottom Right Overlay)
          Positioned(
            bottom: spacings.xl,
            right: spacings.xl,
            width: 380,
            height: 300,
            child: ShaderMask(
              shaderCallback: (Rect bounds) {
                return LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Colors.white, Colors.white],
                  stops: const [0.0, 0.4, 1.0],
                ).createShader(bounds);
              },
              child: AnimatedList(
                key: _listKey,
                initialItemCount: _recentActivities.length,
                reverse: true,
                itemBuilder: (context, index, animation) {
                  return _buildTickerItem(_recentActivities[index], animation);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTickerItem(AgentActivity activity, Animation<double> animation) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    // Smooth entrance from bottom
    final offsetAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.5),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: animation,
      curve: Curves.easeOutQuint,
    ));

    return SlideTransition(
      position: offsetAnimation,
      child: FadeTransition(
        opacity: animation,
        child: Container(
          margin: const EdgeInsets.only(top: 8.0),
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          decoration: BoxDecoration(
            color: colors.surface.withAlpha(230),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF10B981).withAlpha(50)), // Success glow border
            boxShadow: [
              BoxShadow(
                color: Colors.black.withAlpha(50),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Icon(Icons.check_circle, size: 16, color: const Color(0xFF10B981)),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  activity.title.replaceAll('✓ ', ''),
                  style: typography.bodyMedium.copyWith(color: colors.textPrimary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
