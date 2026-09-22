import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/network/websocket_client.dart';

/// Polls the existing WebSocket client connection flag. Does not invent a new transport.
final connectionStatusProvider = StreamProvider<bool>((ref) async* {
  yield wsClient.isConnected;
  yield* Stream<bool>.periodic(
    const Duration(seconds: 2),
    (_) => wsClient.isConnected,
  );
});
