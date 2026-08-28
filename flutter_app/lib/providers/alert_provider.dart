import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/alert_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';
import '../core/network/websocket_client.dart';

final alertListProvider = StateNotifierProvider<AlertListNotifier, List<AlertModel>>((ref) {
  return AlertListNotifier();
});

class AlertListNotifier extends StateNotifier<List<AlertModel>> {
  AlertListNotifier() : super([]) {
    fetchAlerts();
    listenToAlertWebSocket();
  }

  Future<void> fetchAlerts() async {
    try {
      final res = await apiClient.get(ApiConstants.alerts, queryParameters: {'limit': 20});
      if (res.statusCode == 200 && res.data is List) {
        state = (res.data as List).map((i) => AlertModel.fromJson(i as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
  }

  void listenToAlertWebSocket() {
    wsClient.alertStream.listen((data) {
      final alert = AlertModel.fromJson(data);
      state = [alert, ...state];
    });
  }

  Future<void> acknowledgeAlert(int alertId) async {
    try {
      await apiClient.post('${ApiConstants.alerts}/$alertId/acknowledge', data: {
        'acknowledged_by': 'Flutter Operator Console',
      });
      await fetchAlerts();
    } catch (_) {}
  }
}
