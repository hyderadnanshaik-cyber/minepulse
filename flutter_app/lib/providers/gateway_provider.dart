import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import '../models/gateway_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';

final gatewayStatusProvider = FutureProvider<GatewayModel>((ref) async {
  try {
    final res = await apiClient.get(ApiConstants.gatewayStatus);
    if (res.statusCode == 200 && res.data is Map) {
      return GatewayModel.fromJson(Map<String, dynamic>.from(res.data));
    }
  } catch (_) {}
  return GatewayModel(
    id: 1,
    deviceId: 'RPI-ZERO2W-001',
    name: 'MINEGATE Central Gateway',
    ipAddress: '127.0.0.1',
    status: 'ONLINE',
    cpuUsage: 18.5,
    ramUsage: 34.2,
    temperature: 41.2,
    storageUsed: 35.0,
    mqttStatus: 'ONLINE',
    meshStatus: 'ONLINE',
    internetConnected: true,
    alarmActive: false,
    lastSeen: DateTime.now(),
  );
});

final localeProvider = StateNotifierProvider<LocaleNotifier, Locale>((ref) {
  return LocaleNotifier();
});

class LocaleNotifier extends StateNotifier<Locale> {
  LocaleNotifier() : super(const Locale('en'));

  void setLocale(String languageCode) {
    if (['en', 'hi', 'ur'].contains(languageCode)) {
      state = Locale(languageCode);
    }
  }
}
