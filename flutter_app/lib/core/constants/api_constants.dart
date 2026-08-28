class ApiConstants {
  // Configurable base URL:
  // For Android Emulator -> http://10.0.2.2:8000/api
  // For Windows / Web / Real Device -> http://127.0.0.1:8000/api or Azure URL
  static const String localBaseUrl = 'http://127.0.0.1:8000/api';
  static const String androidEmulatorBaseUrl = 'http://10.0.2.2:8000/api';
  static const String azureBaseUrl = 'https://mineguard-sih-api.azurewebsites.net/api';

  static String baseUrl = localBaseUrl;

  // Endpoints
  static const String nodes = '/nodes';
  static const String telemetry = '/telemetry';
  static const String alerts = '/alerts';
  static const String aiStatus = '/ai/status';
  static const String aiPredictions = '/ai/predictions';
  static const String aiTrain = '/ai/train';
  static const String gisNodes = '/gis/nodes';
  static const String gisPanels = '/gis/panels';
  static const String gatewayStatus = '/gateway/status';
  static const String gatewayAlarmTest = '/gateway/alarm/test';
  static const String reportsSummary = '/reports/summary';
  static const String reportsEvents = '/reports/events';
  static const String systemHealth = '/system/health';
  static const String systemConnectivity = '/system/connectivity';
  static const String scenarioTrigger = '/system/scenario/trigger';

  // WebSocket endpoints
  static const String wsTelemetry = 'ws://127.0.0.1:8000/ws/telemetry';
  static const String wsAlerts = 'ws://127.0.0.1:8000/ws/alerts';

  // DGMS Statutory Geotechnical Thresholds
  static const double maxSubsidenceDisplacementMm = 25.0;
  static const double maxStrataTiltDeg = 3.5;
  static const double maxCrackFissureWidthMm = 3.0;
  static const double maxVibrationG = 0.45;
}
