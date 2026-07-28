import 'package:flutter/material.dart';

/// Compact four-function calculator for math sections.
class SimpleCalculatorSheet extends StatefulWidget {
  const SimpleCalculatorSheet({super.key});

  static Future<void> show(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (_) => const Padding(
        padding: EdgeInsets.only(bottom: 12),
        child: SimpleCalculatorSheet(),
      ),
    );
  }

  @override
  State<SimpleCalculatorSheet> createState() => _SimpleCalculatorSheetState();
}

class _SimpleCalculatorSheetState extends State<SimpleCalculatorSheet> {
  String _display = '0';
  double? _acc;
  String? _op;
  bool _fresh = true;

  void _tap(String key) {
    setState(() {
      if (key == 'C') {
        _display = '0';
        _acc = null;
        _op = null;
        _fresh = true;
        return;
      }
      if (key == '±') {
        if (_display.startsWith('-')) {
          _display = _display.substring(1);
        } else if (_display != '0') {
          _display = '-$_display';
        }
        return;
      }
      if ('+-×÷'.contains(key)) {
        _commitOp();
        _op = key;
        _fresh = true;
        return;
      }
      if (key == '=') {
        _commitOp();
        _op = null;
        _fresh = true;
        return;
      }
      if (key == '.') {
        if (_fresh) {
          _display = '0.';
          _fresh = false;
        } else if (!_display.contains('.')) {
          _display = '$_display.';
        }
        return;
      }
      if (_fresh || _display == '0') {
        _display = key;
        _fresh = false;
      } else {
        _display = '$_display$key';
      }
    });
  }

  void _commitOp() {
    final v = double.tryParse(_display) ?? 0;
    if (_acc == null || _op == null) {
      _acc = v;
      return;
    }
    switch (_op) {
      case '+':
        _acc = _acc! + v;
      case '-':
        _acc = _acc! - v;
      case '×':
        _acc = _acc! * v;
      case '÷':
        _acc = v == 0 ? double.nan : _acc! / v;
    }
    if (_acc!.isNaN) {
      _display = 'Hata';
      _acc = null;
      _op = null;
    } else {
      _display = _fmt(_acc!);
    }
  }

  String _fmt(double v) {
    if (v == v.roundToDouble()) return v.toInt().toString();
    return v.toStringAsFixed(6).replaceFirst(RegExp(r'0+$'), '').replaceFirst(RegExp(r'\.$'), '');
  }

  @override
  Widget build(BuildContext context) {
    final keys = [
      ['C', '±', '÷', '×'],
      ['7', '8', '9', '-'],
      ['4', '5', '6', '+'],
      ['1', '2', '3', '='],
      ['0', '.', '', ''],
    ];
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                _display,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
            const SizedBox(height: 12),
            for (final row in keys)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    for (final k in row)
                      Expanded(
                        child: k.isEmpty
                            ? const SizedBox.shrink()
                            : Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 4),
                                child: FilledButton.tonal(
                                  onPressed: () => _tap(k),
                                  child: Text(k),
                                ),
                              ),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
