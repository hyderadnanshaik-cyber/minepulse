import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_spacing.dart';
import '../providers/locale_provider.dart';

class LanguageSelector extends ConsumerWidget {
  final bool compact;
  final bool lightOnDark;

  const LanguageSelector({
    super.key,
    this.compact = true,
    this.lightOnDark = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final current = ref.watch(localeProvider).languageCode;
    final items = const [
      ('EN', 'en'),
      ('हिन्दी', 'hi'),
      ('اردو', 'ur'),
    ];

    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        color: lightOnDark ? Colors.white.withOpacity(0.06) : AppColors.surfaceMuted,
        borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: items.map((item) {
          final selected = current == item.$2;
          return GestureDetector(
            onTap: () => ref.read(localeProvider.notifier).setLocale(item.$2),
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: compact ? 8 : 12, vertical: 5),
              decoration: BoxDecoration(
                color: selected ? AppColors.accent.withOpacity(0.22) : Colors.transparent,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                item.$1,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  color: selected ? AppColors.textPrimary : AppColors.textMuted,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
