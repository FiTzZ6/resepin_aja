import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Userdata {
  final int id_user;
  final String username;
  final String deskripsi_user;
  Userdata(
    this.id_user,
    this.username,
    this.deskripsi_user,
    );
}