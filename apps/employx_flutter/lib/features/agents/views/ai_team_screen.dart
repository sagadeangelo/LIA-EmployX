import 'package:flutter/material.dart';
import 'dart:async';
import '../../../core/theme/lia_theme.dart';
import '../models/agent_models.dart';
import '../models/agent_activity.dart';
import '../widgets/agent_card.dart';
import 'agent_hub_screen.dart';

class AiTeamScreen extends StatefulWidget {
  const AiTeamScreen({Key? key}) : super(key: key);

  @override
  State<AiTeamScreen> createState() => _AiTeamScreenState();
}

class _AiTeamScreenState extends State<AiTeamScreen> {
  // Simulated State
  List<AgentModel> _agents = [];
  List<AgentActivity> _activities = [];
  Timer? _simulationTimer;

  int _workingAgentsCount = 0;
  int _missionsActive = 2;
  Duration _timeSaved = const Duration(hours: 4, minutes: 12);
  int _tasksCompletedToday = 145;

  // Agent Specific Actions for Simulation
  final Map<AgentType, List<String>> _agentActions = {
    AgentType.career: [
      'Cargando contexto del usuario',
      'Analizando objetivo profesional',
      'Evaluando brechas de habilidades',
      'Coordinando estrategia laboral',
    ],
    AgentType.cv: [
      'Detectando habilidades clave',
      'Analizando CV',
      'Optimizando ATS',
      'Generando Cover Letter',
    ],
    AgentType.hunter: [
      'Buscando vacantes',
      'Analizando salarios',
      'Comparando ofertas',
      'Encontrando nuevas oportunidades',
    ],
  };

  @override
  void initState() {
    super.initState();
    _initializeMockAgents();
    _startSimulation();
  }

  void _initializeMockAgents() {
    _agents = [
      AgentModel(
        id: '1',
        name: 'Career Agent IA',
        subtitle: 'Coordinador Principal',
        description: 'El cerebro del sistema. Orquesta a todos los demás agentes.',
        icon: Icons.psychology,
        color: const Color(0xFF16C784), // Emerald
        accentColor: const Color(0xFF0F9D67),
        type: AgentType.career,
        status: AgentStatus.active,
        isCore: true,
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.career]![1],
          currentProgress: 0.25,
          lastActionText: _agentActions[AgentType.career]![0],
          nextActionText: _agentActions[AgentType.career]![2],
        )..metrics = AgentMetrics(
          tasksCompleted: 45,
          timeSaved: const Duration(minutes: 120),
          cpuUsage: 0.4,
        )..capabilities = AgentCapabilities(
          skills: ['Estrategia', 'Análisis', 'Coordinación'],
        ),
        
      AgentModel(
        id: '2',
        name: 'CV Expert Agent',
        subtitle: 'Especialista en Currículums',
        description: 'Crea, mejora y optimiza currículums para sistemas ATS.',
        icon: Icons.document_scanner,
        color: const Color(0xFF3B82F6), // Royal Blue
        accentColor: const Color(0xFF2563EB),
        type: AgentType.cv,
        status: AgentStatus.active,
        isCore: true,
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.cv]![1],
          currentProgress: 0.1,
          lastActionText: _agentActions[AgentType.cv]![0],
          nextActionText: _agentActions[AgentType.cv]![2],
        )..metrics = AgentMetrics(
          tasksCompleted: 32,
          timeSaved: const Duration(minutes: 60),
          cpuUsage: 0.8,
        )..capabilities = AgentCapabilities(
          skills: ['Análisis ATS', 'Redacción', 'Cover Letters'],
        ),

      AgentModel(
        id: '3',
        name: 'Job Hunter Agent',
        subtitle: 'Búsqueda Laboral',
        description: 'Busca y compara vacantes automáticamente.',
        icon: Icons.radar,
        color: const Color(0xFFF59E0B), // Orange
        accentColor: const Color(0xD97706),
        type: AgentType.hunter,
        status: AgentStatus.active,
        isCore: true,
      )..execution = AgentExecution(
          currentActionText: _agentActions[AgentType.hunter]![0],
          currentProgress: 0.65,
          lastActionText: 'Inicializando radar',
          nextActionText: _agentActions[AgentType.hunter]![1],
        )..metrics = AgentMetrics(
          tasksCompleted: 68,
          timeSaved: const Duration(minutes: 72),
          cpuUsage: 0.6,
        )..capabilities = AgentCapabilities(
          skills: ['Scraping', 'Filtros avanzados', 'Alertas'],
        ),
    ];
    
    _workingAgentsCount = _agents.length;

    _activities = [
      AgentActivity(
        id: '1',
        agentId: '2',
        agentName: 'CV Expert Agent',
        timestamp: DateTime.now().subtract(const Duration(minutes: 2)),
        title: 'CV Optimizado',
        description: 'Mejoró la compatibilidad ATS al 94%',
        type: ActivityType.success,
      ),
      AgentActivity(
        id: '2',
        agentId: '3',
        agentName: 'Job Hunter Agent',
        timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
        title: 'Vacantes encontradas',
        description: 'Encontró 14 vacantes nuevas',
        type: ActivityType.info,
      ),
      AgentActivity(
        id: '3',
        agentId: '1',
        agentName: 'Career Agent IA',
        timestamp: DateTime.now().subtract(const Duration(minutes: 8)),
        title: 'Estrategia lista',
        description: 'Terminó la estrategia laboral',
        type: ActivityType.success,
      ),
    ];
  }

  void _startSimulation() {
    _simulationTimer = Timer.periodic(const Duration(seconds: 4), (timer) {
      if (!mounted) return;
      
      setState(() {
        for (var agent in _agents) {
          double newProgress = agent.execution.currentProgress + 0.25;
          if (newProgress >= 1.0) {
            newProgress = 0.0;
            // Shift actions cyclically based on specific tasks
            final actions = _agentActions[agent.type]!;
            int currentIndex = actions.indexOf(agent.execution.currentActionText);
            if (currentIndex == -1) currentIndex = 0;
            
            int nextIndex = (currentIndex + 1) % actions.length;
            int nextNextIndex = (nextIndex + 1) % actions.length;

            agent.execution.lastActionText = agent.execution.currentActionText;
            agent.execution.currentActionText = actions[nextIndex];
            agent.execution.nextActionText = actions[nextNextIndex];
            
            // Randomly update status for Career Agent to show "Coordinating" effect
            if (agent.type == AgentType.career) {
              agent.status = (timer.tick % 3 == 0) ? AgentStatus.coordinating : AgentStatus.active;
            }
          }
          agent.execution.currentProgress = newProgress;
        }
        
        // Add random activity every 8 ticks
        if (timer.tick % 8 == 0) {
          _activities.insert(0, AgentActivity(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            agentId: '3',
            agentName: 'Job Hunter Agent',
            timestamp: DateTime.now(),
            title: 'Análisis de mercado',
            description: 'Encontró nuevas oportunidades remotas de alto nivel',
            type: ActivityType.info,
          ));
          if (_activities.length > 10) _activities.removeLast();
        }
      });
    });
  }

  @override
  void dispose() {
    _simulationTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(spacings.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Premium Header
            Container(
              padding: EdgeInsets.symmetric(vertical: spacings.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Mi Equipo de Agentes IA',
                    style: typography.display.copyWith(
                      color: colors.textPrimary,
                      fontSize: 40,
                    ),
                  ),
                  SizedBox(height: spacings.sm),
                  Text(
                    '"Tus agentes trabajan continuamente para ayudarte a conseguir mejores oportunidades laborales."',
                    style: typography.bodyLarge.copyWith(
                      color: colors.textSecondary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: spacings.xl),

            // Summary Stats - Glassmorphic
            Container(
              padding: EdgeInsets.all(spacings.lg),
              decoration: BoxDecoration(
                color: colors.surface.withOpacity(0.5),
                borderRadius: spacings.radiusLg,
                border: Border.all(color: colors.border.withOpacity(0.5)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatItem(context, Icons.memory, 'Agentes instalados', '${_agents.length}', null),
                  _buildStatItem(context, Icons.bolt, 'Agentes trabajando', '$_workingAgentsCount', colors.accentPrimary),
                  _buildStatItem(context, Icons.rocket_launch, 'Misiones activas', '$_missionsActive', const Color(0xFF16C784)),
                  _buildStatItem(context, Icons.timer, 'Tiempo ahorrado', '${_timeSaved.inHours}h ${_timeSaved.inMinutes % 60}m', const Color(0xFF3B82F6)),
                  _buildStatItem(context, Icons.task_alt, 'Tareas (Hoy)', '$_tasksCompletedToday', const Color(0xFFF59E0B)),
                ],
              ),
            ),

            SizedBox(height: spacings.xxl),

            // Agents Grid (Using Wrap for fluid layout without hardcoded heights)
            Wrap(
              spacing: spacings.xl,
              runSpacing: spacings.xl,
              children: _agents.map((agent) {
                return SizedBox(
                  width: 380, // Fixed width for each card to keep them identical
                  child: AgentCard(
                    agent: agent,
                    onTap: () {}, // Expansion is handled internally by AgentCard
                  ),
                );
              }).toList(),
            ),

            SizedBox(height: spacings.xxl),
            Divider(color: colors.border),
            SizedBox(height: spacings.xl),

            // Premium Timeline
            Text(
              'Actividad Reciente',
              style: typography.h2.copyWith(color: colors.textPrimary),
            ),
            SizedBox(height: spacings.xl),
            
            Container(
              padding: EdgeInsets.all(spacings.lg),
              decoration: BoxDecoration(
                color: colors.surface,
                borderRadius: spacings.radiusLg,
                border: Border.all(color: colors.border),
              ),
              child: Column(
                children: _activities.asMap().entries.map((entry) {
                  int idx = entry.key;
                  var activity = entry.value;
                  return _buildTimelineItem(context, activity, isLast: idx == _activities.length - 1);
                }).toList(),
              ),
            ),

            SizedBox(height: spacings.xxl),

            // Marketplace Button
            Center(
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: spacings.radiusLg,
                  gradient: LinearGradient(
                    colors: [
                      colors.surfaceHover,
                      colors.surface,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    )
                  ],
                ),
                child: ElevatedButton.icon(
                  onPressed: () {
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
                  icon: Icon(Icons.storefront, size: 24, color: colors.textPrimary),
                  label: Text('Explorar Marketplace'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: EdgeInsets.symmetric(horizontal: spacings.xl, vertical: spacings.lg),
                    textStyle: typography.bodyLarge.copyWith(fontWeight: FontWeight.bold),
                    shape: RoundedRectangleBorder(
                      borderRadius: spacings.radiusLg,
                      side: BorderSide(color: colors.border.withOpacity(0.5)),
                    ),
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 100), // Bottom padding
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(BuildContext context, IconData icon, String title, String value, Color? valueColor) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: colors.textSecondary),
            const SizedBox(width: 8),
            Text(
              title,
              style: typography.caption.copyWith(color: colors.textSecondary),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: typography.display.copyWith(
            fontSize: 28,
            color: valueColor ?? colors.textPrimary,
          ),
        ),
      ],
    );
  }

  Widget _buildTimelineItem(BuildContext context, AgentActivity activity, {bool isLast = false}) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    final diff = DateTime.now().difference(activity.timestamp);
    String timeAgo = 'Hace ${diff.inMinutes} min';
    if (diff.inMinutes == 0) timeAgo = 'Justo ahora';

    Color dotColor = colors.textSecondary;
    if (activity.type == ActivityType.success) dotColor = const Color(0xFF16C784); // Emerald
    if (activity.type == ActivityType.warning) dotColor = const Color(0xFFF59E0B); // Orange
    if (activity.type == ActivityType.error) dotColor = const Color(0xFFEF4444); // Red
    if (activity.type == ActivityType.info) dotColor = const Color(0xFF3B82F6); // Blue

    // Encontrar el agente para usar su icono real
    final agent = _agents.firstWhere((a) => a.id == activity.agentId, orElse: () => _agents.first);
    
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Time
          SizedBox(
            width: 100,
            child: Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                timeAgo,
                style: typography.caption.copyWith(color: colors.textSecondary),
                textAlign: TextAlign.right,
              ),
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Timeline Line & Dot
          Column(
            children: [
              Container(
                margin: const EdgeInsets.only(top: 10),
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: dotColor.withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: dotColor.withOpacity(0.5)),
                ),
                child: Icon(agent.icon, size: 14, color: dotColor),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    color: colors.border.withOpacity(0.5),
                  ),
                ),
            ],
          ),
          
          const SizedBox(width: 16),
          
          // Content
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(top: 12, bottom: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    activity.agentName,
                    style: typography.bodyMedium.copyWith(
                      color: colors.textPrimary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    activity.description,
                    style: typography.bodyMedium.copyWith(color: colors.textSecondary),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
