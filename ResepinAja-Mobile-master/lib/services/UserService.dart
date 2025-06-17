import 'package:http/http.dart' as http;
import 'package:resepinajamobile/models/AppData.dart';
import 'dart:convert';
import 'package:resepinajamobile/models/Rating.dart';
import 'package:resepinajamobile/models/UserData.dart';

class Userservice {
  static Future<List<Rating>?> showResepRating(int id_resep) async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/ratingresep/$id_resep'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Rating(
              json['id_rating'] as int,
              json['id_resep'] as int,
              json['bintang'] as int,
              json['id_user'] as int,
              json['username'] as String,
              json['komentar'] as String,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<Userdata?> showProfile(int id_user) async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/profil/$id_user'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return Userdata(data['data']['id_user'], data['data']['username'], data['data']['deskripsi_user']);
    } else {
      return null;
    }
  }

  static Future<bool?> deleteUserRating(int? id_user, int? id_resep) async {
    final token = AppData().token;
    final response = await http.delete(
      Uri.parse('http://192.168.100.9:8000/api/del-rating'),
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'id_resep': id_resep, 'id_user': id_user}),
    );
    if (response.statusCode == 200) {
      return true;
    } else {
      return false;
    }
  }
}
