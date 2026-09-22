import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../models/telemetry_model.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/ui_kit.dart';

class TelemetryScreen extends ConsumerStatefulWidget {
  const TelemetryScreen({super.key});

  @override
  ConsumerState<TelemetryScreen> createState() => _TelemetryScreenState();
}

class _TelemetryScreenState extends ConsumerState<TelemetryScreen> {
  String _selectedMetric = 'displacement';

  @override
  Widget build(BuildContext context) {
    final selectedNode = ref.watch(selectedNodeIdProvider);
    final historyAsync = ref.watch(nodeHistoryProvider(selectedNode));
    final latest = ref.watch(latestTelemetryProvider)[selectedNode];
    final nodesAsync = ref.watch(nodesProvider);
    final apiCodes = nodesAsync.valueOrNull?.map((n) => n.nodeCode).toList() ?? [];
    final nodeCodes = apiCodes.isNotEmpty ? apiCodes : [selectedNode];
    final dropdownValue = nodeCodes.contains(selectedNode) ? selectedNode : nodeCodes.first;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppCard(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('MONITORED NODE', style: Theme.of(context).textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text(
                        RiskUtils.displayNodeCode(dropdownValue),
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, letterSpacing: 0.4),
                      ),
                    ],
                  ),
                ),
                DropdownButton<String>(
                  value: dropdownValue,
                  dropdownColor: AppColors.surfaceElevated,
                  underline: const SizedBox(),
                  items: nodeCodes
                      .map((code) => DropdownMenuItem(
                            value: code,
                            child: Text(RiskUtils.displayNodeCode(code), style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                          ))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) ref.read(selectedNodeIdProvider.notifier).state = val;
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          if (latest != null) ...[
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _stat('Current', _formatValue(latest, _selectedMetric), _unit(_selectedMetric)),
                _stat('Updated', latest.timestamp.toLocal().toString().split('.').first, ''),
                _stat('Battery', '${latest.battery.toStringAsFixed(0)}%', ''),
                _stat('Temp', '${latest.temperature.toStringAsFixed(1)} °C', ''),
                _stat('Humidity', '${latest.humidity.toStringAsFixed(0)}%', ''),
                _stat('Pressure', '${latest.pressure.toStringAsFixed(0)} hPa', ''),
              ],
            ),
            const SizedBox(height: 12),
          ] else
            const Padding(
              padding: EdgeInsets.only(bottom: 12),
              child: Text('Waiting for telemetry…', style: TextStyle(color: AppColors.textMuted)),
            ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _tab('Displacement', 'displacement', 'mm', Icons.compress_rounded),
                _tab('Tilt', 'tilt', '°', Icons.screen_rotation_rounded),
                _tab('Crack width', 'crack', 'mm', Icons.line_axis),
                _tab('Vibration', 'vibration', 'g', Icons.vibration_rounded),
                _tab('Acceleration', 'accel', 'g', Icons.speed),
              ],
            ),
          ),
          const SizedBox(height: 12),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('TREND  •  ${RiskUtils.displayNodeCode(dropdownValue)}', style: Theme.of(context).textTheme.labelSmall),
                const SizedBox(height: 16),
                SizedBox(
                  height: 240,
                  width: double.infinity,
                  child: historyAsync.when(
                    data: (history) => _buildChart(history),
                    loading: () => const LoadingState(message: 'Loading waveform…'),
                    error: (_, __) => const EmptyState(
                      icon: Icons.show_chart,
                      title: 'Unable to retrieve history',
                      message: 'Live stream may still be updating latest values.',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _stat(String label, String value, String unit) {
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 110),
      child: AppCard(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            Text('$value${unit.isEmpty ? '' : ' $unit'}', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
          ],
        ),
      ),
    );
  }

  Widget _tab(String label, String key, String unit, IconData icon) {
    final selected = _selectedMetric == key;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        selected: selected,
        label: Text('$label ($unit)'),
        avatar: Icon(icon, size: 14, color: selected ? AppColors.textOnAccent : AppColors.accent),
        selectedColor: AppColors.accent,
        backgroundColor: AppColors.surface,
        labelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: selected ? AppColors.textOnAccent : AppColors.textPrimary,
        ),
        side: const BorderSide(color: AppColors.border),
        onSelected: (_) => setState(() => _selectedMetric = key),
      ),
    );
  }

  String _unit(String key) {
    switch (key) {
      case 'tilt':
        return '°';
      case 'vibration':
      case 'accel':
        return 'g';
      default:
        return 'mm';
    }
  }

  String _formatValue(TelemetryModel t, String key) {
    switch (key) {
      case 'tilt':
        return t.tiltX.toStringAsFixed(2);
      case 'crack':
        return t.crackWidth.toStringAsFixed(2);
      case 'vibration':
        return t.vibration.toStringAsFixed(3);
      case 'accel':
        return t.accelZ.toStringAsFixed(3);
      default:
        return t.displacement.toStringAsFixed(1);
    }
  }

  Widget _buildChart(List<TelemetryModel> history) {
    if (history.isEmpty) {
      return const EmptyState(
        icon: Icons.timeline,
        title: 'Waiting for telemetry…',
        message: 'No samples received for this node yet.',
      );
    }

    final spots = <FlSpot>[];
    for (int i = 0; i < history.length; i++) {
      spots.add(FlSpot(i.toDouble(), _value(history[i])));
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (v) => const FlLine(color: AppColors.border, strokeWidth: 1),
        ),
        titlesData: const FlTitlesData(
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: false,
            color: AppColors.accent,
            barWidth: 2,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(show: true, color: AppColors.accent.withOpacity(0.08)),
          ),
        ],
      ),
    );
  }

  double _value(TelemetryModel item) {
    switch (_selectedMetric) {
      case 'tilt':
        return item.tiltX;
      case 'crack':
        return item.crackWidth;
      case 'vibration':
        return item.vibration;
      case 'accel':
        return item.accelZ;
      default:
        return item.displacement;
    }
  }
}
