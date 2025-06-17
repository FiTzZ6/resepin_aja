import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/screens/mainpage/base_page.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkExistingAuth();
  }

  Future<void> _checkExistingAuth() async {
    final token = AppData().token;
    final userId = AppData().id_user;
    await Future.delayed(Duration(seconds: 3));
    if (token != null && userId != null) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => HomeBase()));
    } else {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            ClipRRect(
                  borderRadius: BorderRadius.circular(15),
                  child: Image.asset('assets/LogoResJa.jpg', height: 200, width: 200),
                ),
            SizedBox(height: 20),
            CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
