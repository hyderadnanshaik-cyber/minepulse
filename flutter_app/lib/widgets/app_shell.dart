import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/localization/app_localizations.dart';
import '../core/theme/app_colors.dart';
import '../core/theme/app_spacing.dart';
import '../providers/alert_provider.dart';
import '../providers/connection_provider.dart';
import '../providers/telemetry_provider.dart';
import '../screens/ai/ai_analytics_screen.dart';
import '../screens/alerts/alerts_screen.dart';
import '../screens/dashboard/dashboard_screen.dart';
import '../screens/gateway/gateway_screen.dart';
import '../screens/gis/gis_map_screen.dart';
import '../screens/nodes/nodes_screen.dart';
import '../screens/reports/reports_screen.dart';
import '../screens/settings/settings_screen.dart';
import '../screens/telemetry/telemetry_screen.dart';
import '../widgets/language_selector.dart';
import '../widgets/subsidence_alert_dialog.dart';
import '../widgets/ui_kit.dart';

class AppNavItem {
  final String labelKey;
  final String fallback;
  final IconData icon;
  final IconData selectedIcon;

  const AppNavItem(this.labelKey, this.fallback, this.icon, this.selectedIcon);
}

const kNavItems = [
  AppNavItem('dashboard', 'Dashboard', Icons.dashboard_outlined, Icons.dashboard),
  AppNavItem('telemetry', 'Telemetry', Icons.show_chart, Icons.show_chart),
  AppNavItem('gis_map', 'Mine Map', Icons.map_outlined, Icons.map),
  AppNavItem('alerts', 'Alerts', Icons.notifications_none, Icons.notifications_active),
  AppNavItem('nodes', 'Nodes', Icons.sensors_outlined, Icons.sensors),
  AppNavItem('ai_analytics', 'AI Risk', Icons.psychology_outlined, Icons.psychology),
  AppNavItem('gateway', 'Gateway', Icons.router_outlined, Icons.router),
  AppNavItem('reports', 'Reports', Icons.assessment_outlined, Icons.assessment),
  AppNavItem('settings', 'Settings', Icons.settings_outlined, Icons.settings),
];

class AppShell extends ConsumerStatefulWidget {
  const AppShell({super.key});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  int _index = 0;
  bool _alertModalShown = false;

  static const _mobilePrimary = [0, 1, 2, 3]; // Dashboard, Telemetry, GIS, Alerts

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final alerts = ref.watch(alertListProvider);
    final wsAsync = ref.watch(connectionStatusProvider);
    final live = wsAsync.valueOrNull == true;
    final width = MediaQuery.of(context).size.width;
    final isDesktop = width >= 1100;
    final isTablet = width >= 700 && width < 1100;

    if (alerts.isNotEmpty && !_alertModalShown) {
      final criticalAlert = alerts.firstWhere(
        (a) => a.severity == 'CRITICAL' && (a.status == 'DETECTED' || a.status == 'ACTIVE'),
        orElse: () => alerts.first,
      );
      if (criticalAlert.severity == 'CRITICAL') {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted && !_alertModalShown) {
            setState(() => _alertModalShown = true);
            showDialog(
              context: context,
              barrierDismissible: true,
              builder: (ctx) => SubsidenceAlertDialog(
                alert: criticalAlert,
                onAcknowledge: () {
                  ref.read(alertListProvider.notifier).acknowledgeAlert(criticalAlert.id);
                  Navigator.of(ctx).pop();
                },
                onViewGis: () {
                  Navigator.of(ctx).pop();
                  setState(() => _index = 2);
                },
              ),
            );
          }
        });
      }
    }

    final pages = const [
      DashboardHome(),
      TelemetryScreen(),
      GisMapScreen(),
      AlertsScreen(),
      NodesScreen(),
      AiAnalyticsScreen(),
      GatewayScreen(),
      ReportsScreen(),
      SettingsScreen(),
    ];

    final header = _AppHeader(
      title: l10n.translate('app_title'),
      subtitle: l10n.translate('app_subtitle'),
      live: live,
      onRefresh: () {
        ref.read(latestTelemetryProvider.notifier).fetchInitialTelemetry();
        ref.read(alertListProvider.notifier).fetchAlerts();
      },
    );

    Widget body = Column(
      children: [
        header,
        Expanded(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 220),
            child: KeyedSubtree(
              key: ValueKey(_index),
              child: pages[_index],
            ),
          ),
        ),
      ],
    );

    if (isDesktop) {
      return Scaffold(
        body: Row(
          children: [
            _DesktopSidebar(
              index: _index,
              onSelect: (i) => setState(() => _index = i),
              l10n: l10n,
            ),
            VerticalDivider(width: 1, color: AppColors.border),
            Expanded(child: body),
          ],
        ),
      );
    }

    if (isTablet) {
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              labelType: NavigationRailLabelType.all,
              destinations: [
                for (final item in kNavItems)
                  NavigationRailDestination(
                    icon: Icon(item.icon),
                    selectedIcon: Icon(item.selectedIcon),
                    label: Text(l10n.translate(item.labelKey)),
                  ),
              ],
            ),
            const VerticalDivider(width: 1, color: AppColors.border),
            Expanded(child: body),
          ],
        ),
      );
    }

    final moreSelected = !_mobilePrimary.contains(_index);
    return Scaffold(
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: moreSelected ? 4 : _mobilePrimary.indexOf(_index),
        onDestinationSelected: (i) {
          if (i == 4) {
            _openMoreSheet(context, l10n);
          } else {
            setState(() => _index = _mobilePrimary[i]);
          }
        },
        destinations: [
          NavigationDestination(
            icon: Icon(kNavItems[0].icon),
            selectedIcon: Icon(kNavItems[0].selectedIcon),
            label: l10n.translate(kNavItems[0].labelKey),
          ),
          NavigationDestination(
            icon: Icon(kNavItems[1].icon),
            selectedIcon: Icon(kNavItems[1].selectedIcon),
            label: l10n.translate(kNavItems[1].labelKey),
          ),
          NavigationDestination(
            icon: Icon(kNavItems[2].icon),
            selectedIcon: Icon(kNavItems[2].selectedIcon),
            label: l10n.translate(kNavItems[2].labelKey),
          ),
          NavigationDestination(
            icon: Icon(kNavItems[3].icon),
            selectedIcon: Icon(kNavItems[3].selectedIcon),
            label: l10n.translate(kNavItems[3].labelKey),
          ),
          NavigationDestination(
            icon: Icon(moreSelected ? Icons.menu_open : Icons.menu),
            label: 'More',
          ),
        ],
      ),
    );
  }

  void _openMoreSheet(BuildContext context, AppLocalizations l10n) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(height: 8),
              Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.borderStrong,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 8),
              for (int i = 4; i < kNavItems.length; i++)
                ListTile(
                  leading: Icon(kNavItems[i].icon, color: AppColors.textSecondary),
                  title: Text(l10n.translate(kNavItems[i].labelKey)),
                  selected: _index == i,
                  onTap: () {
                    Navigator.pop(ctx);
                    setState(() => _index = i);
                  },
                ),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
  }
}

class _AppHeader extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool live;
  final VoidCallback onRefresh;

  const _AppHeader({
    required this.title,
    required this.subtitle,
    required this.live,
    required this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 8, 8),
      decoration: const BoxDecoration(
        color: AppColors.background,
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: SafeArea(
        bottom: false,
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.accent.withOpacity(0.18),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.accent.withOpacity(0.4)),
              ),
              child: const Icon(Icons.shield_outlined, size: 16, color: AppColors.accent),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.titleMedium),
                  Text(
                    subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            StatusBadge(
              label: live ? 'LIVE' : 'OFFLINE',
              color: live ? AppColors.riskLow : AppColors.riskHigh,
              icon: live ? Icons.wifi : Icons.wifi_off,
            ),
            IconButton(
              tooltip: 'Refresh',
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh, size: 20),
            ),
          ],
        ),
      ),
    );
  }
}

class _DesktopSidebar extends StatelessWidget {
  final int index;
  final ValueChanged<int> onSelect;
  final AppLocalizations l10n;

  const _DesktopSidebar({
    required this.index,
    required this.onSelect,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 228,
      color: AppColors.surfaceMuted,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 20),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('MINEGUARD', style: Theme.of(context).textTheme.titleMedium?.copyWith(letterSpacing: 1.2)),
                const SizedBox(height: 4),
                Text(
                  'SUBSIDENCE MONITORING',
                  style: Theme.of(context).textTheme.labelSmall,
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 12),
            child: LanguageSelector(lightOnDark: true),
          ),
          const SizedBox(height: 12),
          const Divider(color: AppColors.border, height: 1),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
              itemCount: kNavItems.length,
              itemBuilder: (context, i) {
                final item = kNavItems[i];
                final selected = index == i;
                return Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Material(
                    color: selected ? AppColors.accent.withOpacity(0.14) : Colors.transparent,
                    borderRadius: BorderRadius.circular(10),
                    child: ListTile(
                      dense: true,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      leading: Icon(
                        selected ? item.selectedIcon : item.icon,
                        size: 20,
                        color: selected ? AppColors.accent : AppColors.textMuted,
                      ),
                      title: Text(
                        l10n.translate(item.labelKey),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                          color: selected ? AppColors.textPrimary : AppColors.textSecondary,
                        ),
                      ),
                      onTap: () => onSelect(i),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
