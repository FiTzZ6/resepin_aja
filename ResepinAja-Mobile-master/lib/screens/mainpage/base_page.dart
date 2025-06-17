import 'package:flutter/material.dart';
import 'package:resepinajamobile/screens/mainpage/add_page.dart';
import 'package:resepinajamobile/screens/mainpage/home_page.dart';
import 'package:resepinajamobile/screens/mainpage/resep_page.dart';
import 'package:resepinajamobile/screens/mainpage/setting_page.dart';

class HomeBase extends StatefulWidget {
  const HomeBase({super.key});

  @override
  State<HomeBase> createState() => _HomeBaseState();
}

class _HomeBaseState extends State<HomeBase> {
  int currentPageIndex = 0;
  @override
  Widget build(BuildContext context) {
    final _screens = [
      const HomePage(),
      const RecipePage(),
      AddRecipePage(
        onRecipeAdded: () {
          if (mounted) setState(() => currentPageIndex = 0);
        },
      ),
      const SettingPage(),
    ];
    return Scaffold(
      body:IndexedStack(
        index: currentPageIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        onDestinationSelected: (int index) {
          setState(() {
            currentPageIndex = index;
          });
        },
        indicatorColor: Colors.amber,
        selectedIndex: currentPageIndex,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        backgroundColor: Colors.grey[200],
        destinations: const <Widget>[
          NavigationDestination(icon: Icon(Icons.home_filled), label: 'Beranda'),
          NavigationDestination(icon: Icon(Icons.fastfood_rounded), label: 'Resep'),
          // NavigationDestination(icon: Icon(Icons.bookmark), label: 'Tersimpan'),
          NavigationDestination(icon: Icon(Icons.add_box_rounded), label: 'Tambah'),
          NavigationDestination(icon: Icon(Icons.settings), label: 'Pengaturan'),
        ],
      ),
    );
  }
}
