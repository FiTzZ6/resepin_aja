import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/Item.dart';
import 'package:resepinajamobile/models/UserData.dart';
import 'package:resepinajamobile/screens/component/cards.dart';
import 'package:resepinajamobile/services/RecipeService.dart';
import 'package:resepinajamobile/services/UserService.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'dart:developer';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key, required this.id_user});
  final id_user;

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  Userdata? data;
  List<Item>? reseptersimpan;

  @override
  void initState() {
    super.initState();
    _loadData();
    log(AppData().id_user.toString());
    log(AppData().token.toString());
  }

  void _loadData() async {
    final user = await Userservice.showProfile(widget.id_user);
    final tersimpan = await Recipeservice.showResepSendiri(widget.id_user);
    if (user != null) {
      setState(() {
        reseptersimpan = tersimpan;
        data = user;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Profil Pengguna", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
        backgroundColor: Colors.redAccent,
      ),
      body:
          data == null
              ? Center(child: CircularProgressIndicator())
              : SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          CircleAvatar(
                            radius: 60,
                            backgroundImage: AssetImage('assets/profile_placeholder.webp'),
                          ),
                          SizedBox(height: 10),
                          Center(
                            child: Text(
                              data!.username,
                              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 24),
                            ),
                          ),
                          SizedBox(height: 10),
                          Center(child: Text(data!.deskripsi_user, style: TextStyle(fontSize: 18))),
                        ],
                      ),
                      SizedBox(height: 10),
                      reseptersimpan == null
                          ? const Center(child: CircularProgressIndicator())
                          : Padding(
                            padding: const EdgeInsets.all(10.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                ListView.builder(
                                  shrinkWrap: true,
                                  itemCount: reseptersimpan?.length ?? 0,
                                  itemBuilder: (context, index) {
                                    return CardItem_Hori(data: reseptersimpan![index]);
                                  },
                                ),
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
