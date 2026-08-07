import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../shared/widgets/app_bottom_nav_bar.dart';

/// Tüm ikincil özelliklerin (Yolculuk, Denemeler, Ayarlar vs.) toplandığı Menü ekranı.
class MenuScreen extends StatelessWidget {
  const MenuScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Menü'),
      ),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.map_outlined),
            title: const Text('Yolculuğum'),
            subtitle: const Text('Genel ilerleme ve istatistikler'),
            onTap: () => context.push('/journey'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.assignment_outlined),
            title: const Text('Günün denemesi'),
            onTap: () => context.push('/assessment/daily'),
          ),
          ListTile(
            leading: const Icon(Icons.assessment_outlined),
            title: const Text('Seviye testi'),
            onTap: () => context.push('/assessment'),
          ),
          ListTile(
            leading: const Icon(Icons.grading_rounded),
            title: const Text('Deneme sonuçları'),
            onTap: () => context.push('/exams'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.auto_awesome),
            title: const Text('Plan önerisi'),
            onTap: () => context.push('/planner'),
          ),
          ListTile(
            leading: const Icon(Icons.chat_bubble_outline),
            title: const Text('AI sohbet'),
            onTap: () => context.push('/ai-chat'),
          ),
          ListTile(
            leading: const Icon(Icons.map_rounded),
            title: const Text('Haritalar'),
            onTap: () => context.push('/maps'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: const Text('Ayarlar'),
            onTap: () => context.push('/settings'),
          ),
        ],
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 4),
    );
  }
}
