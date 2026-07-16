import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';

class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({Key? key}) : super(key: key);

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen> {
  final List<Map<String, dynamic>> _agents = [
    {
      'title': 'Interview Coach',
      'category': 'Entrevistas',
      'icon': Icons.mic,
      'color': const Color(0xFF8B5CF6), // Purple
      'level': 'Expert',
      'price': 'Gratis',
      'description': 'Simula entrevistas técnicas y de comportamiento. Feedback en tiempo real.',
    },
    {
      'title': 'LinkedIn Networker',
      'category': 'Networking',
      'icon': Icons.people,
      'color': const Color(0xFF0EA5E9), // Sky Blue
      'level': 'Senior',
      'price': '💎 500 Monedas',
      'description': 'Conecta inteligentemente con reclutadores y líderes de ingeniería.',
    },
    {
      'title': 'Salary Negotiator',
      'category': 'Negociación',
      'icon': Icons.handshake,
      'color': const Color(0xFFF59E0B), // Amber
      'level': 'Expert',
      'price': '💎 1200 Monedas',
      'description': 'Estrategias basadas en datos de mercado para aumentar tu oferta salarial.',
    },
    {
      'title': 'Remote Hunter',
      'category': 'Búsqueda',
      'icon': Icons.public,
      'color': const Color(0xFF10B981), // Emerald
      'level': 'Pro',
      'price': '💎 800 Monedas',
      'description': 'Especialista exclusivo en vacantes 100% remotas de empresas US/EU.',
    },
    {
      'title': 'Visa Advisor',
      'category': 'Legal',
      'icon': Icons.airplane_ticket,
      'color': const Color(0xFFEF4444), // Red
      'level': 'Senior',
      'price': '💎 1500 Monedas',
      'description': 'Asesoría de visados O1, H1B y patrocinadores de empleo global.',
    },
    {
      'title': 'Cover Letter Gen',
      'category': 'Aplicación',
      'icon': Icons.draw,
      'color': const Color(0xFF3B82F6), // Blue
      'level': 'Basic',
      'price': 'Gratis',
      'description': 'Redacta cartas de presentación hiper-personalizadas para cada empresa.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Sidebar de Categorías
          Container(
            width: 250,
            color: colors.surface.withAlpha(128),
            padding: EdgeInsets.symmetric(vertical: spacings.xxl, horizontal: spacings.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: Icon(Icons.arrow_back, color: colors.textPrimary),
                      onPressed: () => Navigator.pop(context),
                    ),
                    Text(
                      'Agentes',
                      style: typography.h2.copyWith(color: colors.textPrimary),
                    ),
                  ],
                ),
                SizedBox(height: spacings.xxl),
                _buildCategoryItem(context, 'Todos los Agentes', Icons.apps, true),
                _buildCategoryItem(context, 'Aplicación & CV', Icons.document_scanner, false),
                _buildCategoryItem(context, 'Entrevistas', Icons.mic, false),
                _buildCategoryItem(context, 'Networking', Icons.people, false),
                _buildCategoryItem(context, 'Legal & Visas', Icons.gavel, false),
                _buildCategoryItem(context, 'Negociación', Icons.monetization_on, false),
                
                const Spacer(),
                
                // Saldo IA
                Container(
                  padding: EdgeInsets.all(spacings.md),
                  decoration: BoxDecoration(
                    color: colors.surfaceHover,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: colors.border),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.diamond, color: const Color(0xFF3B82F6), size: 20),
                      SizedBox(width: spacings.sm),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Saldo IA', style: typography.caption.copyWith(color: colors.textSecondary)),
                          Text('2,450 Monedas', style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Grilla Principal (La Tienda)
          Expanded(
            child: CustomScrollView(
              slivers: [
                // Header tipo App Store
                SliverToBoxAdapter(
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: spacings.xxxl, vertical: spacings.xxl),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Descubrir Especialistas',
                          style: typography.display.copyWith(
                            color: colors.textPrimary,
                            fontSize: 40,
                          ),
                        ),
                        SizedBox(height: spacings.sm),
                        Text(
                          'Contrata nuevos Agentes IA para expandir las capacidades de tu equipo.',
                          style: typography.bodyLarge.copyWith(color: colors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ),
                
                // Grilla de Apps
                SliverPadding(
                  padding: EdgeInsets.symmetric(horizontal: spacings.xxxl),
                  sliver: SliverGrid(
                    gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                      maxCrossAxisExtent: 400,
                      mainAxisSpacing: 32,
                      crossAxisSpacing: 32,
                      childAspectRatio: 0.85,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        return _buildAppStoreCard(context, _agents[index]);
                      },
                      childCount: _agents.length,
                    ),
                  ),
                ),
                
                SliverToBoxAdapter(child: const SizedBox(height: 100)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryItem(BuildContext context, String title, IconData icon, bool isSelected) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isSelected ? colors.accentPrimary.withAlpha(25) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: isSelected ? colors.accentPrimary : colors.textSecondary),
          const SizedBox(width: 12),
          Text(
            title,
            style: typography.bodyMedium.copyWith(
              color: isSelected ? colors.accentPrimary : colors.textPrimary,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAppStoreCard(BuildContext context, Map<String, dynamic> agentData) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final isFree = agentData['price'] == 'Gratis';

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: Container(
        decoration: BoxDecoration(
          color: colors.surface,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: colors.border.withAlpha(128)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withAlpha(30),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Cover Half
              Expanded(
                flex: 3,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        (agentData['color'] as Color).withAlpha(100),
                        colors.surface,
                      ],
                    ),
                  ),
                  child: Center(
                    child: Hero(
                      tag: 'icon_${agentData['title']}',
                      child: Container(
                        padding: EdgeInsets.all(spacings.xl),
                        decoration: BoxDecoration(
                          color: colors.background.withAlpha(200),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: (agentData['color'] as Color).withAlpha(128),
                              blurRadius: 30,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: Icon(
                          agentData['icon'],
                          size: 48,
                          color: agentData['color'],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              
              // Details Half
              Expanded(
                flex: 4,
                child: Padding(
                  padding: EdgeInsets.all(spacings.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            agentData['category'],
                            style: typography.caption.copyWith(
                              color: colors.textSecondary,
                              letterSpacing: 1,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: colors.surfaceHover,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              agentData['level'],
                              style: typography.caption.copyWith(color: colors.textPrimary),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: spacings.sm),
                      Text(
                        agentData['title'],
                        style: typography.h3.copyWith(color: colors.textPrimary, fontSize: 20),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: spacings.sm),
                      Expanded(
                        child: Text(
                          agentData['description'],
                          style: typography.bodyMedium.copyWith(color: colors.textSecondary),
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      SizedBox(height: spacings.md),
                      
                      // Install Button
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        decoration: BoxDecoration(
                          color: isFree ? colors.surfaceHover : colors.accentPrimary.withAlpha(25),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isFree ? colors.border : colors.accentPrimary.withAlpha(128),
                          ),
                        ),
                        child: Center(
                          child: Text(
                            isFree ? 'Instalar' : agentData['price'],
                            style: typography.button.copyWith(
                              color: isFree ? colors.textPrimary : colors.accentPrimary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
