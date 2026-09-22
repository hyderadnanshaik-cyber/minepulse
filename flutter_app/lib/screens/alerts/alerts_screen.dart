import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/localization/app_localizations.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../providers/alert_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/ui_kit.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alerts = ref.watch(alertListProvider);
    final l10n = AppLocalizations.of(context);

    if (alerts.isEmpty) {
      return const EmptyState(
        icon: Icons.check_circle_outline,
        title: 'No active alerts',
        message: 'No geotechnical alerts are currently reported.',
        color: AppColors.riskLow,
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      itemCount: alerts.length,
      itemBuilder: (context, idx) {
        final alert = alerts[idx];
        final severity = alert.severity.toUpperCase();
        final color = AppColors.forRisk(severity);
        final active = alert.status == 'DETECTED' || alert.status == 'ACTIVE';

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: AppCard(
            color: AppColors.bgForRisk(severity),
            borderColor: color.withOpacity(severity == 'CRITICAL' ? 0.7 : 0.4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      severity == 'CRITICAL' ? Icons.warning_rounded : Icons.info_outline,
                      color: color,
                      size: 18,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      RiskUtils.displayNodeCode(alert.nodeId),
                      style: const TextStyle(fontWeight: FontWeight.w800, letterSpacing: 0.4),
                    ),
                    const Spacer(),
                    RiskBadge(riskLevel: alert.severity, score: alert.riskScore),
                  ],
                ),
                const SizedBox(height: 10),
                Text(alert.title, style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                Text(alert.message, style: Theme.of(context).textTheme.bodySmall),
                if (alert.alertType.toLowerCase().contains('crack')) ...[
                  const SizedBox(height: 8),
                  const StatusBadge(label: 'CRACK DETECTED', color: AppColors.riskCritical, icon: Icons.warning_amber),
                ],
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${alert.status}  •  ${alert.detectedAt.toLocal().toString().split('.').first}',
                        style: Theme.of(context).textTheme.labelSmall,
                      ),
                    ),
                    if (active)
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: color,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        ),
                        onPressed: () => ref.read(alertListProvider.notifier).acknowledgeAlert(alert.id),
                        child: Text(l10n.translate('acknowledge'), style: const TextStyle(fontSize: 11)),
                      ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
