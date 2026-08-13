/// Plain-text math for quiz UI. Strips `$` / LaTeX wrappers so stems
/// like `$x^2$` render as `x^2` instead of showing dollar signs.
String mathDisplayText(String? raw) {
  if (raw == null || raw.isEmpty) return '';
  var text = raw;
  text = text.replaceAll('\$\$', '').replaceAll('\$', '');
  text = text.replaceAll(r'\(', '').replaceAll(r'\)', '');
  text = text.replaceAll(r'\[', '').replaceAll(r'\]', '');

  const replacements = <String, String>{
    r'\cdot': '·',
    r'\times': '×',
    r'\div': '÷',
    r'\pm': '±',
    r'\mp': '∓',
    r'\geq': '≥',
    r'\ge': '≥',
    r'\leq': '≤',
    r'\le': '≤',
    r'\neq': '≠',
    r'\approx': '≈',
    r'\infty': '∞',
    r'\theta': 'θ',
    r'\alpha': 'α',
    r'\beta': 'β',
    r'\gamma': 'γ',
    r'\delta': 'δ',
    r'\lambda': 'λ',
    r'\sigma': 'σ',
    r'\omega': 'ω',
    r'\pi': 'π',
    r'\mu': 'μ',
    r'\int': '∫',
    r'\sum': '∑',
    r'\prod': '∏',
    r'\partial': '∂',
    r'\mathbb{Q}': 'ℚ',
    r'\mathbb{R}': 'ℝ',
    r'\mathbb{N}': 'ℕ',
    r'\mathbb{Z}': 'ℤ',
    r'\notin': '∉',
    r'\subseteq': '⊆',
    r'\subset': '⊂',
    r'\cup': '∪',
    r'\cap': '∩',
    r'\rightarrow': '→',
    r'\Rightarrow': '⇒',
    r'\to': '→',
    r'\in': '∈',
    r'\ldots': '…',
    r'\dots': '…',
    r'\degree': '°',
    r'^\circ': '°',
    r'\,': ' ',
    r'\;': ' ',
    r'\:': ' ',
    r'\!': '',
  };
  final keys = replacements.keys.toList()
    ..sort((a, b) => b.length.compareTo(a.length));
  for (final src in keys) {
    text = text.replaceAll(src, replacements[src]!);
  }

  text = text.replaceAllMapped(
    RegExp(r'\\frac\{([^{}]+)\}\{([^{}]+)\}'),
    (m) => '(${m[1]})/(${m[2]})',
  );
  text = text.replaceAllMapped(
    RegExp(r'\\sqrt\[([^\]]+)\]\{([^{}]+)\}'),
    (m) => '${m[1]}√(${m[2]})',
  );
  text = text.replaceAllMapped(
    RegExp(r'\\sqrt\{([^{}]+)\}'),
    (m) => '√(${m[1]})',
  );
  text = text.replaceAll(RegExp(r'\\left\s*'), '');
  text = text.replaceAll(RegExp(r'\\right\s*'), '');
  text = text.replaceAllMapped(
    RegExp(r'\\text\{([^{}]+)\}'),
    (m) => m[1] ?? '',
  );
  text = text.replaceAllMapped(
    RegExp(r'\\mathrm\{([^{}]+)\}'),
    (m) => m[1] ?? '',
  );
  text = text.replaceAllMapped(
    RegExp(r'\^\{([^{}]+)\}'),
    (m) => '^${m[1]}',
  );
  text = text.replaceAllMapped(
    RegExp(r'_\{([^{}]+)\}'),
    (m) => '_${m[1]}',
  );
  text = text.replaceAllMapped(
    RegExp(r'\\([a-zA-Z]+)'),
    (m) => m[1] ?? '',
  );
  text = text.replaceAll('{', '').replaceAll('}', '');
  text = text.replaceAll(RegExp(r'[ \t]+'), ' ').trim();
  return text;
}
