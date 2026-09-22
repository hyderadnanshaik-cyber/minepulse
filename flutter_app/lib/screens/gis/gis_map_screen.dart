import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../models/node_model.dart';
import '../../models/telemetry_model.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/ui_kit.dart';

class GisMapScreen extends ConsumerWidget {
  const GisMapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesProvider);
    final telemetryMap = ref.watch(latestTelemetryProvider);

    return Stack(
      children: [
        FlutterMap(
          options: const MapOptions(
            initialCenter: LatLng(23.7505, 86.4205),
            initialZoom: 17.5,
            maxZoom: 19.0,
            minZoom: 15.0,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.redhack.mineguard',
            ),
            PolygonLayer(
              polygons: [
                Polygon(
                  points: const [
                    LatLng(23.7495, 86.4195),
                    LatLng(23.7520, 86.4195),
                    LatLng(23.7520, 86.4225),
                    LatLng(23.7495, 86.4225),
                  ],
                  color: AppColors.accent.withOpacity(0.10),
                  borderColor: AppColors.accent,
                  borderStrokeWidth: 1.5,
                  isFilled: true,
                ),
              ],
            ),
            nodesAsync.when(
              data: (nodes) => MarkerLayer(
                markers: nodes.where((n) => n.latitude != null && n.longitude != null).map((node) {
                  final t = telemetryMap[node.nodeCode];
                  final risk = t != null ? RiskUtils.fromTelemetry(t) : node.riskLevel;
                  final color = AppColors.forRisk(risk);
                  final abnormal = risk == 'HIGH' || risk == 'CRITICAL';

                  return Marker(
                    point: LatLng(node.latitude!, node.longitude!),
                    width: 72,
                    height: 56,
                    child: GestureDetector(
                      onTap: () {
                        ref.read(selectedNodeIdProvider.notifier).state = node.nodeCode;
                        _openNodeSheet(context, node, t, risk);
                      },
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: color,
                              shape: BoxShape.circle,
                              border: Border.all(color: Colors.white, width: abnormal ? 2.5 : 1.5),
                            ),
                            child: const Icon(Icons.sensors, size: 12, color: Colors.white),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                            decoration: BoxDecoration(
                              color: AppColors.background.withOpacity(0.9),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              RiskUtils.displayNodeCode(node.nodeCode),
                              style: TextStyle(
                                color: abnormal ? color : Colors.white,
                                fontSize: 8,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
              loading: () => const MarkerLayer(markers: []),
              error: (_, __) => const MarkerLayer(markers: []),
            ),
          ],
        ),
        Positioned(
          top: 12,
          left: 12,
          right: 12,
          child: AppCard(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                const Icon(Icons.layers_outlined, color: AppColors.accent, size: 18),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Mine panel map', style: Theme.of(context).textTheme.titleMedium),
                      Text(
                        nodesAsync.when(
                          data: (n) => '${n.length} nodes with coordinates from API',
                          loading: () => 'Loading nodes…',
                          error: (_, __) => 'Unable to retrieve node data',
                        ),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _openNodeSheet(BuildContext context, NodeModel node, TelemetryModel? t, String risk) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    RiskUtils.displayNodeCode(node.nodeCode),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                  const Spacer(),
                  RiskBadge(riskLevel: risk),
                ],
              ),
              const SizedBox(height: 8),
              Text(node.status.toUpperCase(), style: Theme.of(ctx).textTheme.bodySmall),
              const SizedBox(height: 12),
              if (t == null)
                const Text('Waiting for telemetry…')
              else ...[
                Text('Displacement  ${t.displacement.toStringAsFixed(1)} mm'),
                Text('Tilt  ${t.tiltX.toStringAsFixed(2)}°'),
                Text('Crack width  ${t.crackWidth.toStringAsFixed(2)} mm'),
                Text('Vibration  ${t.vibration.toStringAsFixed(3)} g'),
                if (t.crackDetected) ...[
                  const SizedBox(height: 8),
                  const StatusBadge(label: 'CRACK DETECTED', color: AppColors.riskCritical),
                ],
                const SizedBox(height: 8),
                Text(
                  'Updated  ${t.timestamp.toLocal().toString().split('.').first}',
                  style: Theme.of(ctx).textTheme.labelSmall,
                ),
              ],
              if (node.latitude != null)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    '${node.latitude!.toStringAsFixed(5)}, ${node.longitude!.toStringAsFixed(5)}',
                    style: Theme.of(ctx).textTheme.labelSmall,
                  ),
                ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
  }
}
