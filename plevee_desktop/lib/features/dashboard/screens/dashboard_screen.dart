import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/typography.dart';
import '../../../core/services/auth_service.dart';
import '../../../shared/widgets/glass_card.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authServiceProvider);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.deepNavy,
              AppColors.darkNavy,
              AppColors.midNavy,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Top bar
              Padding(
                padding: const EdgeInsets.all(24),
                child: Row(
                  children: [
                    // Logo
                    const Icon(
                      Icons.trending_up,
                      size: 32,
                      color: AppColors.electricBlue,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'PLEVEE',
                      style: AppTypography.h2.copyWith(
                        color: AppColors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    // User info
                    Text(
                      authState.userEmail ?? 'User',
                      style: AppTypography.body1.copyWith(
                        color: AppColors.gray,
                      ),
                    ),
                    const SizedBox(width: 16),
                    IconButton(
                      onPressed: () async {
                        await ref.read(authServiceProvider.notifier).signOut();
                      },
                      icon: const Icon(
                        Icons.logout,
                        color: AppColors.gray,
                      ),
                      tooltip: 'Sign Out',
                    ),
                  ],
                ),
              ),

              // Main content
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Welcome message
                      Text(
                        'Welcome to Plevee',
                        style: AppTypography.h1.copyWith(
                          color: AppColors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Your multi-asset automated trading platform',
                        style: AppTypography.body1.copyWith(
                          color: AppColors.gray,
                        ),
                      ),
                      const SizedBox(height: 32),

                      // Quick stats
                      Expanded(
                        child: GridView.count(
                          crossAxisCount: 2,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                          childAspectRatio: 1.5,
                          children: [
                            _buildStatCard(
                              'Total Portfolio',
                              '\$0.00',
                              Icons.account_balance_wallet,
                              AppColors.electricBlue,
                            ),
                            _buildStatCard(
                              'Active Strategies',
                              '0',
                              Icons.auto_graph,
                              AppColors.profitGreen,
                            ),
                            _buildStatCard(
                              'Today\'s P&L',
                              '\$0.00',
                              Icons.trending_up,
                              AppColors.profitGreen,
                            ),
                            _buildStatCard(
                              'Total Trades',
                              '0',
                              Icons.swap_horiz,
                              AppColors.gray,
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 24),

                      // Coming soon message
                      GlassCard(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          children: [
                            const Icon(
                              Icons.construction,
                              size: 48,
                              color: AppColors.electricBlue,
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'Dashboard Features Coming Soon',
                              style: AppTypography.h3.copyWith(
                                color: AppColors.white,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Portfolio management, strategy builder, and live trading features are under development.',
                              style: AppTypography.body2.copyWith(
                                color: AppColors.gray,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const Spacer(),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: AppTypography.h2.copyWith(
                  color: AppColors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: AppTypography.body2.copyWith(
                  color: AppColors.gray,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
