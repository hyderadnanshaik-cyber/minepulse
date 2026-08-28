import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/telemetry_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';
import '../core/network/websocket_client.dart';

final latestTelemetryProvider = StateNotifierProvider<LatestTelemetryNotifier, Map<String, TelemetryModel>>((ref) {
  return LatestTelemetryNotifier();
});

class LatestTelemetryNotifier extends StateNotifier<Map<String, TelemetryModel>> {
  LatestTelemetryNotifier() : super({}) {
    fetchInitialTelemetry();
    listenToLiveWebSocket();
  }

  Future<void> fetchInitialTelemetry() async {
    try {
      final res = await apiClient.get(ApiConstants.telemetry);
      if (res.statusCode == 200 && res.data is List) {
        final map = <String, TelemetryModel>{};
        for (var item in res.data) {
          final model = TelemetryModel.fromJson(item as Map<String, dynamic>);
          map[model.nodeCode] = model;
        }
        state = map;
      }
    } catch (_) {}
  }

  void listenToLiveWebSocket() {
    wsClient.telemetryStream.listen((data) {
      final model = TelemetryModel.fromJson(data);
      state = {...state, model.nodeCode: model};
    });
  }
}

final nodeHistoryProvider = FutureProvider.family<List<TelemetryModel>, String>((ref, nodeCode) async {
  try {
    final res = await apiClient.get('${ApiConstants.telemetry}/$nodeCode', queryParameters: {'limit': 50});
    if (res.statusCode == 200 && res.data is List) {
      return (res.data as List).map((i) => TelemetryModel.fromJson(i as Map<String, dynamic>)).toList();
    }
  } catch (_) {}
  return [];
});
