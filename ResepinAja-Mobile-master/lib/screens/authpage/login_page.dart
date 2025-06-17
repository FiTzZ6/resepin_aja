import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/screens/mainpage/base_page.dart';
import 'package:resepinajamobile/services/AuthService.dart';
import 'package:resepinajamobile/screens/authpage/register_page.dart';


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
  }
  
  void _handleLogin(String username, String password, BuildContext context) async {
    if (_formKey.currentState!.validate()) {
      final status = await Authservice.login(username, password);
      if (status == true) {
        await AppData().fetchAll();
        Navigator.pushAndRemoveUntil(context, MaterialPageRoute(builder: (context) => HomeBase()), (route) => false);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Login failed. Please check credentials.')));
      }
    }
  }


  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      body: Center(
        child: SingleChildScrollView( // supaya kalau kecil ga overflow
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(15),
                  child: Image.asset(
                    'assets/LogoResJa.jpg',
                    height: 100, // kasih tinggi supaya lebih rapi
                  ),
                ),
                SizedBox(height: 30),
                Text(
                  "SIGN IN",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 30),
                Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      TextFormField(
                        controller: _usernameController,
                        decoration: InputDecoration(
                          labelText: "Username",
                          prefixIcon: Icon(Icons.person_outline),
                          border: UnderlineInputBorder(),
                        ),
                        validator: (value) => value!.isEmpty ? "Please enter username" : null,
                      ),
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _passwordController,
                        decoration: InputDecoration(
                          labelText: "Password",
                          prefixIcon: Icon(Icons.lock_outline),
                          border: UnderlineInputBorder(),
                        ),
                        obscureText: true,
                        validator: (value) => value!.isEmpty ? "Please enter password" : null,
                      ),
                      SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text("Don't have an account? "),
                          GestureDetector(
                            onTap: () {
                              // Navigator.pushNamed(context, '/register');
                              Navigator.push(
                                context,
                                MaterialPageRoute(builder: (context) => RegisterPage()),
                              );
                            },
                            child: Text(
                              "Register Here",
                              style: TextStyle(color: Colors.purple),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 30),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          minimumSize: Size(double.infinity, 50),
                          backgroundColor: Colors.black,
                        ),
                        onPressed: () {
                          _handleLogin(_usernameController.text, _passwordController.text, context);
                        },
                        child: Text("LOGIN", style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
