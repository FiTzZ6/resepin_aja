import 'package:flutter/material.dart';
import 'package:resepinajamobile/services/AuthService.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _usernameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passconfirmController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  void _handleReg(
    String username,
    String phone,
    String password,
    String passconfirm,
    BuildContext context,
  ) async {
    if (_formKey.currentState!.validate()) {
      final status = await Authservice.register(username, password, phone, passconfirm);
      if (status == true) {
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Register failed. Please check Your data.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
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
                Text("SIGN UP", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
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
                        controller: _phoneController,
                        decoration: InputDecoration(
                          labelText: "No HP",
                          prefixIcon: Icon(Icons.phone_outlined),
                          border: UnderlineInputBorder(),
                        ),
                        validator: (value) => value!.isEmpty ? "Please enter Phone Number" : null,
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
                      SizedBox(height: 20),
                      TextFormField(
                        controller: _passconfirmController,
                        decoration: InputDecoration(
                          labelText: "Confirm Password",
                          prefixIcon: Icon(Icons.lock_outline),
                          border: UnderlineInputBorder(),
                        ),
                        obscureText: true,
                        validator: (value) => value!.isEmpty ? "Please enter password again" : null,
                      ),
                      SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text("Apakah Anda Sudah Punya Akun? "),
                          GestureDetector(
                            onTap: () {
                              Navigator.pushNamedAndRemoveUntil(context, "/login", (route) => false);
                            },
                            child: Text("Login", style: TextStyle(color: Colors.purple)),
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
                          _handleReg(
                            _usernameController.text,
                            _phoneController.text,
                            _passwordController.text,
                            _passconfirmController.text,
                            context,
                          );
                        },
                        child: Text("REGISTER", style: TextStyle(color: Colors.white)),
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
