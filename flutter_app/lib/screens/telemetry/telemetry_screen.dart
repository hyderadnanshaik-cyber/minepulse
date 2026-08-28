import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/telemetry_provider.dart';
import '../../providers/node_provider.dart';
import '../../models/telemetry_model.dart';

class TelemetryScreen extends ConsumerStatefulWidget {
  const TelemetryScreen({super.key});

  @override
  ConsumerState<TelemetryScreen> createState() => _TelemetryScreenState();
}

class _TelemetryScreenState extends ConsumerState<TelemetryScreen> {
  String _selectedMetric = 'displacement'; // displacement, tilt, crack, vibration

  @override
  Widget build(BuildContext context) {
    final selectedNode = ref.watch(selectedNodeIdProvider);
    final historyAsync = ref.watch(nodeHistoryProvider(selectedNode));

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Station Selector Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'MONITORED STATION',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                      ),
                      Text(
                        selectedNode,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, fontFamily: 'monospace'),
                      ),
                    ],
                  ),
                  DropdownButton<String>(
                    value: selectedNode,
                    underline: const SizedBox(),
                    items: List.generate(20, (i) => 'NODE_${(i + 1).toString().padLeft(2, '0')}')
                        .map((code) => DropdownMenuItem(
                              value: code,
                              child: Text(code, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            ))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) {
                        ref.read(selectedNodeIdProvider.notifier).state = val;
                      }
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Metric Selector Segmented Pills
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildMetricTab('Displacement (mm)', 'displacement', Icons.compress_rounded, AppTheme.primaryBlue),
                  const SizedBox(width: 8),
                  _buildMetricTab('Strata Tilt (°)', 'tilt', Icons.screen_rotation_rounded, const Color(0xFF7C3AED)),
                  const SizedBox(width: 8),
                  _buildMetricTab('Crack Opening (mm)', 'crack', Icons.broken_image_outlined, AppTheme.highOrange),
                  const SizedBox(width: 8),
                  _buildMetricTab('Vibration (g)', 'vibration', Icons.vibration_rounded, const Color(0xFF0D9488)),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Time-Series Chart Box
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'REAL-TIME 50-SAMPLE WAVEFORM',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.slate[600]),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'DGMS Limit Displayed',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primaryBlue),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    height: 220,
                    child: historyAsync.when(
                      data: (history) => _buildChart(history),
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (_, __) => const Center(child: Text('Live telemetry active')),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTab(String label, String key, IconData icon, Color color) {
    final isSelected = _selectedMetric == key;
    return GestureDetector(
      onTap: () => setState(() => _selectedMetric = key),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? color : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? color : AppTheme.borderSubtle),
        ),
        child: Row(
          children: [
            Icon(icon, size: 16, color: isSelected ? Colors.white : color),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: isSelected ? Colors.white : const Color(0xFF0F172A),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChart(List<TelemetryModel> history) {
    if (history.isEmpty) {
      return const Center(child: Text('Awaiting streaming telemetry...'));
    }

    final spots = <FlSpot>[];
    for (int i = 0; i < history.length; i++) {
      final item = history[i];
      double val = 0.0;
      switch (_selectedMetric) {
        case 'tilt':
          val = item.tiltX;
          break;
        case 'crack':
          val = item.crackWidth;
          break;
        case 'vibration':
          val = item.vibration;
          break;
        case 'displacement':
        default:
          val = item.displacement;
      }
      spots.add(FlSpot(i.toDouble(), val));
    }

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: true, drawVerticalLine: false),
        titlesData: const FlTitlesData(
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: AppTheme.primaryBlue,
            barWidth: 2.5,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: AppTheme.primaryBlue.withOpacity(0.08),
            ),
          ),
        ],
      ),
    );
  }
}
