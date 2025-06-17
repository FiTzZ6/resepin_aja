import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/screens/mainpage/save_page.dart';
import 'package:resepinajamobile/screens/mainpage/user_page.dart';
import 'package:resepinajamobile/services/AuthService.dart';

class SettingPage extends StatefulWidget {
  const SettingPage({super.key});

  @override
  State<SettingPage> createState() => _SettingPageState();
}

class _SettingPageState extends State<SettingPage> {
  int id_user = 0;
  String username = '';
  String no_hp = '';
  String deskripsi = '';
  bool isLoading = true;
  bool isEditing = false;

  final _formKey = GlobalKey<FormState>();
  final _deskripsiController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordConfirmController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      id_user = AppData().id_user ?? 0;
      username = AppData().username ?? 'Guest';
      no_hp = AppData().no_hp ?? '';
      deskripsi = AppData().deskripsi_user ?? '';
      _deskripsiController.text = deskripsi;
      isLoading = false;
    });
  }

  void _handleLogout(BuildContext context) async {
    final status = await Authservice().logout();
    if (status == true) {
      Navigator.pushNamedAndRemoveUntil(context, "/login", (route) => false);
    }
  }

  Future<void> _saveProfile() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        isLoading = true;
      });
      final status = await Authservice().editProfile(
        deskripsi: _deskripsiController.text,
        password: _passwordController.text,
        passwordConfirm: _passwordConfirmController.text,
      );
      setState(() {
        isLoading = false;
      });

      if (status == true) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Profile updated successfully')));
        setState(() {
          deskripsi = _deskripsiController.text;
          isEditing = false;
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to update profile')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: Text("Pengaturan", style: TextStyle(fontWeight: FontWeight.w600)),
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 0),
        child: Column(
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                InkWell(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => ProfilePage(id_user: AppData().id_user)),
                    );
                  },
                  child: CircleAvatar(
                    radius: 60,
                    backgroundImage: AssetImage('assets/profile_placeholder.webp'),
                  ),
                ),
                SizedBox(height: 12),
                Text(username, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              ],
            ),
            SizedBox(height: 24),
            // Form atau ExpansionTile
            AnimatedCrossFade(
              firstChild: _buildExpansionTile(),
              secondChild: _buildEditForm(),
              crossFadeState: isEditing ? CrossFadeState.showSecond : CrossFadeState.showFirst,
              duration: Duration(milliseconds: 300),
            ),
            SizedBox(height: 24),
            // Button Tambahan
            SizedBox(
              width: double.infinity,
              child: TextButton(
                style: TextButton.styleFrom(backgroundColor: Colors.amber),
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => SavedPage()));
                },
                child: Text(
                  "Lihat Resep tersimpanku ",
                  style: TextStyle(fontWeight: FontWeight.w500, fontSize: 18, color: Colors.black),
                ),
              ),
            ),
            SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: TextButton(
                style: TextButton.styleFrom(backgroundColor: Colors.redAccent),
                onPressed: () {
                  showDialog(
                    context: context,
                    builder:
                        (context) => AlertDialog(
                          title: Text("Logout Resepin Aja"),
                          content: Text("Yakin ingin Logout?"),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(context), child: Text("Batal")),
                            TextButton(
                              onPressed: () {
                                _handleLogout(context);
                              },
                              child: Text("Yakin", style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                  );
                },
                child: Text(
                  "Logout",
                  style: TextStyle(fontWeight: FontWeight.w500, fontSize: 18, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ExpansionTile awal
  Widget _buildExpansionTile() {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: ExpansionTile(
        title: Text("Edit Profil"),
        children: [
          ListTile(
            title: Text("Ubah Deskripsi & Password"),
            onTap: () {
              setState(() {
                isEditing = true;
              });
            },
          ),
        ],
      ),
    );
  }

  // Form Edit Profile
  Widget _buildEditForm() {
    return Form(
      key: _formKey,
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 2,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Edit Profil", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              SizedBox(height: 16),
              TextFormField(
                controller: _deskripsiController,
                decoration: InputDecoration(labelText: "Deskripsi"),
                maxLines: 3,
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(labelText: "Password Baru"),
                obscureText: true,
                validator: (value) {
                  if (value != null && value.isNotEmpty && value.length < 6) {
                    return "Password minimal 6 karakter";
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _passwordConfirmController,
                decoration: InputDecoration(labelText: "Konfirmasi Password"),
                obscureText: true,
                validator: (value) {
                  if (value != _passwordController.text) {
                    return "Konfirmasi password tidak cocok";
                  }
                  return null;
                },
              ),
              SizedBox(height: 24),
              Row(
                children: [
                  Expanded(child: ElevatedButton(onPressed: _saveProfile, child: Text("Simpan"))),
                  SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        setState(() {
                          isEditing = false;
                          _passwordController.clear();
                          _passwordConfirmController.clear();
                        });
                      },
                      child: Text("Batal"),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
