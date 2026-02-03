import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/update_service.dart';

// Export UpdateInfo so it can be used by widgets
export '../../../core/services/update_service.dart' show UpdateInfo;

sealed class UpdateState {
  const UpdateState();
  const factory UpdateState.idle() = UpdateIdle;
  const factory UpdateState.checking() = UpdateChecking;
  const factory UpdateState.available(UpdateInfo info) = UpdateAvailable;
  const factory UpdateState.downloading(double progress) = UpdateDownloading;
  const factory UpdateState.installing() = UpdateInstalling;
  const factory UpdateState.error(String message) = UpdateError;
}

class UpdateIdle extends UpdateState {
  const UpdateIdle();
}

class UpdateChecking extends UpdateState {
  const UpdateChecking();
}

class UpdateAvailable extends UpdateState {
  final UpdateInfo info;
  const UpdateAvailable(this.info);
}

class UpdateDownloading extends UpdateState {
  final double progress;
  const UpdateDownloading(this.progress);
}

class UpdateInstalling extends UpdateState {
  const UpdateInstalling();
}

class UpdateError extends UpdateState {
  final String message;
  const UpdateError(this.message);
}

class UpdateNotifier extends StateNotifier<UpdateState> {
  final UpdateService _updateService;

  UpdateNotifier(this._updateService) : super(const UpdateState.idle());

  Future<void> checkForUpdates() async {
    try {
      state = const UpdateState.checking();
      
      final info = await _updateService.checkForUpdates();
      
      if (!mounted) return;

      if (info != null) {
        state = UpdateState.available(info);
      } else {
        state = const UpdateState.idle();
      }
    } catch (e) {
      if (!mounted) return;
      state = UpdateState.error(e.toString());
    }
  }

  Future<void> downloadAndInstall(UpdateInfo info) async {
    try {
      state = const UpdateState.downloading(0.0);
      
      final success = await _updateService.downloadAndInstall(
        info,
        onProgress: (progress) {
          if (mounted) {
            state = UpdateState.downloading(progress);
          }
        },
      );
      
      if (!mounted) return;
      
      if (success) {
        state = const UpdateState.installing();
        // The app will likely restart or exit here due to _installMacOSUpdate
      } else {
        state = const UpdateState.error('Failed to install update');
      }
    } catch (e) {
      if (!mounted) return;
      state = UpdateState.error(e.toString());
    }
  }
  
  void reset() {
    state = const UpdateState.idle();
  }
}

final updateServiceProvider = Provider<UpdateService>((ref) {
  return UpdateService();
});

final updateNotifierProvider = StateNotifierProvider<UpdateNotifier, UpdateState>((ref) {
  return UpdateNotifier(ref.watch(updateServiceProvider));
});
