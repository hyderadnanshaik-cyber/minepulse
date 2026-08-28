import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/alert_provider.dart';
import '../../widgets/risk_badge.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertListProvider);

    return Scaffold(
      body: alerts.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.safeEmerald.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check_circle_outline, size: 48, color: AppTheme.safeEmerald),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'All 20 Stations Nominal',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Zero active geotechnical hazard alerts in PostgreSQL',
                    style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: alerts.length,
              itemBuilder: (context, idx) {
                final alert = alerts[idx];
                final isCritical = alert.severity.toUpperCase() == 'CRITICAL';

                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isCritical ? const Color(0xFFFEF2F2) : Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isCritical ? AppTheme.criticalRed.withOpacity(0.4) : AppTheme.borderSubtle,
                      width: isCritical ? 1.5 : 1,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Icon(
                                isCritical ? Icons.warning_rounded : Icons.info_outline,
                                color: isCritical ? AppTheme.criticalRed : AppTheme.warningAmber,
                                size: 18,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                alert.nodeId,
                                style: const TextStyle(fontWeight: FontWeight.w900, fontFamily: 'monospace'),
                              ),
                            ],
                          ),
                          RiskBadge(riskLevel: alert.severity, score: alert.riskScore),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        alert.title,
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        alert.message,
                        style: const TextStyle(fontSize: 12, color: Color(0xFF475569), height: 1.3),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            alert.detectedAt.toLocal().toString().substring(0, 19),
                            style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8), fontFamily: 'monospace'),
                          ),
                          if (alert.status == 'DETECTED' || alert.status == 'ACTIVE')
                            ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: isCritical ? AppTheme.criticalRed : AppTheme.primaryBlue,
                                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                              ),
                              onPressed: () {
                                ref.read(alertListProvider.notifier).acknowledgeAlert(alert.id);
                              },
                              child: const Text('Acknowledge', style: TextStyle(fontSize: 11)),
                            ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
