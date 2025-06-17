import 'package:http/http.dart' as http;
import 'package:resepinajamobile/models/Alat.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/models/Bahan.dart';
import 'package:resepinajamobile/models/Detail.dart';
import 'dart:developer';
import 'dart:convert';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/models/Langkah.dart';

// + Filter Kategori
// + Filter Resep Terbaru dan Terlama
// + Filter Nama Resep dan Nama User

class Recipeservice {
  static Future<List<Item>?> showResepBaru() async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/resepbaru'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Item(
              (json['id_saved'] as int?) ?? 0,
              json['id_resep'] as int,
              json['bintang']?.toDouble() ?? 0.0,
              json['judul'] as String,
              json['gambar'] as String,
              json['wkt_masak'] as int,
              json['prs_resep'] as int,
              json['jumlah_bahan'] as int,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<List<Item>?> showResepPopuler() async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/reseppopuler'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Item(
              (json['id_saved'] as int?) ?? 0,
              json['id_resep'] as int,
              json['bintang']?.toDouble() ?? 0.0,
              json['judul'] as String,
              json['gambar'] as String,
              json['wkt_masak'] as int,
              json['prs_resep'] as int,
              json['jumlah_bahan'] as int,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<List<Item>?> showResepCari(Map<String, dynamic>? params) async {
    final uri = Uri.parse('http://192.168.100.9:8000/api/resepcari').replace(queryParameters: params);
    final response = await http.get(
      uri,
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    log(uri.toString());
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Item(
              (json['id_saved'] as int?) ?? 0,
              json['id_resep'] as int,
              json['bintang']?.toDouble() ?? 0.0,
              json['judul'] as String,
              json['gambar'] as String,
              json['wkt_masak'] as int,
              json['prs_resep'] as int,
              json['jumlah_bahan'] as int,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<List<Item>?> showResepSendiri(int id_user) async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/resepsendiri/$id_user'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Item(
              (json['id_saved'] as int?) ?? 0,
              json['id_resep'] as int,
              json['bintang']?.toDouble() ?? 0.0,
              json['judul'] as String,
              json['gambar'] as String,
              json['wkt_masak'] as int,
              json['prs_resep'] as int,
              json['jumlah_bahan'] as int,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<List<Item>?> showResepTersimpan(int id_user) async {
    final token = AppData().token;
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/tersimpanresep/$id_user'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    );
    if (response.statusCode == 200) {
      log(response.body);
      final data = jsonDecode(response.body);
      final List<dynamic> items = data['data'];
      return items
          .map(
            (json) => Item(
              (json['id_saved'] as int?) ?? 0,
              json['id_resep'] as int,
              json['bintang']?.toDouble() ?? 0.0,
              json['judul'] as String,
              json['gambar'] as String,
              json['wkt_masak'] as int,
              json['prs_resep'] as int,
              json['jumlah_bahan'] as int,
            ),
          )
          .toList();
    } else {
      return null;
    }
  }

  static Future<Detail?> showResepDetail(int id_resep) async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.100.9:8000/api/detailresep/$id_resep'),
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body)['data'];

        final Map<String, dynamic> resep = data['resep'];

        if (resep['bintang'] == null) {
          resep['bintang'] = 0;
        }

        final List<Alat> alatList =
            (data['alat'] as List)
                .map(
                  (json) =>
                      Alat(json['id_alat'] as int, json['id_resep'] as int, json['nama_alat'] as String),
                )
                .toList();

        final List<Bahan> bahanList =
            (data['bahan'] as List)
                .map(
                  (json) => Bahan(
                    json['id_bahan'] as int,
                    json['id_resep'] as int,
                    json['nama_bahan'] as String,
                    json['jml_bahan'] as int,
                    json['stn_bahan'] as String,
                  ),
                )
                .toList();

        final List<Langkah> langkahList =
            (data['langkah'] as List)
                .map(
                  (json) => Langkah(
                    json['id_langkah'] as int,
                    json['id_resep'] as int,
                    json['urutan'] as int,
                    json['cara_langkah'] as String,
                  ),
                )
                .toList();

        return Detail(
          resep['id_resep'] as int,
          resep['judul'] as String,
          resep['gambar'] as String,
          resep['deskripsi'] as String,
          resep['id_user'] as int,
          resep['username'] as String,
          resep['bintang'].toString(),
          resep['wkt_masak'] as int,
          resep['prs_resep'] as int,
          resep['ktg_masak'] as String,
          alatList,
          bahanList,
          langkahList,
        );
      }
    } catch (e) {
      print('Error fetching recipe detail: $e');
    }
    return null;
  }
}
