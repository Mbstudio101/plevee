import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/update_provider.dart';

/// Widget that shows update notification and handles installation
class UpdateNotificationWidget extends ConsumerWidget {
  const UpdateNotificationWidget({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final updateState = ref.watch(updateNotifierProvider);
    
    return switch (updateState) {
      UpdateAvailable(:final info) => _buildUpdateAvailableDialog(context, ref, info),
      UpdateDownloading(:final progress) => _buildDownloadingDialog(context, progress),
      UpdateInstalling() => _buildInstallingDialog(context),
      UpdateError(:final message) => _buildErrorDialog(context, message),
      _ => const SizedBox.shrink(),
    };
  }
  
  Widget _buildUpdateAvailableDialog(BuildContext context, WidgetRef ref, UpdateInfo info) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.system_update, color: Colors.blue),
              SizedBox(width: 12),
              Text('Update Available'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Version ${info.version} is now available!',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              Text(
                'Release Notes:',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  info.releaseNotes,
                  style: const TextStyle(fontSize: 13),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                ref.read(updateNotifierProvider.notifier).reset();
              },
              child: const Text('Later'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                ref.read(updateNotifierProvider.notifier).downloadAndInstall(info);
              },
              child: const Text('Update Now'),
            ),
          ],
        ),
      );
    });
    
    return const SizedBox.shrink();
  }
  
  Widget _buildDownloadingDialog(BuildContext context, double progress) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Downloading Update'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              LinearProgressIndicator(value: progress),
              const SizedBox(height: 16),
              Text('${(progress * 100).toStringAsFixed(0)}%'),
            ],
          ),
        ),
      );
    });
    
    return const SizedBox.shrink();
  }
  
  Widget _buildInstallingDialog(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const AlertDialog(
          title: Text('Installing Update'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('App will restart automatically...'),
            ],
          ),
        ),
      );
    });
    
    return const SizedBox.shrink();
  }
  
  Widget _buildErrorDialog(BuildContext context, String message) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.error, color: Colors.red),
              SizedBox(width: 12),
              Text('Update Failed'),
            ],
          ),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    });
    
    return const SizedBox.shrink();
  }
}

/// Button to manually check for updates
class CheckUpdateButton extends ConsumerWidget {
  const CheckUpdateButton({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final updateState = ref.watch(updateNotifierProvider);
    
    return IconButton(
      icon: const Icon(Icons.system_update_alt),
      tooltip: 'Check for Updates',
      onPressed: updateState is UpdateChecking
          ? null
          : () => ref.read(updateNotifierProvider.notifier).checkForUpdates(),
    );
  }
}
