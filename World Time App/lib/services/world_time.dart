import 'package:http/http.dart';
import 'dart:convert';
import 'package:intl/intl.dart';

class WorldTime {
  String location;
  String time;
  String flag;
  String url;
  bool isDayTime;

  WorldTime({this.location, this.flag, this.url});

  Future<void> getTime() async {
    try {
      Response response =
          await get('http://worldtimeapi.org/api/timezone/$url');
      Map data = jsonDecode(response.body);

      String dateTime = data['datetime'].substring(0, 25);
      DateTime now = DateTime.parse(dateTime);

      isDayTime = now.hour > 6 && now.hour < 19;
      time = DateFormat.jm().format(now);
    } catch (e) {
      print("Error: $e");
      time = "And then everything went to hell";
    }
  }
}
