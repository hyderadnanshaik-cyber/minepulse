import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../providers/gateway_provider.dart';

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
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('📢 Industrial Evacuation Siren Relay (GPIO 18) Triggered for 3 Seconds'),
          backgroundColor: AppTheme.highOrange,
        ),
      );
    } catch (_) {}
    setState(() => _isTestingSiren = false);
  }

  @override
  Widget build(BuildContext context) {
    final gwAsync = ref.watch(gatewayStatusProvider);

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Gateway Device Card
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
                          Icon(Icons.router_rounded, color: AppTheme.primaryBlue, size: 22),
                          SizedBox(width: 8),
                          Text(
                            'MINEGATE EDGE GATEWAY',
                            style: TextStyle(fontWeight: FontWeight.w900, fontSize: 13),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFD1FAE5),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'HARDWARE ONLINE',
                          style: TextStyle(color: AppTheme.safeEmerald, fontWeight: FontWeight.w900, fontSize: 10),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  gwAsync.when(
                    data: (gw) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Hardware: Raspberry Pi Zero 2 W • IN865 LoRa Hat',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text('Local IP: ${gw.ipAddress} • SQLite Edge Buffer: Active (edge_buffer.db)',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                        const SizedBox(height: 14),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            _buildStatItem('CPU Load', '${gw.cpuUsage.toStringAsFixed(1)}%'),
                            _buildStatItem('RAM Used', '${gw.ramUsage.toStringAsFixed(1)}%'),
                            _buildStatItem('Thermal', '${gw.temperature.toStringAsFixed(1)}°C'),
                            _buildStatItem('MQTT Status', gw.mqttStatus),
                          ],
                        ),
                      ],
                    ),
                    loading: () => const CircularProgressIndicator(),
                    error: (_, __) => const SizedBox(),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Siren Emergency Relay Control
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
                  const Row(
                    children: [
                      Icon(Icons.volume_up_rounded, color: AppTheme.criticalRed, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'EVACUATION SIREN RELAY (GPIO 18)',
                        style: TextStyle(fontWeight: FontWeight.w900, fontSize: 12),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Direct hardware optocoupler relay control on the Raspberry Pi Zero 2 W edge gateway. Triggers statutory mine evacuation acoustic siren upon critical threshold trip.',
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.4),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.criticalRed,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      icon: _isTestingSiren
                          ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.campaign_rounded, size: 18),
                      label: Text(_isTestingSiren ? 'Actuating Relay (GPIO 18)...' : 'Test Acoustic Evacuation Siren'),
                      onPressed: _isTestingSiren ? null : _testSiren,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String val) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 9, color: Color(0xFF94A3B8), fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(val, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, fontFamily: 'monospace')),
      ],
    );
  }
}
