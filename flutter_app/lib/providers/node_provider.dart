import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/node_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';

final nodesProvider = FutureProvider<List<NodeModel>>((ref) async {
  try {
    final res = await apiClient.get(ApiConstants.nodes);
    if (res.statusCode == 200 && res.data is List) {
      return (res.data as List).map((i) => NodeModel.fromJson(i as Map<String, dynamic>)).toList();
    }
  } catch (_) {}
  return [];
});

final selectedNodeIdProvider = StateProvider<String>((ref) => 'NODE_03');
