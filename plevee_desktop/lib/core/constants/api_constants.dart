/// API configuration constants
class ApiConstants {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api/v1';
  
  // Endpoints
  static const String auth = '$apiVersion/auth';
  static const String portfolios = '$apiVersion/portfolios';
  static const String strategies = '$apiVersion/strategies';
  static const String backtesting = '$apiVersion/backtesting';
  static const String trading = '$apiVersion/trading';
  static const String marketData = '$apiVersion/market-data';
  
  // WebSocket
  static const String wsUrl = 'ws://localhost:8000/ws';
}
