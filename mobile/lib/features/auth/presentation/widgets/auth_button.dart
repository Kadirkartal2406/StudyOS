import 'package:flutter/material.dart';

/// Auth ekranlarında kullanılan birincil buton.
class AuthButton extends StatelessWidget {
  const AuthButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.isLoading = false,
    this.variant = AuthButtonVariant.primary,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AuthButtonVariant variant;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return SizedBox(
      width: double.infinity,
      height: 56,
      child: switch (variant) {
        AuthButtonVariant.primary => FilledButton(
            onPressed: isLoading ? null : onPressed,
            style: FilledButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              backgroundColor: colors.primary,
              foregroundColor: colors.onPrimary,
              elevation: 0,
            ),
            child: _child(colors.onPrimary),
          ),
        AuthButtonVariant.secondary => OutlinedButton(
            onPressed: isLoading ? null : onPressed,
            style: OutlinedButton.styleFrom(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              side: BorderSide(color: Colors.white.withAlpha(80)),
              foregroundColor: Colors.white,
            ),
            child: _child(Colors.white),
          ),
      },
    );
  }

  Widget _child(Color color) {
    if (isLoading) {
      return SizedBox(
        height: 22,
        width: 22,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          color: color,
        ),
      );
    }
    return Text(
      label,
      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
    );
  }
}

enum AuthButtonVariant { primary, secondary }
