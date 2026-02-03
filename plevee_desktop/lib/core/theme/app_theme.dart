import 'package:flutter/material.dart';
import 'colors.dart';
import 'typography.dart';

/// Main theme configuration for Plevee
class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.deepNavy,
      
      // Color scheme
      colorScheme: const ColorScheme.dark(
        primary: AppColors.electricBlue,
        secondary: AppColors.profitGreen,
        surface: AppColors.darkNavy,
        error: AppColors.lossRed,
        onPrimary: AppColors.deepNavy,
        onSecondary: AppColors.deepNavy,
        onSurface: AppColors.white,
        onError: AppColors.white,
      ),
      
      // App bar theme
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        titleTextStyle: AppTypography.h3.copyWith(color: AppColors.white),
        iconTheme: const IconThemeData(color: AppColors.white),
      ),
      
      // Card theme
      cardTheme: const CardThemeData(
        color: AppColors.glassWhite,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
      
      // Elevated button theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.electricBlue,
          foregroundColor: AppColors.deepNavy,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: AppTypography.button,
        ),
      ),
      
      // Text button theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.electricBlue,
          textStyle: AppTypography.button,
        ),
      ),
      
      // Input decoration theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.glassWhite,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.electricBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.lossRed, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        hintStyle: AppTypography.body1.copyWith(color: AppColors.gray),
      ),
      
      // Text theme
      textTheme: TextTheme(
        displayLarge: AppTypography.display1.copyWith(color: AppColors.white),
        displayMedium: AppTypography.display2.copyWith(color: AppColors.white),
        headlineLarge: AppTypography.h1.copyWith(color: AppColors.white),
        headlineMedium: AppTypography.h2.copyWith(color: AppColors.white),
        headlineSmall: AppTypography.h3.copyWith(color: AppColors.white),
        titleLarge: AppTypography.h4.copyWith(color: AppColors.white),
        bodyLarge: AppTypography.body1.copyWith(color: AppColors.white),
        bodyMedium: AppTypography.body2.copyWith(color: AppColors.white),
        bodySmall: AppTypography.caption.copyWith(color: AppColors.gray),
        labelLarge: AppTypography.button.copyWith(color: AppColors.white),
      ),
    );
  }
}
