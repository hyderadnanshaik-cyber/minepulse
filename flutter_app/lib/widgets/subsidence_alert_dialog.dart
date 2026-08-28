import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../models/alert_model.dart';

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

    return Dialog(
      backgroundColor: const Color(0xFF111827),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Warning Icon Badge
            Container(
              height: 72,
              width: 72,
              decoration: BoxDecoration(
                color: isCritical
                    ? Colors.white.withOpacity(0.12)
                    : AppTheme.warningAmber.withOpacity(0.2),
                shape: BoxShape.circle,
                border: Border.all(
                  color: isCritical ? Colors.white.withOpacity(0.25) : AppTheme.warningAmber,
                  width: 2,
                ),
              ),
              child: Icon(
                Icons.warning_amber_rounded,
                size: 40,
                color: isCritical ? Colors.white : AppTheme.warningAmber,
              ),
            ),
            const SizedBox(height: 20),

            // Headline
            Text(
              isCritical
                  ? 'SUBSIDENCE WARNING: CRITICAL GROUND DEFORMATION'
                  : 'ELEVATED STRATA HAZARD DETECTED',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w900,
                color: Colors.white,
                letterSpacing: -0.2,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              alert.message,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: Colors.white.withOpacity(0.7),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),

            // Telemetry Snapshot Box
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.06),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white.withOpacity(0.1)),
              ),
              child: Column(
                children: [
                  _buildRow('Monitored Node', alert.nodeId, isMono: true),
                  const Divider(color: Colors.white12, height: 16),
                  _buildRow('Risk Score', '${alert.riskScore.toStringAsFixed(1)} / 100',
                      valueColor: AppTheme.criticalRed),
                  const SizedBox(height: 6),
                  _buildRow('Anomaly Confidence', '${(alert.anomalyScore * 100).toStringAsFixed(0)}%',
                      valueColor: AppTheme.warningAmber),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Action Buttons
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF0F172A),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                onPressed: onAcknowledge,
                child: const Text(
                  'Acknowledge Alert & Dispatch Siren (GPIO 18)',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 12),
                ),
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: BorderSide(color: Colors.white.withOpacity(0.2)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                onPressed: onViewGis,
                child: const Text(
                  'View Live GIS Coordinates & Waveform',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value, {bool isMono = false, Color? valueColor}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.5)),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w800,
            fontFamily: isMono ? 'monospace' : null,
            color: valueColor ?? Colors.white,
          ),
        ),
      ],
    );
  }
}
