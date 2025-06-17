import 'package:flutter/material.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/models/Detail.dart';
import 'package:resepinajamobile/screens/mainpage/edit_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:developer';

class SaveButton extends StatefulWidget {
  const SaveButton({super.key, required this.id_resep});
  final int id_resep;

  @override
  State<SaveButton> createState() => _SaveButtonState();
}

class _SaveButtonState extends State<SaveButton> {
  bool _isSaved = false;
  bool _isLoading = false;
  final token = '';

  @override
  void initState() {
    super.initState();
    _checkSavedStatus();
  }

  Future<void> _checkSavedStatus() async {
    final token = AppData().token;
    final id_user = AppData().id_user;
    if (id_user == null) return;
    setState(() => _isLoading = true);
    try {
      final response = await http.get(
        Uri.parse('http://192.168.100.9:8000/api/check-saved/$id_user/${widget.id_resep}'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() => _isSaved = data['is_saved'] ?? false);
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleSave() async {
    if (_isLoading) return;
    final token = AppData().token;
    final id_user = AppData().id_user;
    if (id_user == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please login first')));
      return;
    }
    setState(() => _isLoading = true);
    try {
      final endpoint = _isSaved ? 'unsave-recipe' : 'save-recipe';
      final response = await http.post(
        Uri.parse('http://192.168.100.9:8000/api/$endpoint'),
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
        body: jsonEncode({'id_user': id_user, 'id_resep': widget.id_resep}),
      );
      if (response.statusCode == 200) {
        setState(() => _isSaved = !_isSaved);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(_isSaved ? 'Recipe saved' : 'Recipe unsaved')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${e.toString()}')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      style: IconButton.styleFrom(iconSize: 30),
      icon:
          _isLoading
              ? const CircularProgressIndicator()
              : Icon(_isSaved ? Icons.bookmark_added : Icons.bookmark_add_outlined),
      onPressed: _toggleSave,
    );
  }
}

class EditButton extends StatefulWidget {
  const EditButton({super.key, required this.data_detail});
  final Detail data_detail;

  @override
  State<EditButton> createState() => _EditButtonState();
}

class _EditButtonState extends State<EditButton> {
  @override
  Widget build(BuildContext context) {
    return IconButton(
      style: IconButton.styleFrom(iconSize: 30, backgroundColor: Colors.amber),
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder:
                (context) => EditRecipePage(
                  recipe: widget.data_detail,
                  onRecipeUpdated: () {
                    if (mounted) {}
                  },
                ),
          ),
        );
      },
      icon: Icon(Icons.edit_note_rounded),
    );
  }
}

class DeleteButton extends StatelessWidget {
  final int id_resep;
  final VoidCallback? onDeleted;

  const DeleteButton({super.key, required this.id_resep, this.onDeleted});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      style: IconButton.styleFrom(iconSize: 30, backgroundColor: Colors.redAccent),
      icon: Icon(Icons.delete_forever_rounded),
      onPressed: () => _confirmDelete(context),
    );
  }

  void _confirmDelete(BuildContext context) {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text("Hapus Resep"),
            content: Text("Apakah Anda yakin ingin menghapus resep ini?"),
            actions: [
              TextButton(onPressed: () => Navigator.pop(context), child: Text("Batal")),
              TextButton(
                onPressed: () {
                  _deleteRecipe(context);
                  // Navigator.pop(context);
                },
                child: Text("Hapus", style: TextStyle(color: Colors.red)),
              ),
            ],
          ),
    );
  }

  Future<void> _deleteRecipe(BuildContext context) async {
    final token = AppData().token;

    final response = await http.delete(
      Uri.parse('http://192.168.100.9:8000/api/deleteresep'),
      headers: {'Accept': 'application/json', 'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({
        'id_resep': id_resep
        }),
    );

    final responseData = jsonDecode(response.body);

    if (response.statusCode == 200) {
      // ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Resep berhasil dihapus')));
      Navigator.pop(context);
      Navigator.of(context,rootNavigator: true).pop();
      if (onDeleted != null) onDeleted!();
    } else {
      log(responseData['message']);
      // ScaffoldMessenger.of(
      //   context,
      // ).showSnackBar(SnackBar(content: Text('Gagal menghapus: ${responseData['message']}')));
    }
  }
}
