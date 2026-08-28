import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../constants/api_constants.dart';

class WebSocketClient {
  WebSocketChannel? _telemetryChannel;
  WebSocketChannel? _alertChannel;

  final _telemetryController = StreamController<Map<String, dynamic>>.broadcast();
  final _alertController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get telemetryStream => _telemetryController.stream;
  Stream<Map<String, dynamic>> get alertStream => _alertController.stream;

  bool _isConnected = false;
  bool get isConnected => _isConnected;

  void connect() {
    try {
      _telemetryChannel = WebSocketChannel.connect(Uri.parse(ApiConstants.wsTelemetry));
      _telemetryChannel?.stream.listen(
        (data) {
          try {
            final decoded = jsonDecode(data as String) as Map<String, dynamic>;
            _telemetryController.add(decoded);
            _isConnected = true;
          } catch (_) {}
        },
        onError: (err) {
          _isConnected = false;
          _reconnectTelemetry();
        },
        onDone: () {
          _isConnected = false;
          _reconnectTelemetry();
        },
      );

      _alertChannel = WebSocketChannel.connect(Uri.parse(ApiConstants.wsAlerts));
      _alertChannel?.stream.listen(
        (data) {
          try {
            final decoded = jsonDecode(data as String) as Map<String, dynamic>;
            _alertController.add(decoded);
          } catch (_) {}
        },
        onError: (_) {},
        onDone: () {},
      );
    } catch (_) {
      _isConnected = false;
    }
  }

  void _reconnectTelemetry() {
    Future.delayed(const Duration(seconds: 5), () {
      if (!_isConnected) connect();
    });
  }

  void disconnect() {
    _telemetryChannel?.sink.close();
    _alertChannel?.sink.close();
    _isConnected = false;
  }
}

final wsClient = WebSocketClient();
