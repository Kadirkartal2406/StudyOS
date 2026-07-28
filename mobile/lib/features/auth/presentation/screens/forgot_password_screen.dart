import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/repositories/auth_repository.dart';
import '../providers/auth_provider.dart';
import '../providers/auth_state.dart';
import '../widgets/auth_button.dart';
import '../widgets/auth_text_field.dart';

/// Şifre sıfırlama — e-posta + geliştirme modunda reset linki.
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  bool _sent = false;
  ForgotPasswordResult? _result;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final result = await ref
        .read(authProvider.notifier)
        .forgotPassword(_emailCtrl.text.trim());
    if (result != null && mounted) {
      setState(() {
        _sent = true;
        _result = result;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState is AuthLoading;

    ref.listen<AuthState>(authProvider, (_, next) {
      if (next is AuthError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.message),
            backgroundColor: Theme.of(context).colorScheme.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
        ref.read(authProvider.notifier).clearError();
      }
    });

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
          child: _sent ? _successView(context) : _formView(isLoading),
        ),
      ),
    );
  }

  Widget _formView(bool isLoading) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Şifre Sıfırla',
          style: TextStyle(
            color: Colors.white,
            fontSize: 28,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'E-postana sıfırlama bağlantısı göndereceğiz',
          style: TextStyle(color: Colors.white.withAlpha(160)),
        ),
        const SizedBox(height: 40),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(10),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.white.withAlpha(25)),
          ),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                AuthTextField(
                  controller: _emailCtrl,
                  label: 'E-posta',
                  hint: 'ornek@mail.com',
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.email_outlined,
                  enabled: !isLoading,
                  textInputAction: TextInputAction.done,
                  onFieldSubmitted: (_) => _submit(),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'E-posta gerekli';
                    if (!RegExp(r'^[\w-.]+@([\w-]+\.)+[\w-]{2,}$')
                        .hasMatch(v)) {
                      return 'Geçerli bir e-posta girin';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                AuthButton(
                  label: 'Bağlantı Gönder',
                  onPressed: _submit,
                  isLoading: isLoading,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _successView(BuildContext context) {
    final result = _result;
    final hasDevLink =
        result?.resetUrl != null && result!.resetUrl!.isNotEmpty;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.green.withAlpha(30),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.mark_email_read_outlined,
              size: 44,
              color: Colors.green,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'İstek alındı',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            result?.message ??
                'Gelen kutunu kontrol et.\nBağlantı 15 dakika geçerlidir.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white.withAlpha(160), height: 1.6),
          ),
          if (hasDevLink) ...[
            const SizedBox(height: 16),
            Text(
              'SMTP yapılandırılmadığı için geliştirme bağlantısı:',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.amber.withAlpha(200)),
            ),
            const SizedBox(height: 8),
            SelectableText(
              result!.resetUrl!,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
            const SizedBox(height: 12),
            AuthButton(
              label: 'Şifreyi şimdi sıfırla',
              onPressed: () {
                final token = result.devResetToken;
                if (token != null && token.isNotEmpty) {
                  context.push('/reset-password?token=$token');
                }
              },
            ),
            TextButton(
              onPressed: () {
                Clipboard.setData(ClipboardData(text: result.resetUrl!));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Bağlantı kopyalandı')),
                );
              },
              child: const Text('Bağlantıyı kopyala'),
            ),
          ],
          const SizedBox(height: 24),
          AuthButton(
            label: 'Giriş Ekranına Dön',
            onPressed: () => context.go('/login'),
            variant: AuthButtonVariant.secondary,
          ),
        ],
      ),
    );
  }
}
