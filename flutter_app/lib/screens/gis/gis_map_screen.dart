import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';

class GisMapScreen extends ConsumerWidget {
  const GisMapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nodesAsync = ref.watch(nodesProvider);
    final telemetryMap = ref.watch(latestTelemetryProvider);

    return Scaffold(
      body: Stack(
        children: [
          // FlutterMap OpenStreetMap Layer
          FlutterMap(
            options: const MapOptions(
              initialCenter: LatLng(23.7505, 86.4205),
              initialZoom: 17.5,
              maxZoom: 19.0,
              minZoom: 15.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.redhack.mineguard',
              ),
              // Panel Alpha North Polygon Boundary
              PolygonLayer(
                polygons: [
                  Polygon(
                    points: const [
                      LatLng(23.7495, 86.4195),
                      LatLng(23.7520, 86.4195),
                      LatLng(23.7520, 86.4225),
                      LatLng(23.7495, 86.4225),
                    ],
                    color: AppTheme.primaryBlue.withOpacity(0.12),
                    borderColor: AppTheme.primaryBlue,
                    borderStrokeWidth: 2,
                    isFilled: true,
                  ),
                ],
              ),
              // PostGIS Node Markers
              nodesAsync.when(
                data: (nodes) => MarkerLayer(
                  markers: nodes.map((node) {
                    final lat = node.latitude ?? 23.7500;
                    final lng = node.longitude ?? 86.4200;
                    final t = telemetryMap[node.nodeCode];
                    final isHazard = (t?.displacement ?? 0.0) >= 20.0 || (t?.crackWidth ?? 0.0) >= 2.0;

                    return Marker(
                      point: LatLng(lat, lng),
                      width: 60,
                      height: 60,
                      child: GestureDetector(
                        onTap: () {
                          ref.read(selectedNodeIdProvider.notifier).state = node.nodeCode;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Selected Station: ${node.nodeCode} | Disp: ${(t?.displacement ?? 0).toStringAsFixed(1)}mm | Tilt: ${(t?.tiltX ?? 0).toStringAsFixed(2)}°'),
                            ),
                          );
                        },
                        child: Column(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: isHazard ? AppTheme.criticalRed : AppTheme.safeEmerald,
                                shape: BoxShape.circle,
                                border: Border.all(color: Colors.white, width: 2),
                                boxShadow: [
                                  BoxShadow(
                                    color: (isHazard ? AppTheme.criticalRed : AppTheme.safeEmerald).withOpacity(0.4),
                                    blurRadius: 8,
                                  ),
                                ],
                              ),
                              child: const Icon(Icons.sensors, size: 14, color: Colors.white),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                              decoration: BoxDecoration(
                                color: Colors.black87,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                node.nodeCode,
                                style: const TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold),
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

          // Map HUD Card
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.95),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 10),
                ],
              ),
              child: const Row(
                children: [
                  Icon(Icons.layers_rounded, color: AppTheme.primaryBlue, size: 20),
                  SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'PANEL ALPHA NORTH (POSTGIS 3.6)',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900),
                      ),
                      Text(
                        '20 Stations Active • Centroid 23.7505° N, 86.4205° E',
                        style: TextStyle(fontSize: 10, color: Color(0xFF64748B), fontWeight: FontWeight.w600),
                      ),
                    ],
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
