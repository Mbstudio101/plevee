import 'dart:io';
import 'package:dio/dio.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/foundation.dart';

/// Service for checking and installing app updates
class UpdateService {
  static const String updateCheckUrl = 'https://api.github.com/repos/Mbstudio101/plevee/releases/latest';
  static const String currentVersion = '1.0.0';
  
  final Dio _dio = Dio();
  
  /// Check if an update is available
  Future<UpdateInfo?> checkForUpdates() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;
      
      // Fetch latest release info from GitHub
      final response = await _dio.get(updateCheckUrl);
      
      if (response.statusCode == 200) {
        final data = response.data;
        final latestVersion = (data['tag_name'] as String).replaceAll('v', '');
        final downloadUrl = _getDownloadUrl(data['assets']);
        
        if (downloadUrl != null && _isNewerVersion(currentVersion, latestVersion)) {
          return UpdateInfo(
            version: latestVersion,
            downloadUrl: downloadUrl,
            releaseNotes: data['body'] ?? 'New version available',
            publishedAt: DateTime.parse(data['published_at']),
          );
        }
      }
      
      return null; // No update available
    } catch (e) {
      debugPrint('Error checking for updates: $e');
      return null;
    }
  }
  
  /// Download and install update
  Future<bool> downloadAndInstall(UpdateInfo updateInfo, {
    Function(double)? onProgress,
  }) async {
    try {
      // Get temporary directory
      final tempDir = await getTemporaryDirectory();
      final savePath = '${tempDir.path}/Plevee-${updateInfo.version}.dmg';
      
      // Download update
      await _dio.download(
        updateInfo.downloadUrl,
        savePath,
        onReceiveProgress: (received, total) {
          if (total != -1 && onProgress != null) {
            onProgress(received / total);
          }
        },
      );
      
      // Install update (macOS)
      if (Platform.isMacOS) {
        await _installMacOSUpdate(savePath);
        return true;
      }
      
      return false;
    } catch (e) {
      debugPrint('Error downloading/installing update: $e');
      return false;
    }
  }
  
  /// Install update on macOS
  Future<void> _installMacOSUpdate(String dmgPath) async {
    // Mount DMG
    await Process.run('hdiutil', ['attach', dmgPath]);
    
    // Copy app to Applications
    final volumeName = 'Plevee';
    await Process.run('cp', [
      '-R',
      '/Volumes/$volumeName/Plevee.app',
      '/Applications/Plevee.app'
    ]);
    
    // Unmount DMG
    await Process.run('hdiutil', ['detach', '/Volumes/$volumeName']);
    
    // Restart app
    await Process.run('open', ['/Applications/Plevee.app']);
    
    // Exit current instance
    exit(0);
  }
  
  /// Get download URL for current platform
  String? _getDownloadUrl(List<dynamic> assets) {
    for (var asset in assets) {
      final name = asset['name'] as String;
      if (Platform.isMacOS && name.endsWith('.dmg')) {
        return asset['browser_download_url'];
      }
    }
    return null;
  }
  
  /// Compare version strings
  bool _isNewerVersion(String current, String latest) {
    final currentParts = current.split('.').map(int.parse).toList();
    final latestParts = latest.split('.').map(int.parse).toList();
    
    for (int i = 0; i < 3; i++) {
      if (latestParts[i] > currentParts[i]) return true;
      if (latestParts[i] < currentParts[i]) return false;
    }
    
    return false;
  }
}

/// Update information
class UpdateInfo {
  final String version;
  final String downloadUrl;
  final String releaseNotes;
  final DateTime publishedAt;
  
  UpdateInfo({
    required this.version,
    required this.downloadUrl,
    required this.releaseNotes,
    required this.publishedAt,
  });
}
