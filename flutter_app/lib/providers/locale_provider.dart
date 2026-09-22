import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final localeProvider = StateNotifierProvider<LocaleNotifier, Locale>((ref) {
  return LocaleNotifier();
});

class LocaleNotifier extends StateNotifier<Locale> {
  LocaleNotifier() : super(const Locale('en'));

  void setLocale(String languageCode) {
    if (['en', 'hi', 'ur'].contains(languageCode)) {
      state = Locale(languageCode);
    }
  }
}

final themeModeProvider = StateProvider<ThemeMode>((ref) => ThemeMode.dark);
