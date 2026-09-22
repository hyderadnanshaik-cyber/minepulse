import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../core/utils/risk_utils.dart';
import '../../providers/ai_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/risk_badge.dart';
import '../../widgets/ui_kit.dart';

class AiAnalyticsScreen extends ConsumerStatefulWidget {
  const AiAnalyticsScreen({super.key});

  @override
  ConsumerState<AiAnalyticsScreen> createState() => _AiAnalyticsScreenState();
}

class _AiAnalyticsScreenState extends ConsumerState<AiAnalyticsScreen> {
  bool _isRetraining = false;

  Future<void> _triggerRetrain() async {
    setState(() => _isRetraining = true);
    try {
      final res = await apiClient.post(ApiConstants.aiTrain);
      if (!mounted) return;
      final msg = res.data is Map ? (res.data['message'] ?? 'Retrain requested') : 'Retrain requested';
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$msg')));
      ref.invalidate(aiStatusProvider);
      ref.invalidate(recentPredictionsProvider);
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to start model retraining')),
      );
    }
    setState(() => _isRetraining = false);
  }

  @override
  Widget build(BuildContext context) {
    final statusAsync = ref.watch(aiStatusProvider);
    final predictionsAsync = ref.watch(recentPredictionsProvider);

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
                    const Icon(Icons.psychology_outlined, color: AppColors.accent, size: 20),
                    const SizedBox(width: 8),
                    Expanded(child: Text('AI MODEL STATUS', style: Theme.of(context).textTheme.titleMedium)),
                  ],
                ),
                const SizedBox(height: 12),
                statusAsync.when(
                  data: (status) {
                    final trained = status['is_trained'] == true;
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        StatusBadge(
                          label: trained ? 'CONNECTED' : 'INITIALIZING',
                          color: trained ? AppColors.riskLow : AppColors.riskMedium,
                        ),
                        const SizedBox(height: 10),
                        if (status['model_version'] != null)
                          Text('Version  ${status['model_version']}', style: Theme.of(context).textTheme.bodyMedium),
                        if (status['model_accuracy'] != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Text(
                              'Reported metric  ${status['model_accuracy']}',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ),
                      ],
                    );
                  },
                  loading: () => const Text('Checking model…'),
                  error: (_, __) => const StatusBadge(
                    label: 'NOT AVAILABLE',
                    color: AppColors.riskHigh,
                    icon: Icons.cloud_off,
                  ),
                ),
                const SizedBox(height: 14),
                OutlinedButton.icon(
                  onPressed: _isRetraining ? null : _triggerRetrain,
                  icon: _isRetraining
                      ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.sync, size: 16),
                  label: Text(_isRetraining ? 'Retraining…' : 'Recalibrate on live telemetry'),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.xl),
          const SectionHeader(title: 'Recent predictions'),
          predictionsAsync.when(
            data: (preds) {
              if (preds.isEmpty) {
                return const AppCard(child: Text('No predictions available'));
              }
              return Column(
                children: preds.map((pred) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: AppCard(
                      borderColor: AppColors.forRisk(pred.riskLevel).withOpacity(0.4),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                RiskUtils.displayNodeCode(pred.nodeId),
                                style: const TextStyle(fontWeight: FontWeight.w800),
                              ),
                              const Spacer(),
                              RiskBadge(riskLevel: pred.riskLevel, score: pred.riskScore),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Anomaly  ${pred.anomalyScore.toStringAsFixed(3)}  •  Confidence  ${(pred.confidence * 100).toStringAsFixed(0)}%',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                          Text(
                            pred.createdAt.toLocal().toString().split('.').first,
                            style: Theme.of(context).textTheme.labelSmall,
                          ),
                          if (pred.triggeredIndicators != null && pred.triggeredIndicators!.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: pred.triggeredIndicators!
                                  .map((ind) => StatusBadge(label: ind.toString(), color: AppColors.riskCritical))
                                  .toList(),
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                }).toList(),
              );
            },
            loading: () => const LoadingState(message: 'Loading predictions…'),
            error: (err, _) => ErrorState(message: 'Unable to retrieve predictions'),
          ),
        ],
      ),
    );
  }
}
