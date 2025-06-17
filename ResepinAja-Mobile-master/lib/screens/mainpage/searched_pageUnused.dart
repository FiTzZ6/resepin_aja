import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/RecipeService.dart';

class ResultPage extends StatefulWidget {
  const ResultPage({super.key, required this.kunci});
  final kunci;

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> {
  List<Item>? reseptersimpan;
  List<Item>? filteredResep; // For search results

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {

    final tersimpan = await Recipeservice.showResepCari(widget.kunci);
    if (mounted) {
      setState(() {
        reseptersimpan = tersimpan;
        filteredResep = tersimpan; // Initialize filtered list
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
        title: Text("Hasil '"+widget.kunci+"'", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
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
