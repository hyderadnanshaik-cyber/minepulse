import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/prediction_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';

final aiStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final res = await apiClient.get(ApiConstants.aiStatus);
  if (res.statusCode == 200 && res.data is Map) {
    return Map<String, dynamic>.from(res.data);
  }
  throw Exception('AI model status unavailable');
});

final recentPredictionsProvider = FutureProvider<List<PredictionModel>>((ref) async {
  try {
    final res = await apiClient.get(ApiConstants.aiPredictions, queryParameters: {'limit': 20});
    if (res.statusCode == 200 && res.data is List) {
      return (res.data as List).map((i) => PredictionModel.fromJson(i as Map<String, dynamic>)).toList();
    }
  } catch (_) {}
  return [];
});
