import 'package:flutter/material.dart';

class AppTheme {
  // Industrial High-Contrast Safety Palette
  static const Color primaryBlue = Color(0xFF1E40AF);    // High-visibility Royal Blue
  static const Color darkBackground = Color(0xFF0A0F1D); // Deep Slate Navy
  static const Color surfaceCard = Color(0xFFFFFFFF);   // Pure White Card
  static const Color surfaceLight = Color(0xFFF8FAFC);  // Slate 50
  static const Color borderSubtle = Color(0xFFE2E8F0);  // Slate 200

  // DGMS Status Colors
  static const Color safeEmerald = Color(0xFF059669);   // DGMS Safe Normal
  static const Color warningAmber = Color(0xFFD97706);  // Elevated Watch
  static const Color highOrange = Color(0xFFEA580C);    // High Strata Deformation
  static const Color criticalRed = Color(0xFFDC2626);   // Critical Imminent Trip

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Inter',
    scaffoldBackgroundColor: surfaceLight,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryBlue,
      brightness: Brightness.light,
      primary: primaryBlue,
      surface: surfaceCard,
      error: criticalRed,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.white,
      foregroundColor: Color(0xFF0F172A),
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w800,
        color: Color(0xFF0F172A),
        letterSpacing: -0.5,
      ),
    ),
    cardTheme: CardTheme(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: borderSubtle, width: 1),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryBlue,
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    fontFamily: 'Inter',
    scaffoldBackgroundColor: darkBackground,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryBlue,
      brightness: Brightness.dark,
      primary: const Color(0xFF3B82F6),
      surface: const Color(0xFF1E293B),
      error: criticalRed,
    ),
  );
}
