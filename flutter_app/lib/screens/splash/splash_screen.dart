import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/network/websocket_client.dart';
import '../auth/login_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    wsClient.connect();
    Future.delayed(const Duration(milliseconds: 1800), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const LoginScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: AppColors.accent.withOpacity(0.16),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.accent.withOpacity(0.45)),
              ),
              child: const Icon(Icons.shield_outlined, size: 40, color: AppColors.accent),
            ),
            const SizedBox(height: 24),
            Text(
              'MINEGUARD',
              style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontSize: 26,
                    letterSpacing: 3,
                  ),
            ),
            const SizedBox(height: 8),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                'REAL-TIME MINE SUBSIDENCE MONITORING & EARLY WARNING SYSTEM',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  letterSpacing: 0.4,
                  color: AppColors.textSecondary,
                  height: 1.4,
                ),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'SIH 2026  •  Underground coal mines, India',
              style: TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 40),
            const SizedBox(
              width: 22,
              height: 22,
              child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.accent),
            ),
          ],
        ),
      ),
    );
  }
}