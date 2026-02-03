import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/api_constants.dart';

/// HTTP client service for API calls
class ApiService {
  late final Dio _dio;
  final FlutterSecureStorage _storage;
  String? _accessToken;
  
  // For token refresh
  bool _isRefreshing = false;
  Completer<bool>? _refreshCompleter;

  ApiService(this._storage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );

    // Add interceptor for auth token
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (_accessToken != null) {
            options.headers['Authorization'] = 'Bearer $_accessToken';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          // Handle 401 unauthorized
          if (error.response?.statusCode == 401) {
            // If the failed request was a refresh attempt, don't loop
            if (error.requestOptions.path.contains('/auth/refresh')) {
              return handler.next(error);
            }
            
            if (_isRefreshing) {
              // Wait for the current refresh to complete
              final success = await _refreshCompleter?.future ?? false;
              
              if (success) {
                // Retry request with new token
                final opts = error.requestOptions;
                opts.headers['Authorization'] = 'Bearer $_accessToken';
                final cloneReq = await _dio.request(
                  opts.path,
                  options: Options(
                    method: opts.method,
                    headers: opts.headers,
                    contentType: opts.contentType,
                    responseType: opts.responseType,
                    followRedirects: opts.followRedirects,
                    validateStatus: opts.validateStatus,
                    receiveTimeout: opts.receiveTimeout,
                    sendTimeout: opts.sendTimeout,
                    extra: opts.extra,
                  ),
                  data: opts.data,
                  queryParameters: opts.queryParameters,
                );
                return handler.resolve(cloneReq);
              } else {
                return handler.next(error);
              }
            }
            
            // Start refreshing
            _isRefreshing = true;
            _refreshCompleter = Completer<bool>();
            
            try {
              final refreshToken = await _storage.read(key: 'refresh_token');
              if (refreshToken == null) {
                _isRefreshing = false;
                _refreshCompleter?.complete(false);
                return handler.next(error);
              }
              
              debugPrint('🔄 Refreshing token...');
              
              // Call refresh endpoint using a new Dio instance to avoid interceptors
              final refreshDio = Dio(BaseOptions(
                baseUrl: ApiConstants.baseUrl,
                headers: {'Content-Type': 'application/json'},
              ));
              
              final response = await refreshDio.post(
                '${ApiConstants.auth}/refresh',
                data: {'refresh_token': refreshToken},
              );
              
              if (response.statusCode == 200) {
                final newAccessToken = response.data['access_token'];
                final newRefreshToken = response.data['refresh_token'];
                
                debugPrint('✅ Token refreshed successfully');
                
                // Update local state
                _accessToken = newAccessToken;
                await _storage.write(key: 'access_token', value: newAccessToken);
                await _storage.write(key: 'refresh_token', value: newRefreshToken);
                
                _isRefreshing = false;
                _refreshCompleter?.complete(true);
                
                // Retry original request
                final opts = error.requestOptions;
                opts.headers['Authorization'] = 'Bearer $_accessToken';
                final cloneReq = await _dio.request(
                  opts.path,
                  options: Options(
                    method: opts.method,
                    headers: opts.headers,
                    contentType: opts.contentType,
                    responseType: opts.responseType,
                    followRedirects: opts.followRedirects,
                    validateStatus: opts.validateStatus,
                    receiveTimeout: opts.receiveTimeout,
                    sendTimeout: opts.sendTimeout,
                    extra: opts.extra,
                  ),
                  data: opts.data,
                  queryParameters: opts.queryParameters,
                );
                return handler.resolve(cloneReq);
              } else {
                 debugPrint('❌ Token refresh failed: ${response.statusCode}');
                 _isRefreshing = false;
                 _refreshCompleter?.complete(false);
                 return handler.next(error);
              }
            } catch (e) {
              debugPrint('❌ Token refresh error: $e');
              _isRefreshing = false;
              _refreshCompleter?.complete(false);
              return handler.next(error);
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  void setAccessToken(String token) {
    _accessToken = token;
  }

  void clearAccessToken() {
    _accessToken = null;
  }

  // GET request
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    return await _dio.get(path, queryParameters: queryParameters);
  }

  // POST request
  Future<Response> post(String path, {dynamic data}) async {
    return await _dio.post(path, data: data);
  }

  // PATCH request
  Future<Response> patch(String path, {dynamic data}) async {
    return await _dio.patch(path, data: data);
  }

  // DELETE request
  Future<Response> delete(String path) async {
    return await _dio.delete(path);
  }
}
