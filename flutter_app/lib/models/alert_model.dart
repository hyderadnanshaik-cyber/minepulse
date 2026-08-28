class AlertModel {
  final int id;
  final String nodeId;
  final String alertType;
  final String severity;
  final String title;
  final String message;
  final double riskScore;
  final double anomalyScore;
  final String status;
  final bool localAlarmActivated;
  final DateTime detectedAt;

  AlertModel({
    required this.id,
    required this.nodeId,
    required this.alertType,
    required this.severity,
    required this.title,
    required this.message,
    required this.riskScore,
    required this.anomalyScore,
    required this.status,
    required this.localAlarmActivated,
    required this.detectedAt,
  });

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id']?.toString() ?? '1') ?? 1,
      nodeId: json['node_id'] ?? json['node_code'] ?? 'NODE_03',
      alertType: json['alert_type'] ?? 'GEOTECHNICAL_HAZARD_DETECTED',
      severity: json['severity'] ?? 'CRITICAL',
      title: json['title'] ?? 'Subsidence Anomaly Detected',
      message: json['message'] ?? 'Hazard threshold trip',
      riskScore: (json['risk_score'] as num?)?.toDouble() ?? 85.0,
      anomalyScore: (json['anomaly_score'] as num?)?.toDouble() ?? 0.75,
      status: json['status'] ?? 'DETECTED',
      localAlarmActivated: json['local_alarm_activated'] == true,
      detectedAt: json['detected_at'] != null
          ? (DateTime.tryParse(json['detected_at']) ?? DateTime.now())
          : DateTime.now(),
    );
  }
}
