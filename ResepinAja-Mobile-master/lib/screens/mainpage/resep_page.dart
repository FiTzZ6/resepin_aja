import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/RecipeService.dart';

class RecipePage extends StatefulWidget {
  const RecipePage({super.key});

  @override
  State<RecipePage> createState() => _RecipePageState();
}

enum TanggalResep { terbaru, terlama }

class _RecipePageState extends State<RecipePage> {
  List<Item>? reseptersimpan;
  final _searchController = TextEditingController();
  final _usernameController = TextEditingController();

  TanggalResep? urutTanggal = TanggalResep.terbaru;
  List<String> kategori_list = ["Makanan Ringan", "Makanan Berat", "Minuman", "Snack", "Dessert"];
  List<String> kategori = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final params = {
      'cari_resep': _searchController.text,
      'user_resep': _usernameController.text,
      'ktg_masak[]': kategori.isNotEmpty ? kategori : null,
      'tgl_masak': urutTanggal == TanggalResep.terbaru ? 'desc' : 'asc',
    };
    params.removeWhere((key, value) => value == null || value == '');
    final tersimpan = await Recipeservice.showResepCari(params);
    if (mounted) {
      setState(() {
        reseptersimpan = tersimpan;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.redAccent,
          toolbarHeight: 90,
          title: Padding(
            padding: const EdgeInsets.all(10),
            child: SizedBox(
              width: MediaQuery.of(context).size.width - 20,
              child: SearchBar(
                controller: _searchController,
                leading: const Icon(Icons.search),
                hintText: "Cari Resep",
                // Value tidak dipakai
                onSubmitted: (value) {
                  _loadData();
                },
              ),
            ),
          ),
        ),
        body:
            reseptersimpan == null
                ? const Center(child: CircularProgressIndicator())
                : Padding(
                  padding: const EdgeInsets.all(10.0),
                  // TextButton.icon(
                      //   onPressed: () {
                      //     Scaffold.of(context).openDrawer();
                      //   },
                      //   icon: const Icon(Icons.filter_list),
                      //   label: const Text('Filter Spesifik'),
                      //   iconAlignment: IconAlignment.start,
                      // ),
                  child: Expanded(
                    child: ListView.builder(
                      itemCount: reseptersimpan?.length ?? 0,
                      itemBuilder: (context, index) {
                        return CardItem_Hori(data: reseptersimpan![index]);
                      },
                    ),
                  ),
                ),
        drawer: Drawer(
          child: Padding(
            padding: const EdgeInsets.all(15.0),
            child: Expanded(
              child: ListView(
                shrinkWrap: true,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Nama Resep", style: TextStyle(fontWeight: FontWeight.w600)),
                      TextField(
                        controller: _searchController,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Es Jeger...',
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Nama User", style: TextStyle(fontWeight: FontWeight.w600)),
                      TextField(
                        controller: _usernameController,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Bintang Wonton...',
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Kategori Resep", style: TextStyle(fontWeight: FontWeight.w600)),
                      Column(
                        children: List.generate(kategori_list.length, (index) {
                          final category = kategori_list[index];
                          return CheckboxListTile(
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Text(category),
                            value: kategori.contains(category),
                            onChanged: (bool? value) {  
                              setState(() {
                                if (value == true) {
                                  kategori.add(category);
                                } else {
                                  kategori.remove(category);
                                }
                              });
                            },
                          );
                        }),
                      ),
                    ],
                  ),
                  SizedBox(height: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Urutan Resep", style: TextStyle(fontWeight: FontWeight.w600)),
                      RadioListTile<TanggalResep>(
                        title: const Text('Terbaru'),
                        value: TanggalResep.terbaru,
                        groupValue: urutTanggal,
                        onChanged: (TanggalResep? value) {
                          setState(() {
                            urutTanggal = value;
                          });
                        },
                      ),
                      RadioListTile<TanggalResep>(
                        title: const Text('Terlama'),
                        value: TanggalResep.terlama,
                        groupValue: urutTanggal,
                        onChanged: (TanggalResep? value) {
                          setState(() {
                            urutTanggal = value;
                          });
                        },
                      ),
                    ],
                  ),
                  SizedBox(height: 10),
                  TextButton(
                    onPressed: () {
                      _loadData();
                      Navigator.pop(context);
                    },
                    style: TextButton.styleFrom(backgroundColor: Colors.amber),
                    child: Text("Lanjut"),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
