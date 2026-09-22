import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../widgets/app_card.dart';
import '../../widgets/ui_kit.dart';

final reportsSummaryProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final res = await apiClient.get(ApiConstants.reportsSummary);
  if (res.statusCode == 200 && res.data is Map) {
    return Map<String, dynamic>.from(res.data);
  }
  throw Exception('Unable to retrieve report summary');
});

class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(reportsSummaryProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.assessment_outlined, color: AppColors.accent, size: 20),
                    const SizedBox(width: 8),
                    Text('Compliance summary', style: Theme.of(context).textTheme.titleMedium),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Values below are returned by the reports API. Empty fields are not filled with placeholders.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 14),
                summaryAsync.when(
                  data: (sum) => Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      if (sum['total_readings'] != null) _item('Total readings', '${sum['total_readings']}'),
                      if (sum['active_nodes'] != null) _item('Active nodes', '${sum['active_nodes']}'),
                      if (sum['total_alerts'] != null) _item('Alerts', '${sum['total_alerts']}'),
                    ],
                  ),
                  loading: () => const LoadingState(message: 'Loading report summary…'),
                  error: (_, __) => const Text('Unable to retrieve report summary'),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Export', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Export uses the existing client action (no file generated locally).')),
                    );
                  },
                  icon: const Icon(Icons.file_download_outlined, size: 18),
                  label: const Text('Export telemetry report'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _item(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
      ],
    );
  }
}
