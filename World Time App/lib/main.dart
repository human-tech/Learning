import 'package:flutter/material.dart';
import 'package:Learn/pages/home.dart';
import 'package:Learn/pages/choose_location.dart';
import 'package:Learn/pages/loading.dart';

void main() => runApp(MaterialApp(
      initialRoute: '/',
      routes: {
        '/': (context) => Loading(),
        '/home': (context) => Home(),
        '/location': (context) => ChooseLocation()
      },
    ));
