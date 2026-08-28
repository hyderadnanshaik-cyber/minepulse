import 'package:flutter/material.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations) ??
        AppLocalizations(const Locale('en'));
  }

  static const _localizedValues = <String, Map<String, String>>{
    'en': {
      'app_title': 'MINEGUARD',
      'app_subtitle': 'AI-Enabled Mine Subsidence Monitoring',
      'dashboard': 'Dashboard',
      'telemetry': 'Telemetry',
      'gis_map': 'Mine Map',
      'alerts': 'Alerts',
      'nodes': 'Sensors',
      'ai_analytics': 'AI Analytics',
      'gateway': 'Gateway',
      'reports': 'Reports',
      'settings': 'Settings',
      'normal': 'NORMAL',
      'watch': 'WATCH',
      'high': 'HIGH',
      'critical': 'CRITICAL',
      'displacement': 'Draw-Wire Displacement',
      'strata_tilt': 'Strata Tilt Angle',
      'crack_width': 'Crack Fissure Opening',
      'vibration': 'Dynamic Vibration',
      'battery': 'Battery',
      'mesh_hops': 'LoRa Hops',
      'acknowledge': 'Acknowledge Siren',
      'trigger_sih_demo': 'Trigger NODE-03 Anomaly',
      'reset_safe': 'Reset All Safe',
      'security_status': 'Security Center: OPTIMAL',
    },
    'hi': {
      'app_title': 'माइनगार्ड',
      'app_subtitle': 'कोयला खदान धंसाव पूर्व-चेतावनी प्रणाली',
      'dashboard': 'डैशबोर्ड',
      'telemetry': 'टेलीमेट्री',
      'gis_map': 'खदान मानचित्र',
      'alerts': 'अलर्ट्स',
      'nodes': 'सेंसर नोड्स',
      'ai_analytics': 'एआई विश्लेषण',
      'gateway': 'गेटवे',
      'reports': 'रिपोर्ट्स',
      'settings': 'सेटिंग्स',
      'normal': 'सामान्य',
      'watch': 'निगरानी',
      'high': 'उच्च जोखिम',
      'critical': 'अति-गंभीर',
      'displacement': 'सतह विस्थापन (mm)',
      'strata_tilt': 'स्ट्रैटा झुकाव कोण (°)',
      'crack_width': 'दरार की चौड़ाई (mm)',
      'vibration': 'कंपन स्तर (g)',
      'battery': 'बैटरी',
      'mesh_hops': 'लोरा हॉप्स',
      'acknowledge': 'अलर्ट स्वीकार करें',
      'trigger_sih_demo': 'नोड-03 संकट सिमुलेशन',
      'reset_safe': 'सामान्य स्थिति पर रीसेट करें',
      'security_status': 'सुरक्षा स्थिति: सर्वोत्तम',
    },
    'ur': {
      'app_title': 'مائن گارڈ',
      'app_subtitle': 'کوئلہ کی کان کی زمین بیٹھنے کا پیشگی انتباہی نظام',
      'dashboard': 'ڈیش بورڈ',
      'telemetry': 'ٹیلی میٹری',
      'gis_map': 'کان کا نقشہ',
      'alerts': 'انتباہات',
      'nodes': 'سینسر نوڈز',
      'ai_analytics': 'اے آئی تجزیات',
      'gateway': 'گیٹ وے',
      'reports': 'رپورٹس',
      'settings': 'ترتیبات',
      'normal': 'معمول',
      'watch': 'نگرانی',
      'high': 'زیادہ خطرہ',
      'critical': 'انتہائی خطرناک',
      'displacement': 'زمینی سرکاؤ (mm)',
      'strata_tilt': 'جھکاؤ زاویہ (°)',
      'crack_width': 'دراڑ کی چوڑائی (mm)',
      'vibration': 'ارتعاش (g)',
      'battery': 'بیٹری',
      'mesh_hops': 'لورا ہوپس',
      'acknowledge': 'سائرن تسلیم کریں',
      'trigger_sih_demo': 'نوڈ-03 خطرہ ڈیمو',
      'reset_safe': 'سب محفوظ پر ری سیٹ کریں',
      'security_status': 'سیکیورٹی لیول: بہترین',
    },
  };

  String translate(String key) {
    return _localizedValues[locale.languageCode]?[key] ??
        _localizedValues['en']?[key] ??
        key;
  }
}

class AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['en', 'hi', 'ur'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(AppLocalizationsDelegate old) => false;
}
