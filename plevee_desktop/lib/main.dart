import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';
import 'core/theme/app_theme.dart';
import 'core/services/auth_service.dart';
import 'core/providers/update_provider.dart';
import 'features/auth/screens/signin_screen.dart';
import 'features/dashboard/screens/dashboard_screen.dart';
import 'features/settings/widgets/update_notification.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize window manager
  await windowManager.ensureInitialized();
  
  runApp(
    const ProviderScope(
      child: PleveeApp(),
    ),
  );
}

class PleveeApp extends ConsumerStatefulWidget {
  const PleveeApp({super.key});

  @override
  ConsumerState<PleveeApp> createState() => _PleveeAppState();
}

class _PleveeAppState extends ConsumerState<PleveeApp> {
  @override
  void initState() {
    super.initState();
    
    // Check for updates on startup (after 3 seconds delay)
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        ref.read(updateNotifierProvider.notifier).checkForUpdates();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authServiceProvider);

    return MaterialApp(
      title: 'Plevee',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: Stack(
        children: [
          authState.isAuthenticated
              ? const DashboardScreen()
              : const SignInScreen(),
          // Update notification overlay
          const UpdateNotificationWidget(),
        ],
      ),
    );
  }
}
