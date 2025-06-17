import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/screens/authpage/login_page.dart';
import 'package:resepinajamobile/screens/authpage/register_page.dart';
import 'package:resepinajamobile/screens/authpage/splash_screen.dart';
import 'package:resepinajamobile/screens/mainpage/base_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppData().fetchAll();
  runApp(
      MainApp(),
  );
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(fontFamily: 'Poppins'),
      debugShowCheckedModeBanner: false,
      initialRoute: '/splash',
      routes: {
        // '/': (context) => HomeBase(),
        // '/register': (context) => RegisterPage(),
        '/splash': (context) => SplashScreen(),
        '/login': (context) => LoginPage(),
        // '/profile' : (context) => ProfilePage(),
      },
      // home: const LoginPage(),
    );
  }
}
