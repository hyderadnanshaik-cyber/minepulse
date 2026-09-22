import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/localization/app_localizations.dart';
import '../../core/network/api_client.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../models/node_model.dart';
import '../../models/telemetry_model.dart';
import '../../providers/alert_provider.dart';
import '../../providers/gateway_provider.dart';
import '../../providers/node_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/metric_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/ui_kit.dart';

class DashboardHome extends ConsumerWidget {
  const DashboardHome({super.key});

  Future<void> _triggerScenario(BuildContext context, String mode) async {
    try {
      await apiClient.post(ApiConstants.scenarioTrigger, data: {'mode': mode});
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            mode == 'ANOMALY_NODE_03'
                ? 'Triggered NODE-03 anomaly scenario'
                : 'Reset scenario: all nodes nominal',
          ),
          backgroundColor: mode == 'ANOMALY_NODE_03' ? AppColors.riskCritical : AppColors.riskLow,
        ),
      );
    } catch (_) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to trigger scenario. Check API connection.')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final telemetryMap = ref.watch(latestTelemetryProvider);
    final alerts = ref.watch(alertListProvider);
    final nodesAsync = ref.watch(nodesProvider);
    final gwAsync = ref.watch(gatewayStatusProvider);
    final width = MediaQuery.of(context).size.width;
    final cols = width >= 1100 ? 4 : (width >= 600 ? 2 : 2);

    final activeAlerts = alerts.where((a) {
      final s = a.status.toUpperCase();
      return s == 'DETECTED' || s == 'ACTIVE';
    }).toList();

    String overallRisk = 'NORMAL';
    if (telemetryMap.isNotEmpty) {
      overallRisk = RiskUtils.highest(telemetryMap.values.map(RiskUtils.fromTelemetry));
    } else {
      overallRisk = 'UNKNOWN';
    }

    TelemetryModel? worst;
    for (final t in telemetryMap.values) {
      if (worst == null) {
        worst = t;
        continue;
      }
      final order = ['CRITICAL', 'HIGH', 'MEDIUM', 'NORMAL', 'UNKNOWN'];
      if (order.indexOf(RiskUtils.fromTelemetry(t)) < order.indexOf(RiskUtils.fromTelemetry(worst))) {
        worst = t;
      }
    }

    final nodes = nodesAsync.valueOrNull ?? [];
    final onlineCount = nodes.where((n) => n.status.toUpperCase() == 'ONLINE').length;
    final hasTelemetry = telemetryMap.isNotEmpty;
    final latest = worst ?? (telemetryMap.isNotEmpty ? telemetryMap.values.first : null);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppCard(
            color: AppColors.bgForRisk(overallRisk),
            borderColor: AppColors.forRisk(overallRisk).withOpacity(0.5),
            child: Row(
              children: [
                Icon(
                  overallRisk == 'CRITICAL' || overallRisk == 'HIGH'
                      ? Icons.warning_amber_rounded
                      : Icons.verified_user_outlined,
                  color: AppColors.forRisk(overallRisk),
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('OVERALL MINE SAFETY', style: Theme.of(context).textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text(
                        !hasTelemetry
                            ? 'Waiting for telemetry…'
                            : overallRisk == 'NORMAL' || overallRisk == 'LOW'
                                ? 'Mine status: Safe'
                                : 'Abnormal movement detected',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      if (worst != null && RiskUtils.isAbnormal(worst))
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            '${RiskUtils.displayNodeCode(worst.nodeCode)} requires attention',
                            style: TextStyle(color: AppColors.forRisk(overallRisk), fontWeight: FontWeight.w600, fontSize: 12),
                          ),
                        ),
                    ],
                  ),
                ),
                RiskBadge(riskLevel: overallRisk == 'UNKNOWN' ? 'NORMAL' : overallRisk),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          GridView.count(
            crossAxisCount: cols,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: width < 400 ? 1.55 : 1.7,
            children: [
              MetricCard(
                title: 'Active nodes',
                value: nodesAsync.hasValue ? '${nodes.length}' : '—',
                unit: '',
                icon: Icons.sensors,
                subtitle: nodesAsync.hasValue ? null : 'Loading',
              ),
              MetricCard(
                title: 'Online nodes',
                value: nodesAsync.hasValue ? '$onlineCount' : '—',
                unit: '',
                icon: Icons.podcasts,
                iconColor: AppColors.riskLow,
              ),
              MetricCard(
                title: 'Active alerts',
                value: '${activeAlerts.length}',
                unit: '',
                icon: Icons.notifications_active_outlined,
                iconColor: activeAlerts.isEmpty ? AppColors.riskLow : AppColors.riskCritical,
                isHazard: activeAlerts.isNotEmpty,
              ),
              MetricCard(
                title: 'Highest risk',
                value: overallRisk == 'UNKNOWN' ? '—' : overallRisk,
                unit: '',
                icon: Icons.priority_high,
                iconColor: AppColors.forRisk(overallRisk),
                isHazard: overallRisk == 'HIGH' || overallRisk == 'CRITICAL',
              ),
            ],
          ),
          const SizedBox(height: 10),
          gwAsync.when(
            data: (gw) => AppCard(
              child: Row(
                children: [
                  StatusBadge(
                    label: gw.status.toUpperCase(),
                    color: gw.status.toUpperCase() == 'ONLINE' ? AppColors.riskLow : AppColors.riskHigh,
                    icon: Icons.router,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      '${gw.name}  •  ${gw.ipAddress}',
                      style: Theme.of(context).textTheme.bodySmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Text(
                    'MQTT ${gw.mqttStatus}',
                    style: Theme.of(context).textTheme.labelSmall,
                  ),
                ],
              ),
            ),
            loading: () => const AppCard(child: Text('Checking gateway…')),
            error: (_, __) => const AppCard(
              child: Text('Gateway status unavailable'),
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          AppCard(
            color: AppColors.surfaceElevated,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.science_outlined, size: 16, color: AppColors.accent),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text('SIH scenario control', style: Theme.of(context).textTheme.titleMedium),
                    ),
                    RiskBadge(riskLevel: overallRisk == 'UNKNOWN' ? 'NORMAL' : overallRisk),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Uses the existing /system/scenario/trigger API. Does not inject local fake telemetry.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 12),
                LayoutBuilder(
                  builder: (context, c) {
                    final stacked = c.maxWidth < 480;
                    final trigger = ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: AppColors.riskCritical),
                      onPressed: () => _triggerScenario(context, 'ANOMALY_NODE_03'),
                      icon: const Icon(Icons.bolt, size: 16),
                      label: Text(l10n.translate('trigger_sih_demo'), style: const TextStyle(fontSize: 12)),
                    );
                    final reset = OutlinedButton.icon(
                      onPressed: () => _triggerScenario(context, 'NORMAL'),
                      icon: const Icon(Icons.restart_alt, size: 16),
                      label: Text(l10n.translate('reset_safe'), style: const TextStyle(fontSize: 12)),
                    );
                    if (stacked) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [trigger, const SizedBox(height: 8), reset],
                      );
                    }
                    return Row(
                      children: [
                        Expanded(child: trigger),
                        const SizedBox(width: 8),
                        Expanded(child: reset),
                      ],
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          SectionHeader(title: 'Live sensor readings'),
          if (!hasTelemetry)
            const AppCard(child: Text('Waiting for telemetry…'))
          else
            GridView.count(
              crossAxisCount: cols,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: width < 400 ? 1.45 : 1.55,
              children: [
                MetricCard(
                  title: l10n.translate('displacement'),
                  value: (latest?.displacement ?? 0).toStringAsFixed(1),
                  unit: 'mm',
                  icon: Icons.compress_rounded,
                  subtitle: latest == null ? null : RiskUtils.displayNodeCode(latest.nodeCode),
                  isHazard: (latest?.displacement ?? 0) >= ApiConstants.maxSubsidenceDisplacementMm,
                ),
                MetricCard(
                  title: l10n.translate('strata_tilt'),
                  value: (latest?.tiltX ?? 0).toStringAsFixed(2),
                  unit: '°',
                  icon: Icons.screen_rotation_rounded,
                  subtitle: 'Limit ${ApiConstants.maxStrataTiltDeg}°',
                  isHazard: (latest?.tiltX ?? 0) >= ApiConstants.maxStrataTiltDeg,
                ),
                MetricCard(
                  title: l10n.translate('crack_width'),
                  value: (latest?.crackWidth ?? 0).toStringAsFixed(2),
                  unit: 'mm',
                  icon: Icons.line_axis,
                  subtitle: latest?.crackDetected == true ? 'CRACK DETECTED' : 'Limit ${ApiConstants.maxCrackFissureWidthMm} mm',
                  isHazard: latest?.crackDetected == true || (latest?.crackWidth ?? 0) >= ApiConstants.maxCrackFissureWidthMm,
                ),
                MetricCard(
                  title: l10n.translate('vibration'),
                  value: (latest?.vibration ?? 0).toStringAsFixed(3),
                  unit: 'g',
                  icon: Icons.vibration_rounded,
                  iconColor: AppColors.accent,
                  isHazard: (latest?.vibration ?? 0) >= ApiConstants.maxVibrationG,
                ),
              ],
            ),
          const SizedBox(height: AppSpacing.xl),
          SectionHeader(title: 'Sensor network'),
          nodesAsync.when(
            data: (list) {
              if (list.isEmpty) {
                return const AppCard(child: Text('Unable to retrieve node data'));
              }
              return AppCard(
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: list.map((NodeModel node) {
                    final t = telemetryMap[node.nodeCode];
                    final risk = t != null ? RiskUtils.fromTelemetry(t) : node.riskLevel;
                    final abnormal = risk == 'HIGH' || risk == 'CRITICAL';
                    final color = AppColors.forRisk(risk);
                    return Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: AppColors.bgForRisk(risk),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: abnormal ? color : AppColors.border,
                          width: abnormal ? 1.4 : 1,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.circle, size: 8, color: color),
                          const SizedBox(width: 6),
                          Text(
                            RiskUtils.displayNodeCode(node.nodeCode),
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.3,
                              color: abnormal ? color : AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              );
            },
            loading: () => const LoadingState(message: 'Loading nodes…'),
            error: (_, __) => const AppCard(child: Text('Unable to retrieve node data')),
          ),
          const SizedBox(height: AppSpacing.xl),
          SectionHeader(title: 'Recent alerts'),
          if (alerts.isEmpty)
            const AppCard(child: Text('No active alerts'))
          else
            ...alerts.take(3).map((alert) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: AppCard(
                  borderColor: AppColors.forRisk(alert.severity).withOpacity(0.45),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            RiskUtils.displayNodeCode(alert.nodeId),
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                          ),
                          const Spacer(),
                          RiskBadge(riskLevel: alert.severity, score: alert.riskScore),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(alert.title, style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 4),
                      Text(alert.message, style: Theme.of(context).textTheme.bodySmall),
                      const SizedBox(height: 6),
                      Text(
                        alert.detectedAt.toLocal().toString().split('.').first,
                        style: Theme.of(context).textTheme.labelSmall,
                      ),
                    ],
                  ),
                ),
              );
            }),
        ],
      ),
    );
  }
}
