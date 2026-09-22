import 'package:flutter/material.dart';

/// MineGuard industrial safety palette. Use these tokens everywhere.
class AppColors {
  AppColors._();

  // Surfaces
  static const Color background = Color(0xFF0B1016);
  static const Color surface = Color(0xFF131A22);
  static const Color surfaceElevated = Color(0xFF1A222C);
  static const Color surfaceMuted = Color(0xFF0F151C);
  static const Color border = Color(0xFF2A3542);
  static const Color borderStrong = Color(0xFF3A4756);

  // Light surfaces (optional light theme)
  static const Color lightBackground = Color(0xFFF3F5F7);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightBorder = Color(0xFFD8DEE6);

  // Text
  static const Color textPrimary = Color(0xFFE8EEF4);
  static const Color textSecondary = Color(0xFF9AA8B6);
  static const Color textMuted = Color(0xFF6B7A8A);
  static const Color textOnAccent = Color(0xFFFFFFFF);
  static const Color lightTextPrimary = Color(0xFF0F1720);
  static const Color lightTextSecondary = Color(0xFF4B5A6A);

  // Accent — technical, not neon
  static const Color accent = Color(0xFF2F7FD1);
  static const Color accentMuted = Color(0xFF1B4F80);

  // Risk
  static const Color riskLow = Color(0xFF2F9E6A);
  static const Color riskMedium = Color(0xFFD4A017);
  static const Color riskHigh = Color(0xFFE07A2F);
  static const Color riskCritical = Color(0xFFD13A3A);

  static const Color riskLowBg = Color(0x1A2F9E6A);
  static const Color riskMediumBg = Color(0x1AD4A017);
  static const Color riskHighBg = Color(0x1AE07A2F);
  static const Color riskCriticalBg = Color(0x1AD13A3A);

  static Color forRisk(String level) {
    switch (level.toUpperCase()) {
      case 'CRITICAL':
        return riskCritical;
      case 'HIGH':
        return riskHigh;
      case 'MEDIUM':
      case 'WATCH':
      case 'MODERATE':
        return riskMedium;
      case 'LOW':
      case 'NORMAL':
      default:
        return riskLow;
    }
  }

  static Color bgForRisk(String level) {
    switch (level.toUpperCase()) {
      case 'CRITICAL':
        return riskCriticalBg;
      case 'HIGH':
        return riskHighBg;
      case 'MEDIUM':
      case 'WATCH':
      case 'MODERATE':
        return riskMediumBg;
      case 'LOW':
      case 'NORMAL':
      default:
        return riskLowBg;
    }
  }
}
