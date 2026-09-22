import '../../models/telemetry_model.dart';
import '../constants/api_constants.dart';

class RiskUtils {
  RiskUtils._();

  static String displayNodeCode(String code) => code.replaceAll('_', '-');

  static String fromTelemetry(TelemetryModel? t) {
    if (t == null) return 'UNKNOWN';
    if (t.displacement >= ApiConstants.maxSubsidenceDisplacementMm ||
        t.tiltX >= ApiConstants.maxStrataTiltDeg ||
        t.crackWidth >= ApiConstants.maxCrackFissureWidthMm ||
        t.vibration >= ApiConstants.maxVibrationG) {
      return 'CRITICAL';
    }
    if (t.displacement >= 20.0 || t.tiltX >= 3.0 || t.crackWidth >= 2.0) {
      return 'HIGH';
    }
    if (t.displacement >= 10.0 || t.tiltX >= 1.5 || t.crackWidth >= 1.0) {
      return 'MEDIUM';
    }
    return 'NORMAL';
  }

  static bool isAbnormal(TelemetryModel? t) {
    final level = fromTelemetry(t);
    return level == 'HIGH' || level == 'CRITICAL';
  }

  static String highest(Iterable<String> levels) {
    const order = ['CRITICAL', 'HIGH', 'MEDIUM', 'WATCH', 'MODERATE', 'NORMAL', 'LOW', 'UNKNOWN'];
    String best = 'NORMAL';
    var bestIdx = order.length;
    for (final level in levels) {
      final idx = order.indexOf(level.toUpperCase());
      final resolved = idx < 0 ? order.length : idx;
      if (resolved < bestIdx) {
        bestIdx = resolved;
        best = level.toUpperCase();
      }
    }
    return best;
  }
}
