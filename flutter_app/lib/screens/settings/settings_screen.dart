import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../providers/locale_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/language_selector.dart';
import '../../widgets/ui_kit.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _audioSirenEnabled = true;

  @override
  Widget build(BuildContext context) {
    final dark = ref.watch(themeModeProvider) == ThemeMode.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Language', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                Text(
                  'English, Hindi, and Urdu. Sensor names remain in technical English.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 12),
                const LanguageSelector(compact: false),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          AppCard(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Audio siren alerts', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  subtitle: const Text('Audible warning on critical alerts', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  value: _audioSirenEnabled,
                  onChanged: (val) => setState(() => _audioSirenEnabled = val),
                ),
                const Divider(height: 1, color: AppColors.border),
                SwitchListTile(
                  title: const Text('Dark industrial theme', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  subtitle: const Text('High-contrast monitoring display', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  value: dark,
                  onChanged: (val) => ref.read(themeModeProvider.notifier).state = val ? ThemeMode.dark : ThemeMode.light,
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          const Center(
            child: Column(
              children: [
                Text('MINEGUARD v1.0.0  •  SIH 2026', style: TextStyle(fontSize: 11, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
                SizedBox(height: 4),
                Text('Real-time mine subsidence monitoring', style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
