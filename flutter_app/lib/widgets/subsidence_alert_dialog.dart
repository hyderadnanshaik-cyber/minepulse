import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../models/alert_model.dart';
import '../core/utils/risk_utils.dart';
import 'risk_badge.dart';

class SubsidenceAlertDialog extends StatelessWidget {
  final AlertModel alert;
  final VoidCallback onAcknowledge;
  final VoidCallback onViewGis;

  const SubsidenceAlertDialog({
    super.key,
    required this.alert,
    required this.onAcknowledge,
    required this.onViewGis,
  });

  @override
  Widget build(BuildContext context) {
    final isCritical = alert.severity.toUpperCase() == 'CRITICAL';
    final color = AppColors.forRisk(alert.severity);

    return Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: color.withOpacity(0.6)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.warning_amber_rounded, size: 36, color: color),
            const SizedBox(height: 12),
            Text(
              isCritical ? 'CRITICAL SUBSIDENCE ALERT' : 'SUBSIDENCE WARNING',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, letterSpacing: 0.4),
            ),
            const SizedBox(height: 8),
            RiskBadge(riskLevel: alert.severity, score: alert.riskScore),
            const SizedBox(height: 12),
            Text(
              RiskUtils.displayNodeCode(alert.nodeId),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, letterSpacing: 0.6),
            ),
            const SizedBox(height: 8),
            Text(
              alert.message,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.4),
            ),
            const SizedBox(height: 12),
            Text(
              'Time  ${alert.detectedAt.toLocal().toString().split('.').first}',
              style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: color),
                onPressed: onAcknowledge,
                child: const Text('Acknowledge'),
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: onViewGis,
                child: const Text('View on map'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
