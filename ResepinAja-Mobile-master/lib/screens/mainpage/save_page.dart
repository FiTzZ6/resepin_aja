import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/RecipeService.dart';
import 'dart:developer';

class SavedPage extends StatefulWidget {
  const SavedPage({super.key});

  @override
  State<SavedPage> createState() => _SavedPageState();
}

class _SavedPageState extends State<SavedPage> {
  List<Item>? reseptersimpan;
  List<Item>? filteredResep; // For search results
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
    _searchController.addListener(_filterResep); // Add search listener
  }

  Future<void> _loadData() async {
    // final id_user = null;
    final id_user = AppData().id_user;
    log(id_user.toString() + " Stein");

    final tersimpan = await Recipeservice.showResepTersimpan(id_user!);
    if (tersimpan != null) {
      setState(() {
        log("NEMOOOO");
        reseptersimpan = tersimpan;
        filteredResep = tersimpan; // Initialize filtered list
      });
    } else {
      log("SINANJU");
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
          automaticallyImplyLeading: false,
          backgroundColor: Colors.redAccent,
          toolbarHeight: 90,
          title: Padding(
            padding: const EdgeInsets.all(10),
            child: SizedBox(
              width: MediaQuery.of(context).size.width - 20,
              child: SearchBar(
                controller: _searchController,
                leading: const Icon(Icons.search),
                hintText: "Cari Resep Tersimpan",
                onChanged: (_) {}, // Listener already handles this
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
