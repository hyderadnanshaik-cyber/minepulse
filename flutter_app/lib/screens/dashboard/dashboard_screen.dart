import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/localization/app_localizations.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../providers/telemetry_provider.dart';
import '../../providers/node_provider.dart';
import '../../providers/alert_provider.dart';
import '../../widgets/metric_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/subsidence_alert_dialog.dart';
import '../telemetry/telemetry_screen.dart';
import '../gis/gis_map_screen.dart';
import '../alerts/alerts_screen.dart';
import '../nodes/nodes_screen.dart';
import '../ai/ai_analytics_screen.dart';
import '../gateway/gateway_screen.dart';
import '../reports/reports_screen.dart';
import '../settings/settings_screen.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _currentNavIndex = 0;
  bool _alertModalShown = false;

  Future<void> _triggerScenario(String mode) async {
    try {
      await apiClient.post(ApiConstants.scenarioTrigger, data: {'mode': mode});
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(mode == 'ANOMALY_NODE_03'
              ? '⚡ SIH Demo: Triggered Critical Subsidence Anomaly on NODE-03'
              : '✅ Reset all 20 nodes to nominal DGMS safe parameters'),
          backgroundColor: mode == 'ANOMALY_NODE_03' ? AppTheme.criticalRed : AppTheme.safeEmerald,
        ),
      );
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final telemetryMap = ref.watch(latestTelemetryProvider);
    final alerts = ref.watch(alertListProvider);
    final nodesAsync = ref.watch(nodesProvider);

    // Check for incoming critical alerts
    if (alerts.isNotEmpty && !_alertModalShown) {
      final criticalAlert = alerts.firstWhere(
        (a) => a.severity == 'CRITICAL' && (a.status == 'DETECTED' || a.status == 'ACTIVE'),
        orElse: () => alerts.first,
      );
      if (criticalAlert.severity == 'CRITICAL') {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted && !_alertModalShown) {
            setState(() => _alertModalShown = true);
            showDialog(
              context: context,
              barrierDismissible: true,
              builder: (ctx) => SubsidenceAlertDialog(
                alert: criticalAlert,
                onAcknowledge: () {
                  ref.read(alertListProvider.notifier).acknowledgeAlert(criticalAlert.id);
                  Navigator.of(ctx).pop();
                },
                onViewGis: () {
                  Navigator.of(ctx).pop();
                  setState(() => _currentNavIndex = 2); // Switch to GIS
                },
              ),
            );
          }
        });
      }
    }

    // Determine highest risk node
    final node3Telemetry = telemetryMap['NODE_03'];
    final dispVal = node3Telemetry?.displacement ?? 1.2;
    final tiltVal = node3Telemetry?.tiltX ?? 0.05;
    final crackVal = node3Telemetry?.crackWidth ?? 0.0;
    final vibVal = node3Telemetry?.vibration ?? 0.02;

    final isNode3Hazard = dispVal >= 20.0 || tiltVal >= 3.0 || crackVal >= 2.0;

    final pages = [
      _buildDashboardHome(context, l10n, dispVal, tiltVal, crackVal, vibVal, isNode3Hazard, nodesAsync),
      const TelemetryScreen(),
      const GisMapScreen(),
      const AlertsScreen(),
      const NodesScreen(),
      const AiAnalyticsScreen(),
      const GatewayScreen(),
      const ReportsScreen(),
      const SettingsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.primaryBlue,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield_rounded, color: Colors.white, size: 16),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.translate('app_title'),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, letterSpacing: 0.5),
                ),
                Text(
                  'PANEL ALPHA NORTH • 20 NODES ACTIVE',
                  style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.slate[500]),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, size: 20),
            onPressed: () {
              ref.read(latestTelemetryProvider.notifier).fetchInitialTelemetry();
              ref.read(alertListProvider.notifier).fetchAlerts();
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: pages[_currentNavIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentNavIndex,
        onDestinationSelected: (idx) => setState(() => _currentNavIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.show_chart), label: 'Telemetry'),
          NavigationDestination(icon: Icon(Icons.map_outlined), selectedIcon: Icon(Icons.map), label: 'GIS'),
          NavigationDestination(icon: Icon(Icons.notifications_active_outlined), selectedIcon: Icon(Icons.notifications_active), label: 'Alerts'),
          NavigationDestination(icon: Icon(Icons.sensors_outlined), selectedIcon: Icon(Icons.sensors), label: 'Nodes'),
          NavigationDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: 'AI Risk'),
          NavigationDestination(icon: Icon(Icons.router_outlined), selectedIcon: Icon(Icons.router), label: 'Gateway'),
          NavigationDestination(icon: Icon(Icons.assessment_outlined), selectedIcon: Icon(Icons.assessment), label: 'Reports'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }

  Widget _buildDashboardHome(
    BuildContext context,
    AppLocalizations l10n,
    double dispVal,
    double tiltVal,
    double crackVal,
    double vibVal,
    bool isHazard,
    AsyncValue<List<NodeModel>> nodesAsync,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // SIH Scenario Control Panel
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.tune_rounded, color: Colors.amberAccent, size: 16),
                        SizedBox(width: 8),
                        Text(
                          'SIH 2026 Interactive Scenario Simulator',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                    RiskBadge(riskLevel: isHazard ? 'CRITICAL' : 'NORMAL'),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.criticalRed,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 10),
                        ),
                        icon: const Icon(Icons.bolt, size: 16),
                        label: const Text('⚡ Trigger NODE-03 Anomaly', style: TextStyle(fontSize: 11)),
                        onPressed: () => _triggerScenario('ANOMALY_NODE_03'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.white,
                          side: const BorderSide(color: Colors.white24),
                          padding: const EdgeInsets.symmetric(vertical: 10),
                        ),
                        icon: const Icon(Icons.restart_alt, size: 16),
                        label: const Text('Reset All Safe', style: TextStyle(fontSize: 11)),
                        onPressed: () => _triggerScenario('NORMAL'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // 4 Geotechnical KPI Pillars
          const Text(
            'GEOTECHNICAL HAZARD PILLARS (DGMS STANDARDS)',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: Color(0xFF64748B),
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 8),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 1.35,
            children: [
              MetricCard(
                title: l10n.translate('displacement'),
                value: dispVal.toStringAsFixed(1),
                unit: 'mm',
                icon: Icons.compress_rounded,
                iconColor: AppTheme.primaryBlue,
                subtitle: 'DGMS Limit: 25.0 mm',
                isHazard: dispVal >= 25.0,
              ),
              MetricCard(
                title: l10n.translate('strata_tilt'),
                value: tiltVal.toStringAsFixed(2),
                unit: '°',
                icon: Icons.screen_rotation_rounded,
                iconColor: const Color(0xFF7C3AED),
                subtitle: 'DGMS Limit: 3.50°',
                isHazard: tiltVal >= 3.5,
              ),
              MetricCard(
                title: l10n.translate('crack_width'),
                value: crackVal.toStringAsFixed(2),
                unit: 'mm',
                icon: Icons.broken_image_outlined,
                iconColor: AppTheme.highOrange,
                subtitle: 'DGMS Limit: 3.00 mm',
                isHazard: crackVal >= 3.0,
              ),
              MetricCard(
                title: l10n.translate('vibration'),
                value: vibVal.toStringAsFixed(3),
                unit: 'g',
                icon: Icons.vibration_rounded,
                iconColor: const Color(0xFF0D9488),
                subtitle: 'Limit: 0.45 g',
                isHazard: vibVal >= 0.45,
              ),
            ],
          ),
          const SizedBox(height: 20),

          // 20-Node Grid Fleet Matrix
          const Text(
            '20-NODE LORA IN865 MONITORING FLEET',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: Color(0xFF64748B),
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 8),
          nodesAsync.when(
            data: (nodes) => Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: nodes.map((node) {
                  final isTargetNode = node.nodeCode == 'NODE_03' && isHazard;
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: isTargetNode ? const Color(0xFFFEE2E2) : const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: isTargetNode ? AppTheme.criticalRed : const Color(0xFFE2E8F0),
                        width: isTargetNode ? 1.5 : 1,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.sensors,
                          size: 14,
                          color: isTargetNode ? AppTheme.criticalRed : AppTheme.safeEmerald,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          node.nodeCode,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                            color: isTargetNode ? AppTheme.criticalRed : const Color(0xFF0F172A),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (_, __) => const SizedBox(),
          ),
        ],
      ),
    );
  }
}
