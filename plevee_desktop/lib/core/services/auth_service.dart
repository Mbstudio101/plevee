import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';

/// Authentication state
class AuthState {
  final bool isAuthenticated;
  final String? accessToken;
  final String? refreshToken;
  final String? userEmail;

  AuthState({
    this.isAuthenticated = false,
    this.accessToken,
    this.refreshToken,
    this.userEmail,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    String? accessToken,
    String? refreshToken,
    String? userEmail,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      userEmail: userEmail ?? this.userEmail,
    );
  }
}

/// Authentication service
class AuthService extends StateNotifier<AuthState> {
  final ApiService _apiService;
  final FlutterSecureStorage _storage;

  AuthService(this._apiService, this._storage) : super(AuthState()) {
    _loadStoredAuth();
  }

  Future<void> _loadStoredAuth() async {
    final accessToken = await _storage.read(key: 'access_token');
    final refreshToken = await _storage.read(key: 'refresh_token');
    final userEmail = await _storage.read(key: 'user_email');

    if (accessToken != null) {
      _apiService.setAccessToken(accessToken);
      state = AuthState(
        isAuthenticated: true,
        accessToken: accessToken,
        refreshToken: refreshToken,
        userEmail: userEmail,
      );
    }
  }

  Future<Map<String, dynamic>> signUp({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      debugPrint('🔵 Attempting sign up for: $email');
      debugPrint('🔵 API URL: ${ApiConstants.baseUrl}${ApiConstants.auth}/signup');
      
      final response = await _apiService.post(
        '${ApiConstants.auth}/signup',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
        },
      );

      debugPrint('✅ Sign up response received: ${response.statusCode}');
      
      final accessToken = response.data['access_token'];
      final refreshToken = response.data['refresh_token'];

      await _storage.write(key: 'access_token', value: accessToken);
      await _storage.write(key: 'refresh_token', value: refreshToken);
      await _storage.write(key: 'user_email', value: email);

      _apiService.setAccessToken(accessToken);

      state = AuthState(
        isAuthenticated: true,
        accessToken: accessToken,
        refreshToken: refreshToken,
        userEmail: email,
      );

      debugPrint('✅ Sign up successful!');
      return {'success': true};
    } catch (e, stackTrace) {
      debugPrint('❌ Sign up error: $e');
      debugPrint('❌ Stack trace: $stackTrace');
      
      // Extract error message from DioException
      String errorMessage = 'Failed to create account. Please try again.';
      if (e.toString().contains('DioException')) {
        if (e.toString().contains('400')) {
          errorMessage = 'Email already registered or invalid data. Please use a different email.';
        } else if (e.toString().contains('500')) {
          errorMessage = 'Server error. Please try again later.';
        } else if (e.toString().contains('Connection')) {
          errorMessage = 'Cannot connect to server. Please check your connection.';
        }
      }
      
      return {'success': false, 'error': errorMessage};
    }
  }

  Future<bool> signIn({
    required String email,
    required String password,
  }) async {
    try {
      debugPrint('🔵 Attempting sign in for: $email');
      
      final response = await _apiService.post(
        '${ApiConstants.auth}/signin',
        data: {
          'email': email,
          'password': password,
        },
      );

      debugPrint('✅ Sign in response received: ${response.statusCode}');
      
      final accessToken = response.data['access_token'];
      final refreshToken = response.data['refresh_token'];

      await _storage.write(key: 'access_token', value: accessToken);
      await _storage.write(key: 'refresh_token', value: refreshToken);
      await _storage.write(key: 'user_email', value: email);

      _apiService.setAccessToken(accessToken);

      state = AuthState(
        isAuthenticated: true,
        accessToken: accessToken,
        refreshToken: refreshToken,
        userEmail: email,
      );

      debugPrint('✅ Sign in successful!');
      return true;
    } catch (e, stackTrace) {
      debugPrint('❌ Sign in error: $e');
      debugPrint('❌ Stack trace: $stackTrace');
      return false;
    }
  }

  Future<void> signOut() async {
    await _storage.deleteAll();
    _apiService.clearAccessToken();
    state = AuthState();
  }
}

// Providers
final secureStorageProvider = Provider<FlutterSecureStorage>(
  (ref) => const FlutterSecureStorage(),
);

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService(ref.watch(secureStorageProvider));
});

final authServiceProvider = StateNotifierProvider<AuthService, AuthState>((ref) {
  return AuthService(
    ref.watch(apiServiceProvider),
    ref.watch(secureStorageProvider),
  );
});
