import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Rating.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/UserService.dart';

class RatingPage extends StatefulWidget {
  const RatingPage({super.key, required this.id_resep});
  final id_resep;

  @override
  State<RatingPage> createState() => _RatingPageState();
}

class _RatingPageState extends State<RatingPage> {
  List<Rating>? rating_data;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() async {
    final rating = await Userservice.showResepRating(widget.id_resep);
    if (rating != null) {
      setState(() {
        rating_data = rating;
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Rating Resep", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
        backgroundColor: Colors.redAccent,
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : Padding(
                padding: const EdgeInsets.all(10.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: ListView.builder(
                        scrollDirection: Axis.vertical,
                        itemCount: rating_data!.length,
                        itemBuilder: (context, index) {
                          return CardItem_Rating(data: rating_data![index]);
                        },
                      ),
                    ),
                  ],
                ),
              ),
    );
  }
}
