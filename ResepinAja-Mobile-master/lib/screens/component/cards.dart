import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/models/Rating.dart';
import 'package:resepinajamobile/screens/component/buttons.dart';
import 'package:resepinajamobile/screens/mainpage/detail_page.dart';
import 'package:resepinajamobile/screens/mainpage/user_page.dart';

class CardItem_Hori extends StatefulWidget {
  const CardItem_Hori({super.key, required this.data});
  final Item data;

  @override
  State<CardItem_Hori> createState() => _CardItem_HoriState();
}

class _CardItem_HoriState extends State<CardItem_Hori> {
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 10),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => DetailPage(id_resep: widget.data.id_resep)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                children: [
                  Container(
                    margin: EdgeInsets.fromLTRB(0, 0, 10, 0),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(10),

                      child: Image.network(
                        "http://192.168.100.9:8000/storage/${widget.data.gambar}",
                        width: 90,
                        height: 90,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(
                        width: 195,
                        child: Text(
                          widget.data.judul,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 17.5),
                        ),
                      ),
                      Text(
                        "${widget.data.jumlah_bahan} Bahan | ${widget.data.wkt_masak} Menit \n${widget.data.prs_resep} Porsi",
                      ),
                    ],
                  ),
                ],
              ),
              Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  SaveButton(id_resep: widget.data.id_resep),
                  SizedBox(height: 20),
                  Wrap(children: [Icon(Icons.star), Text(widget.data.bintang.toString())]),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CardItem_Cube extends StatefulWidget {
  const CardItem_Cube({super.key, required this.data});
  final Item data;

  @override
  State<CardItem_Cube> createState() => _CardItem_CubeState();
}

class _CardItem_CubeState extends State<CardItem_Cube> {
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 10),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => DetailPage(id_resep: widget.data.id_resep)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(
                  "http://192.168.100.9:8000/storage/${widget.data.gambar}",
                  width: 150,
                  height: 150,
                  fit: BoxFit.cover,
                ),
              ),
              SizedBox(
                width: 145, // same as the image width
                child: Text(
                  widget.data.judul,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 18),
                ),
              ),
              Wrap(
                children: [
                  Icon(Icons.star),
                  Text(widget.data.bintang.toString(), style: TextStyle(fontSize: 18)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class CardItem_Rating extends StatefulWidget {
  const CardItem_Rating({super.key, required this.data});
  final Rating data;
  @override
  State<CardItem_Rating> createState() => _CardItem_RatingState();
}

class _CardItem_RatingState extends State<CardItem_Rating> {
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 10),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                InkWell(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => ProfilePage(id_user: widget.data.id_user)),
                    );
                  },
                  child: Wrap(
                    children: [
                      Padding(
                        padding: const EdgeInsets.fromLTRB(0, 0, 20, 10),
                        child: CircleAvatar(
                          radius: 20,
                          backgroundImage: AssetImage('assets/profile_placeholder.webp'),
                        ),
                      ),
                      Text(widget.data.username, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
                    ],
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Row(
                      children: List.generate(5, (index) {
                        final rating = double.tryParse(widget.data.bintang.toString()) ?? 0.0;
                        final filledStars = rating.floor(); // Round down to nearest integer
                        final hasHalfStar = (rating - filledStars) >= 0.5;

                        if (index < filledStars) {
                          return const Icon(Icons.star, color: Colors.amber);
                        } else if (index == filledStars && hasHalfStar) {
                          return const Icon(Icons.star_half, color: Colors.amber);
                        } else {
                          return const Icon(Icons.star_border, color: Colors.amber);
                        }
                      }),
                    ),
                    Text("${widget.data.bintang} / 5"),
                  ],
                ),
              ],
            ),
            Text(widget.data.komentar),
          ],
        ),
      ),
    );
  }
}
