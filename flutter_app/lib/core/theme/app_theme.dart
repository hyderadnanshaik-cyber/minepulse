import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_spacing.dart';

class AppTheme {
  // Backwards-compatible aliases used by existing screens during migration
  static const Color primaryBlue = AppColors.accent;
  static const Color darkBackground = AppColors.background;
  static const Color surfaceCard = AppColors.surface;
  static const Color surfaceLight = AppColors.surfaceMuted;
  static const Color borderSubtle = AppColors.border;
  static const Color safeEmerald = AppColors.riskLow;
  static const Color warningAmber = AppColors.riskMedium;
  static const Color highOrange = AppColors.riskHigh;
  static const Color criticalRed = AppColors.riskCritical;

  static const String fontFamily = 'Roboto';

  static TextTheme _textTheme(Color primary, Color secondary) {
    return TextTheme(
      displaySmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 28,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.4,
        color: primary,
      ),
      headlineMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 22,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.2,
        color: primary,
      ),
      titleLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: primary,
      ),
      titleMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
        color: primary,
      ),
      titleSmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.6,
        color: secondary,
      ),
      bodyLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w400,
        height: 1.4,
        color: primary,
      ),
      bodyMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 13,
        fontWeight: FontWeight.w400,
        height: 1.4,
        color: primary,
      ),
      bodySmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 11,
        fontWeight: FontWeight.w500,
        color: secondary,
      ),
      labelLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 13,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.3,
        color: primary,
      ),
      labelSmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 10,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.8,
        color: secondary,
      ),
    );
  }

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: fontFamily,
    scaffoldBackgroundColor: AppColors.background,
    colorScheme: const ColorScheme.dark(
      primary: AppColors.accent,
      onPrimary: AppColors.textOnAccent,
      surface: AppColors.surface,
      onSurface: AppColors.textPrimary,
      error: AppColors.riskCritical,
      outline: AppColors.border,
    ),
    textTheme: _textTheme(AppColors.textPrimary, AppColors.textSecondary),
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.background,
      foregroundColor: AppColors.textPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontFamily: fontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
        letterSpacing: 0.4,
      ),
    ),
    cardTheme: CardTheme(
      color: AppColors.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        side: const BorderSide(color: AppColors.border, width: 1),
      ),
    ),
    dividerColor: AppColors.border,
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: AppColors.surface,
      indicatorColor: AppColors.accent.withOpacity(0.18),
      surfaceTintColor: Colors.transparent,
      labelTextStyle: MaterialStateProperty.resolveWith((states) {
        final selected = states.contains(MaterialState.selected);
        return TextStyle(
          fontSize: 11,
          fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
          color: selected ? AppColors.textPrimary : AppColors.textMuted,
        );
      }),
    ),
    navigationRailTheme: const NavigationRailThemeData(
      backgroundColor: AppColors.surfaceMuted,
      selectedIconTheme: IconThemeData(color: AppColors.accent),
      unselectedIconTheme: IconThemeData(color: AppColors.textMuted),
      selectedLabelTextStyle: TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),
      unselectedLabelTextStyle: TextStyle(
        fontSize: 11,
        color: AppColors.textMuted,
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.surfaceElevated,
      contentTextStyle: const TextStyle(color: AppColors.textPrimary, fontSize: 13),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppSpacing.radiusMd)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.accent,
        foregroundColor: AppColors.textOnAccent,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
        textStyle: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.textPrimary,
        side: const BorderSide(color: AppColors.borderStrong),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surfaceMuted,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        borderSide: const BorderSide(color: AppColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        borderSide: const BorderSide(color: AppColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        borderSide: const BorderSide(color: AppColors.accent, width: 1.4),
      ),
      hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
      labelStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
    ),
    dialogTheme: DialogTheme(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    ),
  );

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: fontFamily,
    scaffoldBackgroundColor: AppColors.lightBackground,
    colorScheme: const ColorScheme.light(
      primary: AppColors.accent,
      onPrimary: AppColors.textOnAccent,
      surface: AppColors.lightSurface,
      onSurface: AppColors.lightTextPrimary,
      error: AppColors.riskCritical,
      outline: AppColors.lightBorder,
    ),
    textTheme: _textTheme(AppColors.lightTextPrimary, AppColors.lightTextSecondary),
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.lightSurface,
      foregroundColor: AppColors.lightTextPrimary,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardTheme(
      color: AppColors.lightSurface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        side: const BorderSide(color: AppColors.lightBorder),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.accent,
        foregroundColor: AppColors.textOnAccent,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
      ),
    ),
  );
}
