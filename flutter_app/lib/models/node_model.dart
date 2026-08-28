class NodeModel {
  final int id;
  final String nodeCode;
  final String nodeName;
  final String status;
  final String riskLevel;
  final double riskScore;
  final double? latitude;
  final double? longitude;
  final double battery;
  final double signalStrength;
  final int hopCount;
  final String? parentNodeId;
  final List<dynamic>? meshRoute;
  final DateTime? lastSeen;

  NodeModel({
    required this.id,
    required this.nodeCode,
    required this.nodeName,
    required this.status,
    required this.riskLevel,
    required this.riskScore,
    this.latitude,
    this.longitude,
    required this.battery,
    required this.signalStrength,
    required this.hopCount,
    this.parentNodeId,
    this.meshRoute,
    this.lastSeen,
  });

  factory NodeModel.fromJson(Map<String, dynamic> json) {
    return NodeModel(
      id: json['id'] is int ? json['id'] : (int.tryParse(json['id']?.toString() ?? '1') ?? 1),
      nodeCode: json['node_code'] ?? json['node_id'] ?? 'NODE_01',
      nodeName: json['node_name'] ?? json['name'] ?? 'MINEGUARD Station',
      status: json['status'] ?? 'ONLINE',
      riskLevel: json['risk_level'] ?? 'NORMAL',
      riskScore: (json['risk_score'] as num?)?.toDouble() ?? 5.0,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      battery: (json['battery'] ?? json['battery_level'] as num?)?.toDouble() ?? 94.0,
      signalStrength: (json['signal_strength'] ?? json['rssi'] as num?)?.toDouble() ?? -68.0,
      hopCount: (json['hop_count'] as num?)?.toInt() ?? 1,
      parentNodeId: json['parent_node_id'],
      meshRoute: json['mesh_route'] is List ? json['mesh_route'] : null,
      lastSeen: json['last_seen'] != null ? DateTime.tryParse(json['last_seen']) : null,
    );
  }
}
