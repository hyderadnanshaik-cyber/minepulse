import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/ui_kit.dart';

class NodesScreen extends ConsumerWidget {
  const NodesScreen({super.key});

  Future<void> _locateNode(BuildContext context, int nodeId, String code) async {
    try {
      await apiClient.post('/nodes/$nodeId/locate');
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Locate command sent for ${RiskUtils.displayNodeCode(code)}')),
      );
    } catch (_) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to send locate command')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesProvider);
    final telemetryMap = ref.watch(latestTelemetryProvider);

    return nodesAsync.when(
      data: (nodes) {
        if (nodes.isEmpty) {
          return const EmptyState(
            icon: Icons.sensors_off,
            title: 'No nodes available',
            message: 'Unable to retrieve node data from the API.',
          );
        }
        return ListView.builder(
          padding: const EdgeInsets.all(AppSpacing.pagePadding),
          itemCount: nodes.length,
          itemBuilder: (context, idx) {
            final node = nodes[idx];
            final telemetry = telemetryMap[node.nodeCode];
            final risk = telemetry != null ? RiskUtils.fromTelemetry(telemetry) : node.riskLevel;
            final abnormal = risk == 'HIGH' || risk == 'CRITICAL';
            final lastUpdate = telemetry?.timestamp ?? node.lastSeen;

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: AppCard(
                borderColor: abnormal ? AppColors.forRisk(risk).withOpacity(0.6) : null,
                color: abnormal ? AppColors.bgForRisk(risk) : null,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AppColors.forRisk(risk).withOpacity(0.16),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(Icons.sensors, size: 18, color: AppColors.forRisk(risk)),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                RiskUtils.displayNodeCode(node.nodeCode),
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, letterSpacing: 0.4),
                              ),
                              Text(
                                '${node.status.toUpperCase()}  •  ${node.nodeName}',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ),
                        RiskBadge(riskLevel: risk, score: node.riskScore),
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (telemetry?.crackDetected == true || (telemetry?.crackWidth ?? 0) >= 2.0)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: StatusBadge(
                          label: 'CRACK DETECTED',
                          color: AppColors.riskCritical,
                          icon: Icons.warning_amber_rounded,
                        ),
                      ),
                    Wrap(
                      spacing: 16,
                      runSpacing: 10,
                      children: [
                        _mini('Displacement', telemetry == null ? '—' : '${telemetry.displacement.toStringAsFixed(1)} mm'),
                        _mini('Tilt', telemetry == null ? '—' : '${telemetry.tiltX.toStringAsFixed(2)}°'),
                        _mini('Crack width', telemetry == null ? '—' : '${telemetry.crackWidth.toStringAsFixed(2)} mm'),
                        _mini('Vibration', telemetry == null ? '—' : '${telemetry.vibration.toStringAsFixed(3)} g'),
                        _mini('Battery', '${node.battery.toStringAsFixed(0)}%'),
                        _mini('RSSI', '${node.signalStrength.toStringAsFixed(0)} dBm'),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            lastUpdate == null
                                ? 'No last update'
                                : 'Last update  ${lastUpdate.toLocal().toString().split('.').first}',
                            style: Theme.of(context).textTheme.labelSmall,
                          ),
                        ),
                        OutlinedButton.icon(
                          onPressed: () => _locateNode(context, node.id, node.nodeCode),
                          icon: const Icon(Icons.location_searching, size: 14),
                          label: const Text('Locate', style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
      loading: () => const LoadingState(message: 'Loading nodes…'),
      error: (err, _) => ErrorState(message: 'Unable to retrieve node data\n$err'),
    );
  }

  Widget _mini(String label, String value) {
    return SizedBox(
      width: 140,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
          const SizedBox(height: 2),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
