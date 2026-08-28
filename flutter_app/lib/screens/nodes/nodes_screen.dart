import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/network/api_client.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/risk_badge.dart';

class NodesScreen extends ConsumerWidget {
  const NodesScreen({super.key});

  Future<void> _locateNode(BuildContext context, int nodeId, String code) async {
    try {
      await apiClient.post('/nodes/$nodeId/locate');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('📡 LoRa Downlink Broadcasted: Buzzer & LED Activated for $code'),
          backgroundColor: AppTheme.primaryBlue,
        ),
      );
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesProvider);
    final telemetryMap = ref.watch(latestTelemetryProvider);

    return Scaffold(
      body: nodesAsync.when(
        data: (nodes) => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: nodes.length,
          itemBuilder: (context, idx) {
            final node = nodes[idx];
            final telemetry = telemetryMap[node.nodeCode];
            final isHazard = (telemetry?.displacement ?? 0.0) >= 20.0 || (telemetry?.crackWidth ?? 0.0) >= 2.0;

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isHazard ? AppTheme.criticalRed.withOpacity(0.4) : AppTheme.borderSubtle,
                  width: isHazard ? 1.5 : 1,
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
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: isHazard ? const Color(0xFFFEE2E2) : const Color(0xFFEFF6FF),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Icon(
                              Icons.sensors,
                              size: 18,
                              color: isHazard ? AppTheme.criticalRed : AppTheme.primaryBlue,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                node.nodeCode,
                                style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14, fontFamily: 'monospace'),
                              ),
                              const Text(
                                'ESP32+MPU9250+BME280+ADS1115',
                                style: TextStyle(fontSize: 9, color: Color(0xFF64748B), fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ],
                      ),
                      RiskBadge(riskLevel: isHazard ? 'CRITICAL' : 'NORMAL'),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // Sensor Values Row
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildMiniMetric('Displacement', '${(telemetry?.displacement ?? 0.0).toStringAsFixed(1)} mm'),
                      _buildMiniMetric('Strata Tilt', '${(telemetry?.tiltX ?? 0.0).toStringAsFixed(2)}°'),
                      _buildMiniMetric('Crack Opening', '${(telemetry?.crackWidth ?? 0.0).toStringAsFixed(2)} mm'),
                      _buildMiniMetric('Battery', '${node.battery.toStringAsFixed(0)}%'),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Actions & Locator
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'LoRa: ${node.signalStrength.toStringAsFixed(0)} dBm • Hop ${node.hopCount}',
                        style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8), fontWeight: FontWeight.bold),
                      ),
                      OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          side: const BorderSide(color: AppTheme.borderSubtle),
                        ),
                        icon: const Icon(Icons.location_searching, size: 14),
                        label: const Text('Locate Beacon', style: TextStyle(fontSize: 11)),
                        onPressed: () => _locateNode(context, node.id, node.nodeCode),
                      ),
                    ],
                  ),
                ],
              ),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error loading stations: $err')),
      ),
    );
  }

  Widget _buildMiniMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 9, color: Color(0xFF94A3B8), fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, fontFamily: 'monospace')),
      ],
    );
  }
}
