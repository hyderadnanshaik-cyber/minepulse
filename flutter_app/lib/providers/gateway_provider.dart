import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/gateway_model.dart';
import '../core/network/api_client.dart';
import '../core/constants/api_constants.dart';

final gatewayStatusProvider = FutureProvider<GatewayModel>((ref) async {
  final res = await apiClient.get(ApiConstants.gatewayStatus);
  if (res.statusCode == 200 && res.data is Map) {
    return GatewayModel.fromJson(Map<String, dynamic>.from(res.data));
  }
  throw Exception('Unable to retrieve gateway status');
});
