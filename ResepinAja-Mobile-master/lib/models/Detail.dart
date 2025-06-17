import 'package:resepinajamobile/models/Alat.dart';
import 'package:resepinajamobile/models/Bahan.dart';
import 'package:resepinajamobile/models/Langkah.dart';

class Detail {
  final int id_resep;
  final String judul;
  final String gambar;
  final String deskripsi;
  final int id_user;
  final String username;
  final String bintang;
  final int wkt_masak;
  final int prs_resep;
  final String ktg_masak;
  final List<Alat> alat_resep;
  final List<Bahan> bahan_resep;
  final List<Langkah> langkah_resep;
  Detail(
    this.id_resep, this.judul, this.gambar, this.deskripsi, this.id_user,
    this.username, this.bintang, this.wkt_masak, this.prs_resep, this.ktg_masak, this.alat_resep, this.bahan_resep, this.langkah_resep);
}
