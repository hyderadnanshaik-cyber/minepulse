import 'package:flutter/material.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_spacing.dart';

class RiskBadge extends StatelessWidget {
  final String riskLevel;
  final double? score;

  const RiskBadge({
    super.key,
    required this.riskLevel,
    this.score,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppColors.forRisk(riskLevel);
    final label = riskLevel.toUpperCase();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.bgForRisk(riskLevel),
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: color.withOpacity(0.45)),
      ),
      child: Text(
        score != null ? '$label  ${score!.toStringAsFixed(0)}' : label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.6,
          color: color,
        ),
      ),
    );
  }
}
