import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/locale_provider.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _audioSirenEnabled = true;
  bool _darkMode = false;

  @override
  Widget build(BuildContext context) {
    final currentLocale = ref.watch(localeProvider);

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Security Center Status Card (Reference Design 3)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.verified_user_rounded, color: AppTheme.primaryBlue, size: 22),
                          SizedBox(width: 8),
                          Text(
                            'SECURITY CENTER',
                            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 13),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFD1FAE5),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          'SECURITY LEVEL: OPTIMAL',
                          style: TextStyle(color: AppTheme.safeEmerald, fontWeight: FontWeight.w900, fontSize: 10),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Progress Bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: const LinearProgressIndicator(
                      value: 1.0,
                      backgroundColor: Color(0xFFE2E8F0),
                      valueColor: AlwaysStoppedAnimation<Color>(AppTheme.safeEmerald),
                      minHeight: 6,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildCheckItem('Firebase Auth Token Verified', true),
                  _buildCheckItem('LoRa IN865 Mesh Network Online', true),
                  _buildCheckItem('GPIO 18 Siren Relay Armed', true),
                  _buildCheckItem('Azure PostgreSQL 18 + PostGIS Connected', true),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Interface & Language Picker
            const Text(
              'INTERFACE & MULTILINGUAL LOCALIZATION',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF64748B), letterSpacing: 0.5),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Interface Language (भाषा / زبان)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text('Urdu (UR) activates dynamic RTL layout automatically.', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      _buildLangCard('English', 'en', currentLocale.languageCode),
                      const SizedBox(width: 8),
                      _buildLangCard('हिन्दी', 'hi', currentLocale.languageCode),
                      const SizedBox(width: 8),
                      _buildLangCard('اردو (RTL)', 'ur', currentLocale.languageCode),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Operator Preferences
            const Text(
              'OPERATOR PREFERENCES',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF64748B), letterSpacing: 0.5),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Audio Siren Alerts', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                    subtitle: const Text('Audible warning on critical hazard alerts', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                    value: _audioSirenEnabled,
                    activeColor: AppTheme.primaryBlue,
                    onChanged: (val) => setState(() => _audioSirenEnabled = val),
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Dark Mode Display', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                    subtitle: const Text('High-contrast underground display theme', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                    value: _darkMode,
                    activeColor: AppTheme.primaryBlue,
                    onChanged: (val) => setState(() => _darkMode = val),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Footer
            const Center(
              child: Column(
                children: [
                  Text(
                    'MINEGUARD v1.0.0 — SIH 2026 • Team RED HACK',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Microsoft Azure + PostgreSQL 18 + PostGIS + LoRa IN865',
                    style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCheckItem(String label, bool ok) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(ok ? Icons.check_circle_rounded : Icons.cancel_rounded, size: 16, color: ok ? AppTheme.safeEmerald : AppTheme.criticalRed),
          const SizedBox(width: 8),
          Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF334155))),
        ],
      ),
    );
  }

  Widget _buildLangCard(String label, String code, String currentCode) {
    final isSelected = currentCode == code;
    return Expanded(
      child: GestureDetector(
        onTap: () => ref.read(localeProvider.notifier).setLocale(code),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFFEFF6FF) : const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? AppTheme.primaryBlue : AppTheme.borderSubtle,
              width: isSelected ? 2 : 1,
            ),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isSelected ? AppTheme.primaryBlue : const Color(0xFF0F172A),
            ),
          ),
        ),
      ),
    );
  }
}
