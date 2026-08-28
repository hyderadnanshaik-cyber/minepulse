class PredictionModel {
  final int id;
  final String nodeId;
  final int? readingId;
  final double anomalyScore;
  final double riskScore;
  final String riskLevel;
  final double confidence;
  final Map<String, dynamic>? features;
  final String modelVersion;
  final List<dynamic>? triggeredIndicators;
  final DateTime createdAt;

  PredictionModel({
    required this.id,
    required this.nodeId,
    this.readingId,
    required this.anomalyScore,
    required this.riskScore,
    required this.riskLevel,
    required this.confidence,
    this.features,
    required this.modelVersion,
    this.triggeredIndicators,
    required this.createdAt,
  });

  factory PredictionModel.fromJson(Map<String, dynamic> json) {
    List<dynamic>? indicators;
    if (json['spatial_pattern'] is Map && json['spatial_pattern']['triggered_indicators'] is List) {
      indicators = json['spatial_pattern']['triggered_indicators'];
    }

    return PredictionModel(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id']?.toString() ?? '1') ?? 1,
      nodeId: json['node_id'] ?? 'NODE_01',
      readingId: json['reading_id'],
      anomalyScore: (json['anomaly_score'] as num?)?.toDouble() ?? 0.15,
      riskScore: (json['risk_score'] as num?)?.toDouble() ?? 10.0,
      riskLevel: json['risk_level'] ?? 'NORMAL',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.95,
      features: json['features'] is Map ? Map<String, dynamic>.from(json['features']) : null,
      modelVersion: json['model_version'] ?? 'v2.1.0-IsolationForest',
      triggeredIndicators: indicators,
      createdAt: json['created_at'] != null
          ? (DateTime.tryParse(json['created_at']) ?? DateTime.now())
          : DateTime.now(),
    );
  }
}
