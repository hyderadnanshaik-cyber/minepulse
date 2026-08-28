class TelemetryModel {
  final int? readingId;
  final String nodeCode;
  final DateTime timestamp;

  // MPU9250 9-Axis Motion
  final double tiltX;
  final double tiltY;
  final double vibration;
  final double accelX;
  final double accelY;
  final double accelZ;
  final double gyroX;
  final double gyroY;
  final double gyroZ;

  // BME280 Environment
  final double temperature;
  final double humidity;
  final double pressure;

  // Draw-Wire Subsidence Displacement
  final double displacement;
  final double displacementRate;
  final double displacementBaseline;

  // ADS1115 Potentiometric Crack Gauge
  final bool crackDetected;
  final double crackWidth;

  // Power & LoRa Mesh
  final double battery;
  final double rssi;
  final int hopCount;
  final String? parentNodeId;

  TelemetryModel({
    this.readingId,
    required this.nodeCode,
    required this.timestamp,
    required this.tiltX,
    required this.tiltY,
    required this.vibration,
    required this.accelX,
    required this.accelY,
    required this.accelZ,
    required this.gyroX,
    required this.gyroY,
    required this.gyroZ,
    required this.temperature,
    required this.humidity,
    required this.pressure,
    required this.displacement,
    required this.displacementRate,
    required this.displacementBaseline,
    required this.crackDetected,
    required this.crackWidth,
    required this.battery,
    required this.rssi,
    required this.hopCount,
    this.parentNodeId,
  });

  factory TelemetryModel.fromJson(Map<String, dynamic> json) {
    return TelemetryModel(
      readingId: json['reading_id'] is int ? json['reading_id'] : json['id'],
      nodeCode: json['node_code'] ?? json['node_id'] ?? 'NODE_01',
      timestamp: json['timestamp'] != null
          ? (DateTime.tryParse(json['timestamp']) ?? DateTime.now())
          : (json['recorded_at'] != null
              ? (DateTime.tryParse(json['recorded_at']) ?? DateTime.now())
              : DateTime.now()),
      tiltX: (json['tilt_x'] ?? json['tilt'] as num?)?.toDouble() ?? 0.0,
      tiltY: (json['tilt_y'] as num?)?.toDouble() ?? 0.0,
      vibration: (json['vibration'] as num?)?.toDouble() ?? 0.02,
      accelX: (json['accel_x'] as num?)?.toDouble() ?? 0.0,
      accelY: (json['accel_y'] as num?)?.toDouble() ?? 0.0,
      accelZ: (json['accel_z'] as num?)?.toDouble() ?? 1.0,
      gyroX: (json['gyro_x'] as num?)?.toDouble() ?? 0.0,
      gyroY: (json['gyro_y'] as num?)?.toDouble() ?? 0.0,
      gyroZ: (json['gyro_z'] as num?)?.toDouble() ?? 0.0,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 25.0,
      humidity: (json['humidity'] as num?)?.toDouble() ?? 55.0,
      pressure: (json['pressure'] as num?)?.toDouble() ?? 1013.25,
      displacement: (json['displacement'] as num?)?.toDouble() ?? 0.0,
      displacementRate: (json['displacement_rate'] as num?)?.toDouble() ?? 0.0,
      displacementBaseline: (json['displacement_baseline'] as num?)?.toDouble() ?? 0.0,
      crackDetected: json['crack_detected'] == true || json['crack_status'] == true,
      crackWidth: (json['crack_width'] as num?)?.toDouble() ?? 0.0,
      battery: (json['battery'] ?? json['battery_level'] as num?)?.toDouble() ?? 94.0,
      rssi: (json['rssi'] ?? json['signal_strength'] as num?)?.toDouble() ?? -68.0,
      hopCount: (json['hop_count'] as num?)?.toInt() ?? 1,
      parentNodeId: json['parent_node_id'],
    );
  }
}
