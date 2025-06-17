import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppData {
  static final AppData _instance = AppData._internal();
  factory AppData() => _instance;
  AppData._internal();
  int? id_user;
  String? token;
  String? username;
  String? deskripsi_user;
  String? no_hp;
  String? role;

  Future<void> fetchAll() async {
    final _storage = FlutterSecureStorage();
    final getToken = await _storage.read(key: 'auth_token');
    final prefs = await SharedPreferences.getInstance();
    if(getToken != null){
      id_user = prefs.getInt('id_user');
      token = getToken;
      username = prefs.getString('username');
      deskripsi_user = prefs.getString('deskripsi_user');
      no_hp = prefs.getString('no_hp');
      role = prefs.getString('role');
    }
  }
}
