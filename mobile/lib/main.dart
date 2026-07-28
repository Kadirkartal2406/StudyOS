import 'dart:async';
import 'dart:developer' as developer;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

import 'app.dart';
import 'core/constants/app_config.dart';

/// RC2 M22.3 — Global error handler + Sentry (env-aware).
/// ensureInitialized + runApp aynı zone'da olmalı.
Future<void> main() async {
  await runZonedGuarded(() async {
    WidgetsFlutterBinding.ensureInitialized();
    await initializeDateFormatting('tr_TR');

    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      developer.log(
        details.exceptionAsString(),
        name: 'FlutterError',
        stackTrace: details.stack,
        error: details.exception,
      );
      Sentry.captureException(
        details.exception,
        stackTrace: details.stack,
      );
    };

    PlatformDispatcher.instance.onError = (error, stack) {
      developer.log(
        error.toString(),
        name: 'PlatformError',
        stackTrace: stack,
        error: error,
      );
      Sentry.captureException(error, stackTrace: stack);
      return true;
    };

    final dsn = AppConfig.sentryDsn.trim();
    final env = AppConfig.appEnv;

    if (dsn.isEmpty) {
      developer.log('Sentry disabled (SENTRY_DSN empty)', name: 'Sentry');
      runApp(const ProviderScope(child: StudyOSApp()));
      return;
    }

    await SentryFlutter.init(
      (options) {
        options.dsn = dsn;
        options.environment = env;
        options.release = 'studyos-mobile@${AppConfig.appVersion}';
        options.tracesSampleRate =
            (env == 'production' || env == 'prod' || env == 'beta')
                ? 0.1
                : 0.0;
        options.sendDefaultPii = false;
      },
      appRunner: () => runApp(const ProviderScope(child: StudyOSApp())),
    );
  }, (error, stack) {
    developer.log(
      error.toString(),
      name: 'ZoneError',
      stackTrace: stack,
      error: error,
    );
    Sentry.captureException(error, stackTrace: stack);
  });
}
