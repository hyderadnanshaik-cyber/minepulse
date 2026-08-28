import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

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
    Color bg;
    Color fg;

    switch (riskLevel.toUpperCase()) {
      case 'CRITICAL':
        bg = const Color(0xFFFEE2E2);
        fg = AppTheme.criticalRed;
        break;
      case 'HIGH':
        bg = const Color(0xFFFFEDD5);
        fg = AppTheme.highOrange;
        break;
      case 'WATCH':
      case 'MODERATE':
        bg = const Color(0xFFFEF3C7);
        fg = AppTheme.warningAmber;
        break;
      case 'NORMAL':
      default:
        bg = const Color(0xFFD1FAE5);
        fg = AppTheme.safeEmerald;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        score != null ? '$riskLevel (${score!.toStringAsFixed(0)})' : riskLevel,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          color: fg,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
