import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:developer';
import 'dart:io';

import 'package:resepinajamobile/models/AppData.dart';

class AddRecipePage extends StatefulWidget {
  final VoidCallback? onRecipeAdded;
  const AddRecipePage({super.key, this.onRecipeAdded});

  @override
  State<AddRecipePage> createState() => _AddRecipePageState();
}

class _AddRecipePageState extends State<AddRecipePage> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _judulController = TextEditingController();
  final TextEditingController _deskripsiController = TextEditingController();
  File? _gambar;
  final TextEditingController _waktuController = TextEditingController();
  final TextEditingController _porsiController = TextEditingController();
  String? kategori = "Makanan Ringan";
  List<TextEditingController> _jumlahControllers = [TextEditingController()];
  List<String?> satuan_bahan = ["Buah"];
  List<TextEditingController> _bahanControllers = [TextEditingController()];
  List<TextEditingController> _alatControllers = [TextEditingController()];
  List<TextEditingController> _langkahControllers = [TextEditingController()];

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _gambar = File(pickedFile.path);
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

  void removeFormValue() {
    setState(() {
      _judulController.clear();
      _deskripsiController.clear();
      _gambar = null;
      for (var controller in _bahanControllers) {
        controller.clear();
      }
      for (var controller in _alatControllers) {
        controller.clear();
      }
      for (var controller in _langkahControllers) {
        controller.clear();
      }
      _bahanControllers = [TextEditingController()];
      _alatControllers = [TextEditingController()];
      _langkahControllers = [TextEditingController()];
    });
  }

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate() && _gambar != null) {
      try {
        final token = AppData().token;
        var request = http.MultipartRequest('POST', Uri.parse('http://192.168.100.9:8000/api/addresep'));
        request.headers['Accept'] = 'application/json';
        request.headers['Authorization'] = 'Bearer $token';

        // Add text fields
        request.fields['judul'] = _judulController.text;
        request.fields['deskripsi'] = _deskripsiController.text;
        request.fields['wkt_masak'] = _waktuController.text;
        request.fields['prs_resep'] = _porsiController.text;
        request.fields['ktg_masak'] = kategori!;
        request.fields['id_user'] = AppData().id_user.toString();
        request.fields['bahan'] = jsonEncode(_bahanControllers.map((c) => c.text).toList());
        request.fields['jumlah'] = jsonEncode(_jumlahControllers.map((c) => c.text).toList());
        request.fields['satuan'] = jsonEncode(satuan_bahan.toList());
        request.fields['alat'] = jsonEncode(_alatControllers.map((c) => c.text).toList());
        request.fields['langkah'] = jsonEncode(_langkahControllers.map((c) => c.text).toList());

        if (_gambar != null) {
          request.files.add(
            await http.MultipartFile.fromPath('gambar', _gambar!.path, contentType: MediaType('image', '*')),
          );
        }

        var response = await request.send();

        if (response.statusCode == 200) {
          if (widget.onRecipeAdded != null) widget.onRecipeAdded!();
          removeFormValue();
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Resep berhasil disimpan!')));
        } else {
          var responseString = await response.stream.bytesToString();
          var jsonResponse = jsonDecode(responseString);
          log(jsonResponse.toString());
          throw Exception(Error);
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${e.toString()}')));
      }
    }
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
            Text("Tambah Resepmu", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.white)),
            ElevatedButton(
              onPressed: () {
                _submitForm();
              },
              style: ElevatedButton.styleFrom(backgroundColor: const Color.fromARGB(255, 226, 226, 226)),
              child: Text("Post"),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(15.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Judul
              Text('Judul Resep', style: const TextStyle(fontWeight: FontWeight.bold)),
              TextFormField(
                controller: _judulController,
                decoration: const InputDecoration(hintText: 'Judul Resep', border: OutlineInputBorder()),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Harap masukkan judul resep';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 15),

              // Gambar
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Judul Resep', style: const TextStyle(fontWeight: FontWeight.bold)),
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
                          _gambar == null
                              ? const Center(child: Icon(Icons.add_a_photo, size: 50))
                              : Image.file(_gambar!, fit: BoxFit.cover),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 15),

              // deskripsi
              Text('Deskripsi Resep', style: const TextStyle(fontWeight: FontWeight.bold)),
              TextFormField(
                controller: _deskripsiController,
                maxLines: 3,
                decoration: const InputDecoration(hintText: 'deskripsi', border: OutlineInputBorder()),
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
              const SizedBox(height: 20),

              // Bahan
              _CustomDynamicFields(),
              const SizedBox(height: 15),

              // Alat
              _buildDynamicFields(
                title: 'Alat-alat',
                controllers: _alatControllers,
                hintText: 'Masukkan alat',
                isNumbered: true,
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
        Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
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
          itemCount: _bahanControllers.length, // Use the actual controller list
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                children: [
                  // if (true) // You had isNumbered which was always true
                  //   Padding(
                  //     padding: const EdgeInsets.only(right: 8.0),
                  //     child: Text('${index + 1}.', style: const TextStyle(fontWeight: FontWeight.bold)),
                  //   ),
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
