import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/RecipeService.dart';

class ResepSendiri extends StatefulWidget {
  const ResepSendiri({super.key, required this.id_user});
  final id_user;

  @override
  State<ResepSendiri> createState() => _ResepSendiriState();
}

class _ResepSendiriState extends State<ResepSendiri> {
  List<Item>? reseptersimpan;
  List<Item>? filteredResep; // For search results
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _searchController.addListener(_filterResep); // Add search listener
    _loadData();
  }

  Future<void> _loadData() async {
    final tersimpan = await Recipeservice.showResepSendiri(widget.id_user);
    if (mounted) {
      setState(() {
        reseptersimpan = tersimpan;
        filteredResep = tersimpan; // Initialize filtered list
      });
    }
  }

  void _filterResep() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      filteredResep =
          reseptersimpan?.where((resep) {
            return resep.judul.toLowerCase().contains(query);
          }).toList();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
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
                onChanged: (_) {},
              ),
            ),
          ),
        ),
        body:
            reseptersimpan == null
                ? const Center(child: CircularProgressIndicator())
                : Padding(
                  padding: const EdgeInsets.all(10.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: ListView.builder(
                          itemCount: filteredResep?.length ?? 0,
                          itemBuilder: (context, index) {
                            return CardItem_Hori(data: filteredResep![index]);
                          },
                        ),
                      ),
                    ],
                  ),
                ),
      ),
    );
  }
}
