import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import '../../providers/gateway_provider.dart';
import '../../widgets/app_card.dart';
import '../../widgets/ui_kit.dart';

class GatewayScreen extends ConsumerStatefulWidget {
  const GatewayScreen({super.key});

  @override
  ConsumerState<GatewayScreen> createState() => _GatewayScreenState();
}

class _GatewayScreenState extends ConsumerState<GatewayScreen> {
  bool _isTestingSiren = false;

  Future<void> _testSiren() async {
    setState(() => _isTestingSiren = true);
    try {
      await apiClient.post(ApiConstants.gatewayAlarmTest);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Gateway alarm test command sent')),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to reach gateway alarm endpoint')),
      );
    }
    setState(() => _isTestingSiren = false);
  }

  @override
  Widget build(BuildContext context) {
    final gwAsync = ref.watch(gatewayStatusProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          gwAsync.when(
            data: (gw) => AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.router_outlined, color: AppColors.accent, size: 20),
                      const SizedBox(width: 8),
                      Expanded(child: Text(gw.name, style: Theme.of(context).textTheme.titleMedium)),
                      StatusBadge(
                        label: gw.status.toUpperCase(),
                        color: gw.status.toUpperCase() == 'ONLINE' ? AppColors.riskLow : AppColors.riskHigh,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Device  ${gw.deviceId}', style: Theme.of(context).textTheme.bodySmall),
                  Text('IP  ${gw.ipAddress}', style: Theme.of(context).textTheme.bodySmall),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 16,
                    runSpacing: 12,
                    children: [
                      _stat('CPU', '${gw.cpuUsage.toStringAsFixed(1)}%'),
                      _stat('RAM', '${gw.ramUsage.toStringAsFixed(1)}%'),
                      _stat('Thermal', '${gw.temperature.toStringAsFixed(1)} °C'),
                      _stat('Storage', '${gw.storageUsed.toStringAsFixed(0)}%'),
                      _stat('MQTT', gw.mqttStatus),
                      _stat('Mesh', gw.meshStatus),
                      _stat('Internet', gw.internetConnected ? 'Connected' : 'Offline'),
                      _stat('Last seen', gw.lastSeen.toLocal().toString().split('.').first),
                    ],
                  ),
                ],
              ),
            ),
            loading: () => const LoadingState(message: 'Checking gateway…'),
            error: (_, __) => const ErrorState(message: 'Gateway offline or unreachable'),
          ),
          const SizedBox(height: AppSpacing.xl),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Evacuation siren test', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 6),
                Text(
                  'Sends the existing gateway alarm test command. Hardware actuation depends on the connected Raspberry Pi gateway.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 14),
                PrimaryButton(
                  label: _isTestingSiren ? 'Sending command…' : 'Test alarm',
                  icon: Icons.campaign_outlined,
                  color: AppColors.riskCritical,
                  loading: _isTestingSiren,
                  onPressed: _testSiren,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _stat(String label, String val) {
    return SizedBox(
      width: 140,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
          const SizedBox(height: 2),
          Text(val, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
