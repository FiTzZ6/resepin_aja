import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:developer';

// + Ubah Form Tambah_____DONEE
// + Tambah Halaman show product + searching_____DONEE
// + Ubah profil_____DONEE
// + Ubah isi Detail
// + Solve Data ga keupdate

class Authservice {
  static Future<bool> register(String username, String password, String phone, String pass_confirm) async {
    final response = await http.post(
      Uri.parse('http://192.168.100.9:8000/api/register'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({
        'username': username,
        'no_hp': phone,
        'password': password,
        'password_confirmation': pass_confirm,
      }),
    );
    if (response.statusCode == 201) {
      return true;
    } else {
      // final json = jsonDecode(response.body);
      // log(json['message']);
      return false;
    }
  }

  static Future<bool> login(String username, String password) async {
    final _storage = FlutterSecureStorage();
    final prefs = await SharedPreferences.getInstance();
    final response = await http.post(
      Uri.parse('http://192.168.100.9:8000/api/login'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['token'];
      final user = data['user'];
      await _storage.write(key: 'auth_token', value: token);
      await prefs.setInt('id_user', user['id_user']);
      await prefs.setString('username', user['username']);
      await prefs.setString('no_hp', user['no_hp']);
      await prefs.setString('role', user['role']);
      await prefs.setString('deskripsi_user', user['deskripsi_user'] ?? '');
      return true;
    } else {
      return false;
    }
  }

  Future<bool> logout() async {
    final token = await FlutterSecureStorage().read(key: 'auth_token');
    final prefs = await SharedPreferences.getInstance();

    final response = await http.post(
      Uri.parse('http://192.168.100.9:8000/api/logout'),
      headers: {'Authorization': 'Bearer $token', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      await FlutterSecureStorage().delete(key: 'auth_token');
      await prefs.remove('id_user');
      await prefs.remove('username');
      await prefs.remove('no_hp');
      await prefs.remove('deskripsi_user');
      await prefs.remove('role');
      log("Aku Mau Logout");
      log(response.body);
      return true;
    } else {
      log("gabisa Logout");
      log(response.body);
      return false;
    }
  }

  Future<bool?> editProfile({String? deskripsi, String? password, String? passwordConfirm}) async {
    final token = AppData().token;
    final response = await http.post(
      Uri.parse('http://192.168.100.9:8000/api/edit-profile'),
      headers: {'Authorization': 'Bearer $token', 'Accept': 'application/json'},
      body: {
        if (deskripsi != null) 'deskripsi_user': deskripsi,
        if (password != null) 'password': password,
        if (passwordConfirm != null) 'password_confirmation': passwordConfirm,
      },
    );
    if (response.statusCode == 200) {
      log("SinanjuSetFREE");
      return true;
    }
    log(response.body);
    log("SinanjuSetting");
    return false;
  }
}
