import 'dart:convert';
import 'dart:developer';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/models/Detail.dart';
import 'package:resepinajamobile/models/Rating.dart';
import 'package:resepinajamobile/screens/component/buttons.dart';
import 'package:resepinajamobile/screens/mainpage/rating_page.dart';
import 'package:resepinajamobile/screens/mainpage/user_page.dart';
import 'package:resepinajamobile/services/RecipeService.dart';
import 'package:resepinajamobile/services/UserService.dart';

class DetailPage extends StatefulWidget {
  const DetailPage({super.key, required this.id_resep});
  final id_resep;

  @override
  State<DetailPage> createState() => _DetailPageState();
}

class _DetailPageState extends State<DetailPage> {
  int? selectedRating;
  bool showFeedbackField = false;
  Detail? data_detail;
  final TextEditingController _reviewController = TextEditingController();
  bool _isSubmitting = false;
  bool isLoading = true;
  Rating? _currentRating;
  int? userId;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() async {
    final data = await Recipeservice.showResepDetail(widget.id_resep);
    if (data != null) {
      setState(() {
        userId = AppData().id_user;
        data_detail = data;
        isLoading = false;
        _getRating();
      });
    }
  }

  Future<void> _getRating() async {
    final response = await http.get(
      Uri.parse('http://192.168.100.9:8000/api/user-rating/${data_detail!.id_resep}/$userId'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    );
    final responseData = jsonDecode(response.body);
    log(response.body);

    if (response.statusCode == 200) {
      setState(() {
        if (responseData["rating"] != null) {
          _currentRating = Rating(
            responseData["rating"]['id_rating'],
            responseData["rating"]['id_resep'],
            responseData["rating"]['bintang'],
            responseData["rating"]['id_user'],
            responseData["rating"]['username'],
            responseData["rating"]['komentar'],
          );
          _isSubmitting = true;
          showFeedbackField = false;
        }
      });
      log("NemoWorks");
    }
  }

  Future<void> _submitRating() async {
    // if (selectedRating == null) return;
    try {
      final token = AppData().token;

      final response = await http.post(
        Uri.parse('http://192.168.100.9:8000/api/submit-rating'),
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
        body: jsonEncode({
          'id_resep': data_detail?.id_resep,
          'bintang': selectedRating,
          'id_user': userId,
          'komentar': _reviewController.text,
        }),
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(responseData['message'])));
        setState(() {
          _getRating();
          _isSubmitting = true;
          showFeedbackField = false;
        });
      } else {
        throw Exception(responseData['message'] ?? 'Failed to submit rating');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${e.toString()}')));
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  Future<void> _deleteRating() async {
    final delete = await Userservice.deleteUserRating(AppData().id_user, data_detail!.id_resep);
    if (delete == true) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Resep berhasil dihapus')));
      setState(() {
        _isSubmitting = false;
        showFeedbackField = true;
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Gagal menghapus')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.redAccent,
        title: Text("Detail Resep", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : SafeArea(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      Image.network(
                        "http://192.168.100.9:8000/storage/${data_detail!.gambar}",
                        height: 350,
                        width: MediaQuery.of(context).size.width * 1,
                        fit: BoxFit.cover,
                      ),
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Column(
                                  mainAxisAlignment: MainAxisAlignment.start,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    SizedBox(
                                      width: 275,
                                      child: Text(
                                        data_detail!.judul,
                                        maxLines: 5,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 24),
                                      ),
                                    ),
                                    InkWell(
                                      onTap: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (context) => ProfilePage(id_user: data_detail!.id_user),
                                          ),
                                        );
                                      },
                                      child: Text(
                                        'Oleh ${data_detail!.username}',
                                        style: TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ],
                                ),
                                userId == data_detail!.id_user
                                    ? Row(
                                      children: [
                                        EditButton(data_detail: data_detail!),
                                        SizedBox(width: 5),
                                        DeleteButton(id_resep: data_detail!.id_resep),
                                      ],
                                    )
                                    : SaveButton(id_resep: data_detail!.id_resep),
                              ],
                            ),
                            SizedBox(height: 10),
                            Text(
                              "${data_detail!.ktg_masak}",
                              style: TextStyle(color: Colors.brown[800], fontWeight: FontWeight.w600),
                            ),
                            Text("${data_detail!.wkt_masak} Menit, untuk ${data_detail!.prs_resep} Porsi"),
                            SizedBox(height: 10),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                // Star Rating
                                Row(
                                  children: List.generate(5, (index) {
                                    final rating = double.tryParse(data_detail!.bintang) ?? 0.0;
                                    final filledStars = rating.floor(); // Round down to nearest integer
                                    final hasHalfStar = (rating - filledStars) >= 0.5;

                                    if (index < filledStars) {
                                      return const Icon(Icons.star, color: Colors.amber, size: 30);
                                    } else if (index == filledStars && hasHalfStar) {
                                      return const Icon(Icons.star_half, color: Colors.amber, size: 30);
                                    } else {
                                      return const Icon(Icons.star_border, color: Colors.amber, size: 30);
                                    }
                                  }),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '${data_detail!.bintang} / 5',
                                  style: TextStyle(fontSize: 25, fontWeight: FontWeight.w700),
                                ),
                              ],
                            ),
                            SizedBox(height: 20),
                            Text(data_detail!.deskripsi, style: TextStyle(fontSize: 16)),
                            SizedBox(height: 10),
                            Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.grey.withOpacity(0.2),
                                    spreadRadius: 1,
                                    blurRadius: 2,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: ExpansionTile(
                                title: const Text(
                                  "BAHAN",
                                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18),
                                ),
                                children: List.generate(data_detail!.bahan_resep.length, (index) {
                                  final bahan = data_detail!.bahan_resep[index];
                                  return ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: Colors.amber,
                                      child: Text((index + 1).toString()),
                                    ),
                                    title: Expanded(
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(bahan.nama_bahan),
                                          Text("${bahan.jumlah_bahan} ${bahan.satuan_bahan}"),
                                        ],
                                      ),
                                    ),
                                  );
                                }),
                              ),
                            ),
                            SizedBox(height: 10),
                            Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.grey.withOpacity(0.2),
                                    spreadRadius: 1,
                                    blurRadius: 2,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: ExpansionTile(
                                title: const Text(
                                  "ALAT",
                                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18),
                                ),
                                children: List.generate(data_detail!.alat_resep.length, (index) {
                                  final alat = data_detail!.alat_resep[index];
                                  return ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: Colors.amber,
                                      child: Text((index + 1).toString()),
                                    ),
                                    title: Text(alat.nama_alat),
                                  );
                                }),
                              ),
                            ),
                            SizedBox(height: 10),
                            Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.grey.withOpacity(0.2),
                                    spreadRadius: 1,
                                    blurRadius: 2,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: ExpansionTile(
                                title: const Text(
                                  "LANGKAH PEMBUATAN",
                                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18),
                                ),
                                children:
                                    data_detail?.langkah_resep
                                        .map(
                                          (langkah) => ListTile(
                                            leading: CircleAvatar(
                                              backgroundColor: Colors.amber,
                                              child: Text(langkah.urutan.toString()),
                                            ),
                                            title: Text(langkah.cara_langkah),
                                          ),
                                        )
                                        .toList() ??
                                    [const ListTile(title: Text('Tidak ada Tahap'))],
                              ),
                            ),
                            SizedBox(height: 20),
                            Container(
                              margin: EdgeInsets.symmetric(vertical: 15),
                              width: double.infinity,
                              child: ElevatedButton(
                                style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
                                onPressed: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => RatingPage(id_resep: data_detail!.id_resep),
                                    ),
                                  );
                                },
                                child: Text(
                                  "Review Pengguna",
                                  style: TextStyle(
                                    fontWeight: FontWeight.w500,
                                    fontSize: 18,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ),
                            SizedBox(height: 10),
                            Text("Reviewmu : ", style: TextStyle(fontWeight: FontWeight.w600)),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Row(
                                  children: List.generate(5, (index) {
                                    return _isSubmitting
                                        ? Icon(
                                          index < _currentRating!.bintang ? Icons.star : Icons.star_border,
                                          color: Colors.amber,
                                          size: 32,
                                        )
                                        : GestureDetector(
                                          onTap: () {
                                            setState(() {
                                              selectedRating = index + 1;
                                              showFeedbackField = true;
                                            });
                                          },
                                          child: Icon(
                                            (selectedRating != null && index < selectedRating!)
                                                ? Icons.star
                                                : Icons.star_border,
                                            color: Colors.amber,
                                            size: 32,
                                          ),
                                        );
                                  }),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _isSubmitting
                                      ? "${_currentRating!.bintang} / 5"
                                      : selectedRating != null
                                      ? "$selectedRating / 5"
                                      : "0 / 5",
                                ),
                              ],
                            ),

                            if (!_isSubmitting && showFeedbackField) ...[
                              const SizedBox(height: 16),
                              const Text("Bagikan Pengalamanmu"),
                              const SizedBox(height: 8),
                              TextField(
                                controller: _reviewController,
                                minLines: 5,
                                keyboardType: TextInputType.multiline,
                                maxLines: null,
                                decoration: const InputDecoration(
                                  labelText: "Tulis Pengalaman disini",
                                  border: OutlineInputBorder(),
                                ),
                              ),
                              const SizedBox(height: 16),
                              SizedBox(
                                width: double.infinity,
                                child: TextButton(
                                  onPressed: _isSubmitting ? null : _submitRating,
                                  style: TextButton.styleFrom(
                                    backgroundColor: Colors.redAccent,
                                    padding: const EdgeInsets.symmetric(vertical: 16),
                                  ),
                                  child:
                                      _isSubmitting
                                          ? const CircularProgressIndicator(color: Colors.white)
                                          : const Text(
                                            "Submit Review",
                                            style: TextStyle(color: Colors.white),
                                          ),
                                ),
                              ),
                            ],
                            if (_currentRating != null) ...[
                              const SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  if (_currentRating!.komentar.isNotEmpty) ...[
                                    Center(
                                      child: Text(
                                        _currentRating!.komentar,
                                        style: TextStyle(fontStyle: FontStyle.italic),
                                      ),
                                    ),
                                  ],
                                  IconButton(
                                    style: IconButton.styleFrom(
                                      iconSize: 30,
                                      backgroundColor: Colors.redAccent,
                                      foregroundColor: Colors.white,
                                    ),
                                    onPressed: () {
                                      showDialog(
                                        context: context,
                                        builder:
                                            (context) => AlertDialog(
                                              title: Text("Hapus Resep"),
                                              content: Text("Apakah Anda yakin ingin menghapus rating anda?"),
                                              actions: [
                                                TextButton(
                                                  onPressed: () => Navigator.pop(context),
                                                  child: Text("Batal"),
                                                ),
                                                TextButton(
                                                  onPressed: () {
                                                    _deleteRating();
                                                    Navigator.pop(context);
                                                  },
                                                  child: Text("Hapus", style: TextStyle(color: Colors.red)),
                                                ),
                                              ],
                                            ),
                                      );
                                    },
                                    icon: Icon(Icons.delete_sweep_rounded),
                                  ),
                                ],
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
    );
  }
}
