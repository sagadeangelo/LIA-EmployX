import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/actions/mission_actions.dart';
import '../../../core/providers/mission_provider.dart';
import '../../../core/theme/lia_theme.dart';

class CommandCenterWowScreen extends StatelessWidget {
  const CommandCenterWowScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final actions = context.watch<MissionActions>();
    final mission = context.watch<MissionProvider>().snapshot;
    final profile = actions.currentProfile;
    final ats = _score(profile, true);
    final linkedin = _score(profile, false);
    final cv = _cvScore(profile);
    final skills = profile?.skills.technicalSkills.length ?? 0;
    final languages = profile?.languages.length ?? 0;
    final experience = profile?.experience.length ?? 0;
    final overall = ((ats * .4) + (cv * .35) + (linkedin * .25)).round();

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(children: [
        Positioned.fill(child: CustomPaint(painter: _BackgroundPainter(colors))),
        SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(28, 24, 28, 36),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _hero(context, profile, mission?.mission.status ?? 'READY'),
              const SizedBox(height: 18),
              _kpis(context, ats, cv, skills, languages, experience),
              const SizedBox(height: 18),
              LayoutBuilder(builder: (context, c) {
                if (c.maxWidth < 1050) {
                  return Column(children: [
                    _intelligence(context, overall, ats, cv, linkedin),
                    const SizedBox(height: 18),
                    _health(context, mission, cv),
                    const SizedBox(height: 18),
                    _agents(context, mission),
                    const SizedBox(height: 18),
                    _activity(context, mission),
                  ]);
                }
                return Column(children: [
                  Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Expanded(flex: 6, child: _intelligence(context, overall, ats, cv, linkedin)),
                    const SizedBox(width: 18),
                    Expanded(flex: 4, child: _health(context, mission, cv)),
                  ]),
                  const SizedBox(height: 18),
                  Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Expanded(child: _agents(context, mission)),
                    const SizedBox(width: 18),
                    Expanded(child: _activity(context, mission)),
                  ]),
                ]);
              }),
            ]),
          ),
        ),
      ]),
    );
  }

  Widget _hero(BuildContext context, dynamic profile, String status) {
    final c = context.liaColors;
    final name = profile?.personalInfo.name?.toString().trim();
    final role = profile?.personalInfo.currentPosition?.toString().trim();
    return _Card(glow: c.accentPrimary, child: Row(children: [
      Container(width: 68, height: 68, decoration: BoxDecoration(shape: BoxShape.circle, gradient: LinearGradient(colors: [c.accentPrimary, c.accentSecondary]), boxShadow: [BoxShadow(color: c.accentPrimary.withValues(alpha: .35), blurRadius: 28)]), child: Center(child: Text(_initials(name?.isNotEmpty == true ? name! : 'LIA'), style: GoogleFonts.inter(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w800)))),
      const SizedBox(width: 18),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _eyebrow(c, 'CAREER INTELLIGENCE'),
        const SizedBox(height: 5),
        Text(name?.isNotEmpty == true ? 'Bienvenido, $name' : 'Tu carrera. Un solo centro de control.', style: GoogleFonts.inter(color: c.textPrimary, fontSize: 26, fontWeight: FontWeight.w800)),
        const SizedBox(height: 5),
        Text(role?.isNotEmpty == true ? role! : 'Professional Career Operating System', style: GoogleFonts.inter(color: c.textSecondary, fontSize: 13)),
      ])),
      const SizedBox(width: 18),
      _Pill(status, _statusColor(c, status)),
    ]));
  }

  Widget _kpis(BuildContext context, int ats, int cv, int skills, int languages, int experience) {
    final c = context.liaColors;
    final data = [
      ['ATS', ats == 0 ? '—' : '$ats', Icons.document_scanner_outlined, c.accentTertiary],
      ['CAREER', cv == 0 ? '—' : '$cv', Icons.insights_outlined, c.accentPrimary],
      ['SKILLS', '$skills', Icons.psychology_outlined, c.accentPrimary],
      ['LANGUAGES', '$languages', Icons.language_outlined, c.accentTertiary],
      ['EXPERIENCE', '$experience', Icons.work_history_outlined, c.success],
    ];
    return LayoutBuilder(builder: (context, box) {
      final cols = box.maxWidth < 800 ? 2 : data.length;
      return GridView.builder(shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), itemCount: data.length, gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: cols, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: cols == 2 ? 2.5 : 2.0), itemBuilder: (_, i) {
        final d = data[i];
        return _Kpi(label: d[0] as String, value: d[1] as String, icon: d[2] as IconData, color: d[3] as Color);
      });
    });
  }

  Widget _intelligence(BuildContext context, int overall, int ats, int cv, int linkedin) {
    final c = context.liaColors;
    return _Card(glow: c.accentPrimary, child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _Header('CAREER INTELLIGENCE', 'Professional Readiness', Icons.auto_awesome, c.accentPrimary),
      const SizedBox(height: 20),
      Row(children: [
        SizedBox(width: 170, height: 170, child: CustomPaint(painter: _Ring(overall / 100, c.accentPrimary, c.border), child: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [Text('$overall', style: GoogleFonts.inter(color: c.textPrimary, fontSize: 42, fontWeight: FontWeight.w800)), Text('/100', style: GoogleFonts.inter(color: c.textMuted, fontSize: 11, fontWeight: FontWeight.w700)), const SizedBox(height: 3), Text('OVERALL', style: GoogleFonts.inter(color: c.accentPrimary, fontSize: 9, fontWeight: FontWeight.w800, letterSpacing: 1.4))]))),
        const SizedBox(width: 26),
        Expanded(child: Column(children: [
          _Bar('ATS readiness', ats, c.accentTertiary), const SizedBox(height: 15),
          _Bar('Career strength', cv, c.accentPrimary), const SizedBox(height: 15),
          _Bar('LinkedIn readiness', linkedin, c.accentSecondary), const SizedBox(height: 18),
          Align(alignment: Alignment.centerLeft, child: Text('Estos indicadores ya tienen su espacio visual. ATS, LinkedIn y Job Matching alimentarán los valores reales en las siguientes etapas.', style: GoogleFonts.inter(color: c.textMuted, fontSize: 11, height: 1.45))),
        ])),
      ]),
    ]));
  }

  Widget _health(BuildContext context, dynamic mission, int cv) {
    final c = context.liaColors;
    final progress = ((mission?.progress ?? 0) as num).toDouble();
    return _Card(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _Header('CAREER HEALTH', 'System Pulse', Icons.favorite_outline, c.accentTertiary),
      const SizedBox(height: 18),
      Row(children: [Expanded(child: Text(cv == 0 ? 'Awaiting analysis' : '$cv% readiness', style: GoogleFonts.inter(color: c.textPrimary, fontSize: 21, fontWeight: FontWeight.w800))), _Pill(mission?.mission.status ?? 'READY', _statusColor(c, mission?.mission.status ?? 'READY'))]),
      const SizedBox(height: 16), _Bar('Career score', cv, c.accentPrimary), const SizedBox(height: 20),
      _HealthLine('Mission Runtime', mission?.runtime.online ?? true, c), const SizedBox(height: 11),
      _HealthLine('Database', mission?.health.database ?? true, c), const SizedBox(height: 11),
      _HealthLine('Storage', mission?.health.storage ?? true, c), const SizedBox(height: 17),
      Divider(color: c.border), const SizedBox(height: 10),
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Mission progress', style: GoogleFonts.inter(color: c.textMuted, fontSize: 11)), Text('${progress.round()}%', style: GoogleFonts.inter(color: c.textPrimary, fontWeight: FontWeight.w800, fontSize: 11))]),
      const SizedBox(height: 7), _Progress(progress / 100, c.accentTertiary),
    ]));
  }

  Widget _agents(BuildContext context, dynamic mission) {
    final c = context.liaColors;
    final active = (mission?.runtime.activeAgents ?? const []).map((e) => e.toString()).toSet();
    final names = ['CV Expert', 'Career Agent', 'ATS Analyzer', 'Job Hunter', 'LinkedIn Optimizer', 'Cover Letter AI', 'Interview Coach', 'Negotiation Coach'];
    return _Card(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _Header('AGENT NETWORK', 'Career AI Fleet', Icons.hub_outlined, c.accentPrimary), const SizedBox(height: 16),
      ...names.map((name) => Padding(padding: const EdgeInsets.only(bottom: 9), child: _Agent(name, active.contains(name), c))),
    ]));
  }

  Widget _activity(BuildContext context, dynamic mission) {
    final c = context.liaColors;
    final events = mission?.timeline ?? const [];
    return _Card(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _Header('LIVE ACTIVITY', 'Mission Intelligence', Icons.bolt_outlined, c.accentTertiary), const SizedBox(height: 17),
      if (events.isEmpty) _emptyActivity(c) else ...events.reversed.take(8).map((e) => _Event(e.title.toString(), (e.userMessage ?? e.description).toString(), e.stage?.toString() ?? 'MISSION', e.severity == 'error', c)),
    ]));
  }

  Widget _emptyActivity(dynamic c) => Container(width: double.infinity, padding: const EdgeInsets.all(22), decoration: BoxDecoration(color: c.background.withValues(alpha: .35), borderRadius: BorderRadius.circular(15), border: Border.all(color: c.border)), child: Column(children: [Icon(Icons.radar_outlined, color: c.accentPrimary, size: 34), const SizedBox(height: 10), Text('Mission activity will appear here', style: GoogleFonts.inter(color: c.textPrimary, fontSize: 12, fontWeight: FontWeight.w700)), const SizedBox(height: 5), Text('El centro de comando está listo para recibir los motores de inteligencia.', textAlign: TextAlign.center, style: GoogleFonts.inter(color: c.textMuted, fontSize: 10))]));

  static int _score(dynamic p, bool ats) => p == null ? 0 : ((ats ? p.atsMetrics.atsScore : p.linkedinMetrics.score) as num?)?.round() ?? 0;
  static int _cvScore(dynamic p) => p == null ? 0 : ((p.cvScore as num?)?.round() ?? 0).clamp(0, 100);
  static String _initials(String value) { final p = value.trim().split(RegExp(r'\s+')); return p.length == 1 ? p.first.substring(0, 1).toUpperCase() : '${p.first.substring(0, 1)}${p.last.substring(0, 1)}'.toUpperCase(); }
  static Color _statusColor(dynamic c, String s) => s == 'FAILED' ? c.error : (s == 'COMPLETED' || s == 'COMPLETE' ? c.success : c.accentPrimary);
  static Widget _eyebrow(dynamic c, String text) => Text(text, style: GoogleFonts.inter(color: c.accentPrimary, fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 1.8));
}

class _Card extends StatelessWidget {
  final Widget child; final Color? glow;
  const _Card({required this.child, this.glow});
  @override Widget build(BuildContext context) { final c = context.liaColors; final g = glow ?? c.accentPrimary; return Container(padding: const EdgeInsets.all(21), decoration: BoxDecoration(color: c.surface.withValues(alpha: .72), borderRadius: BorderRadius.circular(22), border: Border.all(color: g.withValues(alpha: glow == null ? .22 : .4)), boxShadow: [BoxShadow(color: g.withValues(alpha: .09), blurRadius: 30), BoxShadow(color: Colors.black.withValues(alpha: .22), blurRadius: 24, offset: const Offset(0, 12))]), child: child); }
}

class _Kpi extends StatelessWidget { final String label, value; final IconData icon; final Color color; const _Kpi({required this.label, required this.value, required this.icon, required this.color}); @override Widget build(BuildContext context) { final c = context.liaColors; return Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: c.surface.withValues(alpha: .62), borderRadius: BorderRadius.circular(16), border: Border.all(color: c.border)), child: Row(children: [Container(width: 36, height: 36, decoration: BoxDecoration(color: color.withValues(alpha: .12), borderRadius: BorderRadius.circular(10)), child: Icon(icon, color: color, size: 18)), const SizedBox(width: 10), Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [Text(label, style: GoogleFonts.inter(color: c.textMuted, fontSize: 8, fontWeight: FontWeight.w800, letterSpacing: .9)), const SizedBox(height: 4), Text(value, style: GoogleFonts.inter(color: c.textPrimary, fontSize: 19, fontWeight: FontWeight.w800))]) ])); } }

class _Header extends StatelessWidget { final String eyebrow, title; final IconData icon; final Color color; const _Header(this.eyebrow, this.title, this.icon, this.color); @override Widget build(BuildContext context) { final c = context.liaColors; return Row(children: [Container(width: 34, height: 34, decoration: BoxDecoration(color: color.withValues(alpha: .11), borderRadius: BorderRadius.circular(10)), child: Icon(icon, color: color, size: 18)), const SizedBox(width: 11), Column(crossAxisAlignment: CrossAxisAlignment.start, children: [_eyebrow(c, eyebrow), const SizedBox(height: 2), Text(title, style: GoogleFonts.inter(color: c.textPrimary, fontSize: 16, fontWeight: FontWeight.w800))])]); } }

class _Pill extends StatelessWidget { final String text; final Color color; const _Pill(this.text, this.color); @override Widget build(BuildContext context) => Container(padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6), decoration: BoxDecoration(color: color.withValues(alpha: .1), borderRadius: BorderRadius.circular(999), border: Border.all(color: color.withValues(alpha: .25))), child: Row(mainAxisSize: MainAxisSize.min, children: [Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)), const SizedBox(width: 6), Text(text, style: GoogleFonts.inter(color: color, fontSize: 8, fontWeight: FontWeight.w800, letterSpacing: .7))])); }

class _Bar extends StatelessWidget { final String label; final int value; final Color color; const _Bar(this.label, this.value, this.color); @override Widget build(BuildContext context) { final c = context.liaColors; return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(label, style: GoogleFonts.inter(color: c.textSecondary, fontSize: 11)), Text('$value', style: GoogleFonts.inter(color: c.textPrimary, fontSize: 11, fontWeight: FontWeight.w800))]), const SizedBox(height: 7), _Progress(value / 100, color)]); } }

class _Progress extends StatelessWidget { final double value; final Color color; const _Progress(this.value, this.color); @override Widget build(BuildContext context) { return ClipRRect(borderRadius: BorderRadius.circular(999), child: Stack(children: [Container(height: 7, color: color.withValues(alpha: .1)), FractionallySizedBox(widthFactor: value.clamp(0, 1), child: Container(height: 7, color: color))])); } }

class _HealthLine extends StatelessWidget { final String label; final bool online; final dynamic c; const _HealthLine(this.label, this.online, this.c); @override Widget build(BuildContext context) { final color = online ? c.success : c.error; return Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(label, style: GoogleFonts.inter(color: c.textSecondary, fontSize: 11)), Row(children: [Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)), const SizedBox(width: 6), Text(online ? 'ONLINE' : 'OFFLINE', style: GoogleFonts.inter(color: color, fontSize: 9, fontWeight: FontWeight.w800))])]); } }

class _Agent extends StatelessWidget { final String name; final bool active; final dynamic c; const _Agent(this.name, this.active, this.c); @override Widget build(BuildContext context) { final color = active ? c.success : c.textMuted; return Container(padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 9), decoration: BoxDecoration(color: c.background.withValues(alpha: .35), borderRadius: BorderRadius.circular(11), border: Border.all(color: c.border)), child: Row(children: [Icon(Icons.smart_toy_outlined, color: color, size: 16), const SizedBox(width: 9), Expanded(child: Text(name, style: GoogleFonts.inter(color: c.textPrimary, fontSize: 11, fontWeight: FontWeight.w600))), Container(width: 6, height: 6, decoration: BoxDecoration(color: color, shape: BoxShape.circle)), const SizedBox(width: 6), Text(active ? 'ACTIVE' : 'STANDBY', style: GoogleFonts.inter(color: color, fontSize: 8, fontWeight: FontWeight.w800, letterSpacing: .7))])); } }

class _Event extends StatelessWidget { final String title, detail, stage; final bool error; final dynamic c; const _Event(this.title, this.detail, this.stage, this.error, this.c); @override Widget build(BuildContext context) { final color = error ? c.error : c.accentPrimary; return Padding(padding: const EdgeInsets.only(bottom: 13), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [Container(margin: const EdgeInsets.only(top: 3), width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle, boxShadow: [BoxShadow(color: color.withValues(alpha: .45), blurRadius: 8)])), const SizedBox(width: 11), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(color: c.textPrimary, fontSize: 11, fontWeight: FontWeight.w700))), Text(stage, style: GoogleFonts.inter(color: color, fontSize: 8, fontWeight: FontWeight.w800))]), const SizedBox(height: 3), Text(detail, maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(color: c.textMuted, fontSize: 9, height: 1.35))]))])); } }

class _BackgroundPainter extends CustomPainter { final dynamic c; _BackgroundPainter(this.c); @override void paint(Canvas canvas, Size size) { final paint = Paint(); for (final item in [[Offset(size.width * .05, size.height * .02), c.accentPrimary, 420.0], [Offset(size.width * .92, size.height * .28), c.accentSecondary, 520.0], [Offset(size.width * .55, size.height * 1.05), c.accentTertiary, 500.0]]) { final center = item[0] as Offset; final color = item[1] as Color; final radius = item[2] as double; paint.shader = RadialGradient(colors: [color.withValues(alpha: .09), Colors.transparent]).createShader(Rect.fromCircle(center: center, radius: radius)); canvas.drawCircle(center, radius, paint); } } @override bool shouldRepaint(covariant _BackgroundPainter oldDelegate) => false; }

class _Ring extends CustomPainter { final double value; final Color color, track; _Ring(this.value, this.color, this.track); @override void paint(Canvas canvas, Size size) { const pi = 3.141592653589793; final center = size.center(Offset.zero); final r = size.shortestSide / 2 - 12; final base = Paint()..style = PaintingStyle.stroke..strokeWidth = 11..strokeCap = StrokeCap.round..color = track.withValues(alpha: .45); final active = Paint()..style = PaintingStyle.stroke..strokeWidth = 11..strokeCap = StrokeCap.round..color = color; canvas.drawCircle(center, r, base); canvas.drawArc(Rect.fromCircle(center: center, radius: r), -pi / 2, pi * 2 * value.clamp(0, 1), false, active); } @override bool shouldRepaint(covariant _Ring oldDelegate) => oldDelegate.value != value; }
