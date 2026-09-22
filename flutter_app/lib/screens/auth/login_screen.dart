import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../widgets/app_shell.dart';
import '../../widgets/language_selector.dart';
import '../../widgets/ui_kit.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController(text: 'engineer@mine.com');
  final _passwordController = TextEditingController(text: 'station2026');
  bool _obscurePassword = true;
  bool _rememberMe = true;
  bool _isSignUp = false;
  bool _loading = false;

  Future<void> _handleLogin() async {
    setState(() => _loading = true);
    await Future<void>.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const AppShell()),
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final wide = MediaQuery.of(context).size.width >= 900;

    final form = _LoginForm(
      emailController: _emailController,
      passwordController: _passwordController,
      obscurePassword: _obscurePassword,
      rememberMe: _rememberMe,
      isSignUp: _isSignUp,
      loading: _loading,
      onToggleObscure: () => setState(() => _obscurePassword = !_obscurePassword),
      onRemember: (v) => setState(() => _rememberMe = v),
      onToggleMode: (signUp) => setState(() => _isSignUp = signUp),
      onSubmit: _handleLogin,
    );

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: wide
            ? Row(
                children: [
                  Expanded(child: _BrandPanel()),
                  Expanded(child: Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 440), child: form))),
                ],
              )
            : Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                    child: Row(
                      children: [
                        const Icon(Icons.shield_outlined, color: AppColors.accent, size: 18),
                        const SizedBox(width: 8),
                        Text('MINEGUARD', style: Theme.of(context).textTheme.titleMedium),
                        const Spacer(),
                        const LanguageSelector(),
                      ],
                    ),
                  ),
                  Expanded(child: SingleChildScrollView(padding: const EdgeInsets.all(20), child: form)),
                ],
              ),
      ),
    );
  }
}

class _BrandPanel extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.surfaceMuted,
      padding: const EdgeInsets.all(40),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const LanguageSelector(),
          const SizedBox(height: 32),
          const Icon(Icons.shield_outlined, size: 36, color: AppColors.accent),
          const SizedBox(height: 16),
          Text('MINEGUARD', style: Theme.of(context).textTheme.displaySmall?.copyWith(fontSize: 32, letterSpacing: 2)),
          const SizedBox(height: 12),
          const Text(
            'REAL-TIME MINE SUBSIDENCE MONITORING & EARLY WARNING SYSTEM',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.5, letterSpacing: 0.3),
          ),
          const SizedBox(height: 24),
          Text(
            'Operator console for underground coal mine geotechnical monitoring.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}

class _LoginForm extends StatelessWidget {
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool obscurePassword;
  final bool rememberMe;
  final bool isSignUp;
  final bool loading;
  final VoidCallback onToggleObscure;
  final ValueChanged<bool> onRemember;
  final ValueChanged<bool> onToggleMode;
  final VoidCallback onSubmit;

  const _LoginForm({
    required this.emailController,
    required this.passwordController,
    required this.obscurePassword,
    required this.rememberMe,
    required this.isSignUp,
    required this.loading,
    required this.onToggleObscure,
    required this.onRemember,
    required this.onToggleMode,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(isSignUp ? 'Create operator account' : 'Operator sign in', style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 6),
        const Text(
          'Authorized personnel only. Mine safety command access.',
          style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
        ),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(3),
          decoration: BoxDecoration(
            color: AppColors.surfaceMuted,
            borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
            border: Border.all(color: AppColors.border),
          ),
          child: Row(
            children: [
              _tab(context, 'Sign in', !isSignUp, () => onToggleMode(false)),
              _tab(context, 'Register', isSignUp, () => onToggleMode(true)),
            ],
          ),
        ),
        const SizedBox(height: 20),
        Text('EMAIL', style: Theme.of(context).textTheme.labelSmall),
        const SizedBox(height: 6),
        TextField(
          controller: emailController,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            hintText: 'operator@mine.gov.in',
            prefixIcon: Icon(Icons.mail_outline, size: 18, color: AppColors.textMuted),
          ),
        ),
        const SizedBox(height: 14),
        Text('PASSWORD', style: Theme.of(context).textTheme.labelSmall),
        const SizedBox(height: 6),
        TextField(
          controller: passwordController,
          obscureText: obscurePassword,
          decoration: InputDecoration(
            hintText: '••••••••',
            prefixIcon: const Icon(Icons.lock_outline, size: 18, color: AppColors.textMuted),
            suffixIcon: IconButton(
              tooltip: obscurePassword ? 'Show password' : 'Hide password',
              icon: Icon(
                obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                size: 18,
                color: AppColors.textMuted,
              ),
              onPressed: onToggleObscure,
            ),
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            SizedBox(
              height: 24,
              width: 24,
              child: Checkbox(
                value: rememberMe,
                onChanged: (v) => onRemember(v ?? true),
              ),
            ),
            const SizedBox(width: 8),
            const Text('Remember this station', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          ],
        ),
        const SizedBox(height: 18),
        PrimaryButton(
          label: isSignUp ? 'Register and enter console' : 'Enter monitoring console',
          icon: Icons.login,
          loading: loading,
          onPressed: onSubmit,
        ),
        const SizedBox(height: 16),
        const Text(
          'MINEGUARD  v1.0.0  •  SIH 2026',
          style: TextStyle(fontSize: 10, color: AppColors.textMuted),
        ),
      ],
    );
  }

  Widget _tab(BuildContext context, String label, bool selected, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: selected ? AppColors.surface : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: selected ? AppColors.textPrimary : AppColors.textMuted,
            ),
          ),
        ),
      ),
    );
  }
}
