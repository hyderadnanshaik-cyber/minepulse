class GatewayModel {
  final int id;
  final String deviceId;
  final String name;
  final String ipAddress;
  final String status;
  final double cpuUsage;
  final double ramUsage;
  final double temperature;
  final double storageUsed;
  final String mqttStatus;
  final String meshStatus;
  final bool internetConnected;
  final bool alarmActive;
  final DateTime lastSeen;

  GatewayModel({
    required this.id,
    required this.deviceId,
    required this.name,
    required this.ipAddress,
    required this.status,
    required this.cpuUsage,
    required this.ramUsage,
    required this.temperature,
    required this.storageUsed,
    required this.mqttStatus,
    required this.meshStatus,
    required this.internetConnected,
    required this.alarmActive,
    required this.lastSeen,
  });

  factory GatewayModel.fromJson(Map<String, dynamic> json) {
    return GatewayModel(
      id: json['id'] is int ? json['id'] : 1,
      deviceId: json['device_id'] ?? 'RPI-ZERO2W-001',
      name: json['name'] ?? 'MINEGATE Central Gateway',
      ipAddress: json['ip_address'] ?? '127.0.0.1',
      status: json['status'] ?? 'ONLINE',
      cpuUsage: (json['cpu_usage'] as num?)?.toDouble() ?? 18.5,
      ramUsage: (json['ram_usage'] as num?)?.toDouble() ?? 34.2,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 41.2,
      storageUsed: (json['storage_used'] as num?)?.toDouble() ?? 35.0,
      mqttStatus: json['mqtt_status'] ?? 'ONLINE',
      meshStatus: json['mesh_status'] ?? 'ONLINE',
      internetConnected: json['internet_connected'] == true,
      alarmActive: json['alarm_active'] == true,
      lastSeen: json['last_seen'] != null
          ? (DateTime.tryParse(json['last_seen']) ?? DateTime.now())
          : DateTime.now(),
    );
  }
}
