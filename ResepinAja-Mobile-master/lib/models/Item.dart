class Item {
  int? id_saved = 0;
  final int id_resep;
  double? bintang = 0;
  final String judul;
  final String gambar;
  final int wkt_masak;
  final int prs_masak;
  final int jumlah_bahan;
  Item(
    this.id_saved,
    this.id_resep,
    this.bintang,
    this.judul,
    this.gambar,
    this.wkt_masak,
    this.prs_masak,
    this.jumlah_bahan,
  );
}
