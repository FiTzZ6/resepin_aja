import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:resepinajamobile/models/AppData.dart';
import 'package:resepinajamobile/models/Detail.dart';
import 'dart:developer';
import 'dart:io';

class EditRecipePage extends StatefulWidget {
  const EditRecipePage({super.key, required this.recipe, this.onRecipeUpdated});
  final Detail recipe;
  final VoidCallback? onRecipeUpdated;

  @override
  State<EditRecipePage> createState() => _EditRecipePageState();
}

class _EditRecipePageState extends State<EditRecipePage> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _judulController;
  late final TextEditingController _deskripsiController;
  File? _gambar;
  late TextEditingController _waktuController = TextEditingController();
  late TextEditingController _porsiController = TextEditingController();
  late String? kategori;
  late List<TextEditingController> _jumlahControllers;
  late List<String?> satuan_bahan;
  late List<TextEditingController> _bahanControllers;
  late List<TextEditingController> _alatControllers;
  late List<TextEditingController> _langkahControllers;
  String? _currentImageUrl;

  @override
  void initState() {
    super.initState();
    _judulController = TextEditingController(text: widget.recipe.judul);
    _deskripsiController = TextEditingController(text: widget.recipe.deskripsi);
    _waktuController = TextEditingController(text: widget.recipe.wkt_masak.toString());
    _porsiController = TextEditingController(text: widget.recipe.prs_resep.toString());
    kategori = widget.recipe.ktg_masak;
    _currentImageUrl = "http://192.168.100.9:8000/storage/${widget.recipe.gambar}";

    _bahanControllers =
        widget.recipe.bahan_resep.map((bahan) => TextEditingController(text: bahan.nama_bahan)).toList();
    if (_bahanControllers.isEmpty) _bahanControllers.add(TextEditingController());

    _jumlahControllers =
        widget.recipe.bahan_resep
            .map((bahan) => TextEditingController(text: bahan.jumlah_bahan.toString()))
            .toList();
    if (_jumlahControllers.isEmpty) _jumlahControllers.add(TextEditingController());

    satuan_bahan = widget.recipe.bahan_resep.map((bahan) => bahan.satuan_bahan).toList();
    if (satuan_bahan.isEmpty) satuan_bahan.add("Buah");

    _alatControllers =
        widget.recipe.alat_resep.map((alat) => TextEditingController(text: alat.nama_alat)).toList();
    if (_alatControllers.isEmpty) _alatControllers.add(TextEditingController());

    _langkahControllers =
        widget.recipe.langkah_resep
            .map((langkah) => TextEditingController(text: langkah.cara_langkah))
            .toList();
    if (_langkahControllers.isEmpty) _langkahControllers.add(TextEditingController());
  }

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _gambar = File(pickedFile.path);
        _currentImageUrl = null;
      });
    }
  }

  void _addIngredientField() {
    setState(() {
      _bahanControllers.add(TextEditingController());
      _jumlahControllers.add(TextEditingController());
      satuan_bahan.add("Buah"); // Default value
    });
  }

  void _removeIngredientField(int index) {
    setState(() {
      _bahanControllers[index].dispose();
      _jumlahControllers[index].dispose();
      _bahanControllers.removeAt(index);
      _jumlahControllers.removeAt(index);
      satuan_bahan.removeAt(index);
    });
  }

  void _addField(List<TextEditingController> list) {
    setState(() {
      list.add(TextEditingController());
    });
  }

  void _removeField(List<TextEditingController> list, int index) {
    if (list.length > 1) {
      setState(() {
        list.removeAt(index);
      });
    }
  }

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate()) {
      try {
        final token = AppData().token;
        var request = http.MultipartRequest('POST', Uri.parse('http://192.168.100.9:8000/api/updateresep/'));
        request.headers['Accept'] = 'application/json';
        request.headers['Authorization'] = 'Bearer $token';

        // Add text fields
        request.fields['id_resep'] = widget.recipe.id_resep.toString();
        request.fields['judul'] = _judulController.text;
        request.fields['deskripsi'] = _deskripsiController.text;
        request.fields['_method'] = 'PUT';
        request.fields['wkt_masak'] = _waktuController.text;
        request.fields['prs_resep'] = _porsiController.text;
        request.fields['ktg_masak'] = kategori!;
        request.fields['jumlah'] = jsonEncode(_jumlahControllers.map((c) => c.text).toList());
        request.fields['satuan'] = jsonEncode(satuan_bahan.toList());
        request.fields['bahan'] = jsonEncode(_bahanControllers.map((c) => c.text).toList());
        request.fields['alat'] = jsonEncode(_alatControllers.map((c) => c.text).toList());
        request.fields['langkah'] = jsonEncode(_langkahControllers.map((c) => c.text).toList());

        // Only add image if a new one was selected
        if (_gambar != null) {
          request.files.add(
            await http.MultipartFile.fromPath('gambar', _gambar!.path, contentType: MediaType('image', '*')),
          );
        }

        var response = await request.send();

        if (response.statusCode == 200) {
          if (widget.onRecipeUpdated != null) widget.onRecipeUpdated!();
          Navigator.pop(context); // Close the edit page
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Resep berhasil diperbarui!')));
        } else {
          var responseString = await response.stream.bytesToString();
          var jsonResponse = jsonDecode(responseString);
          log(jsonResponse.toString());
          throw Exception('Failed to update recipe');
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${e.toString()}')));
      }
    }
  }

  @override
  void dispose() {
    _judulController.dispose();
    _deskripsiController.dispose();
    for (var c in _bahanControllers) {
      c.dispose();
    }
    for (var c in _alatControllers) {
      c.dispose();
    }
    for (var c in _langkahControllers) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.redAccent,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("Edit Resep", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
            ElevatedButton(
              onPressed: _submitForm,
              style: ElevatedButton.styleFrom(backgroundColor: const Color.fromARGB(255, 226, 226, 226)),
              child: Text("Simpan"),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Judul
              TextFormField(
                controller: _judulController,
                decoration: const InputDecoration(labelText: 'Judul Resep', border: OutlineInputBorder()),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Harap masukkan judul resep';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 15),

              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Gambar Resep', style: TextStyle(fontSize: 16)),
                  const SizedBox(height: 8),
                  GestureDetector(
                    onTap: _pickImage,
                    child: Container(
                      height: 150,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child:
                          _gambar != null
                              ? Image.file(_gambar!, fit: BoxFit.cover)
                              : _currentImageUrl != null
                              ? Image.network(_currentImageUrl!, fit: BoxFit.cover)
                              : const Center(child: Icon(Icons.add_a_photo, size: 50)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 15),

              // Deskripsi
              TextFormField(
                controller: _deskripsiController,
                maxLines: 3,
                decoration: const InputDecoration(labelText: 'Deskripsi', border: OutlineInputBorder()),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Harap masukkan deskripsi';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 15),

              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Waktu Masak', style: const TextStyle(fontWeight: FontWeight.bold)),
                        Padding(
                          padding: const EdgeInsets.fromLTRB(0, 0, 10, 0),
                          child: TextFormField(
                            controller: _waktuController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              hintText: '5 Menit',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Harap masukkan Waktu Masak';
                              }
                              return null;
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Porsi Resep', style: const TextStyle(fontWeight: FontWeight.bold)),
                        Padding(
                          padding: const EdgeInsets.fromLTRB(0, 0, 10, 0),
                          child: TextFormField(
                            controller: _porsiController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              hintText: '10 Orang',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Harap masukkan Porsi resep';
                              }
                              return null;
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 15),
              Text('Kategori Resep', style: const TextStyle(fontWeight: FontWeight.bold)),
              DropdownButton(
                isExpanded: true,
                value: kategori,
                items: [
                  DropdownMenuItem<String>(value: "Makanan Ringan", child: Text("Makanan Ringan")),
                  DropdownMenuItem<String>(value: "Makanan Berat", child: Text("Makanan Berat")),
                  DropdownMenuItem<String>(value: "Minuman", child: Text("Minuman")),
                  DropdownMenuItem<String>(value: "Snack", child: Text("Snack")),
                  DropdownMenuItem<String>(value: "Dessert", child: Text("Dessert")),
                ],
                onChanged: (String? value) {
                  setState(() {
                    kategori = value!;
                  });
                },
              ),
              const SizedBox(height: 15),

              _CustomDynamicFields(),
              const SizedBox(height: 15),

              // Alat
              _buildDynamicFields(
                title: 'Alat-alat',
                controllers: _alatControllers,
                hintText: 'Masukkan alat',
              ),
              const SizedBox(height: 15),

              // Langkah Pembuatan
              _buildDynamicFields(
                title: 'Langkah Pembuatan',
                controllers: _langkahControllers,
                hintText: 'Masukkan langkah',
                isNumbered: true,
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDynamicFields({
    required String title,
    required List<TextEditingController> controllers,
    required String hintText,
    bool isNumbered = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: controllers.length,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                children: [
                  if (isNumbered)
                    Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: Text('${index + 1}.', style: const TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  Expanded(
                    child: TextFormField(
                      maxLines: null,
                      controller: controllers[index],
                      decoration: InputDecoration(
                        hintText: hintText,
                        border: const OutlineInputBorder(),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.remove),
                          onPressed: () => _removeField(controllers, index),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Harap isi field ini';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: () => _addField(controllers),
            icon: const Icon(Icons.add),
            label: const Text('Tambah'),
          ),
        ),
      ],
    );
  }

  Widget _CustomDynamicFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Bahan Bahan Resep", style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _bahanControllers.length,
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                children: [
                  Expanded(
                    child: Row(
                      children: [
                        // Ingredient Name
                        Flexible(
                          flex: 3,
                          child: TextFormField(
                            controller: _bahanControllers[index],
                            decoration: InputDecoration(
                              hintText: "Garam Madu",
                              border: const OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Harap isi nama bahan';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(width: 8),

                        // Quantity
                        Flexible(
                          flex: 1,
                          child: TextFormField(
                            controller: _jumlahControllers[index],
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(hintText: "500", border: const OutlineInputBorder()),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Harap isi jumlah';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(width: 8),

                        // Unit Dropdown
                        Flexible(
                          flex: 1,
                          child: DropdownButtonFormField<String>(
                            isExpanded: true,
                            value: satuan_bahan[index],
                            items: const [
                              DropdownMenuItem(value: "Buah", child: Text("Buah")),
                              DropdownMenuItem(value: "gr", child: Text("Gram")),
                              DropdownMenuItem(value: "ml", child: Text("Mililiter")),
                            ],
                            onChanged: (String? value) {
                              setState(() {
                                satuan_bahan[index] = value;
                              });
                            },
                          ),
                        ),
                        const SizedBox(width: 8),

                        // Remove Button
                        IconButton(
                          icon: const Icon(Icons.remove),
                          style: IconButton.styleFrom(backgroundColor: Colors.redAccent),
                          onPressed: () => _removeIngredientField(index),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: _addIngredientField,
            icon: const Icon(Icons.add),
            label: const Text('Tambah Bahan'),
          ),
        ),
      ],
    );
  }
}
