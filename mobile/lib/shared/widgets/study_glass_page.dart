import 'package:flutter/material.dart';

import 'editorial_page.dart';
import 'study_liquid_glass.dart';

/// Shared liquid-glass page chrome — atmosphere + transparent app bar.
class StudyGlassPage extends StatelessWidget {
  const StudyGlassPage({
    super.key,
    required this.body,
    this.title,
    this.actions,
    this.leading,
    this.bottomNavigationBar,
    this.floatingActionButton,
    this.centerTitle = false,
    this.padding,
    this.atmosphere = true,
  });

  final Widget body;
  final Widget? title;
  final List<Widget>? actions;
  final Widget? leading;
  final Widget? bottomNavigationBar;
  final Widget? floatingActionButton;
  final bool centerTitle;
  final EdgeInsetsGeometry? padding;
  final bool atmosphere;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    final pageBody = Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: EditorialPage.maxContentWidth(width),
        ),
        child: padding == null
            ? body
            : Padding(
                padding: padding!,
                child: body,
              ),
      ),
    );

    return Scaffold(
      backgroundColor: Colors.transparent,
      extendBodyBehindAppBar: false,
      appBar: title == null && actions == null && leading == null
          ? null
          : AppBar(
              backgroundColor: Colors.transparent,
              elevation: 0,
              scrolledUnderElevation: 0,
              centerTitle: centerTitle,
              title: title,
              leading: leading,
              actions: actions,
            ),
      floatingActionButton: floatingActionButton,
      bottomNavigationBar: bottomNavigationBar,
      body: atmosphere
          ? StudyGlassAtmosphere(child: pageBody)
          : pageBody,
    );
  }
}
