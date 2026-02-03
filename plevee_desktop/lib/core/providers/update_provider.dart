import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/update_service.dart';

/// Provider for update service
final updateServiceProvider = Provider((ref) => UpdateService());

/// Provider for update check
final updateCheckProvider = FutureProvider.autoDispose<UpdateInfo?>((ref) async {
  final updateService = ref.watch(updateServiceProvider);
  return await updateService.checkForUpdates();
});

/// State notifier for update progress
class UpdateNotifier extends StateNotifier<UpdateState> {
  final UpdateService _updateService;
  
  UpdateNotifier(this._updateService) : super(const UpdateState.idle());
  
  Future<void> checkForUpdates() async {
    state = const UpdateState.checking();
    
    final updateInfo = await _updateService.checkForUpdates();
    
    if (updateInfo != null) {
      state = UpdateState.available(updateInfo);
    } else {
      state = const UpdateState.upToDate();
    }
  }
  
  Future<void> downloadAndInstall(UpdateInfo updateInfo) async {
    state = const UpdateState.downloading(0.0);
    
    final success = await _updateService.downloadAndInstall(
      updateInfo,
      onProgress: (progress) {
        state = UpdateState.downloading(progress);
      },
    );
    
    if (success) {
      state = const UpdateState.installing();
    } else {
      state = const UpdateState.error('Failed to download update');
    }
  }
}

/// Update state
sealed class UpdateState {
  const UpdateState();
  
  const factory UpdateState.idle() = UpdateIdle;
  const factory UpdateState.checking() = UpdateChecking;
  const factory UpdateState.available(UpdateInfo info) = UpdateAvailable;
  const factory UpdateState.upToDate() = UpdateUpToDate;
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

class UpdateUpToDate extends UpdateState {
  const UpdateUpToDate();
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

/// Provider for update notifier
final updateNotifierProvider = StateNotifierProvider<UpdateNotifier, UpdateState>((ref) {
  final updateService = ref.watch(updateServiceProvider);
  return UpdateNotifier(updateService);
});
